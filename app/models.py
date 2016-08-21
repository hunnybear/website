"""
Database models
"""

# Builtin
import re

# 3rd-party
import flask
import flask_login

import markdown
from markdown.extensions import codehilite
from markdown.extensions import extra

import micawber

import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm

import app
from app import config


DB = app.db
LM = flask_login.LoginManager(app.application)

Base = sqlalchemy.ext.declarative.declarative_base()

SIZE_SUFFIX = '?sz={0}'


class User(flask_login.UserMixin, DB.Model):
    """
    A little heavyhanded for the current implementation, but might come in
    handy if I decide to go with the dream and start blogging.

    *Properties:*

      :``id``:          `int` database primary key
      :``url_name``:    `str` url to the user page
      :``social_id``:   `str` ID for google auth
      :``avatar_path``: `str` path to the user's avatar
      :``name``:        `str` user real name
      :``nickname``:    `str` user nickname
      :``email``:       `str` user email
      :``last_seen``:   `datetime.datetime` last time user logged in
      :``posts``:       `collection<Post>` collection of Posts by the user
      :``projects``:    `collection<Project>` collection of Projects by the user

    """
    id = DB.Column(DB.Integer, primary_key=True)

    url_name = DB.Column(
        DB.String(config.URL_NAME_LENGTH),
        nullable=True,
        unique=True
    )

    social_id = DB.Column(DB.String(64), nullable=False, unique=True)
    avatar_path = DB.Column(DB.String(128))
    name = DB.Column(DB.String(64), nullable=True, index=True)

    nickname = DB.Column(
        DB.String(config.MAX_NICKNAME_LENGTH),
        nullable=True,
        index=True
    )

    email = DB.Column(DB.String(120), index=True, unique=True)
    last_seen = DB.Column(DB.DateTime)

    posts = DB.relationship('Post', backref='author', lazy='dynamic')

    @classmethod
    def query_for_url(cls, url_name):
        """
        Look for a user with either the given int ID or the given url name,
        depending on whether url_name is a digit (as a string) or not

        *Arguments:*

            :``url_name``:  `str` a string giving a url identifier for a user

        *Returns:*
            :``user``:      `User` an instance of this class, or None if there is no user by that name
        """

        if url_name.isdigit():
            return cls.query.filter_by(id=int(url_name)).first()
        else:
            return cls.query.filter_by(url_name=url_name).first()

    def __repr__(self):
        """repr function for the user."""

        return '<User {0}>'.format(self.name)

    def get_display_name(self):
        """Get the name to be used to display the user"""
        return self.nickname or self.name or config.DEFAULT_NAME

    def get_url_name(self):
        """get the url name to be used for the user's about page"""
        if self.url_name:
            return self.url_name

        return str(self.id)

    def get_avatar(self, size=None):
        """
        Get the avatar for this user.  This is not currently used, but I need
        to get it working before the blog is 100% ready to go.

        *Arguments:*

            None

        *Keyword Arguments:*

            :``size``:  `int`   if specified, get the size of the avatar image.
                                if not specified, get it at the default size
                                (specified in the config.py file)

        """
        avatar_path = None

        if self.avatar_path:
            avatar_path = self.avatar_path

        # TODO replace with default image
        if avatar_path is None:
            return None

        if size is None:
            size = config.DEFAULT_AVATAR_SIZE

        avatar_path += SIZE_SUFFIX.format(size)
        return avatar_path

    @sqlalchemy.orm.validates('url_name')
    def validate_url_name(self, key, url_name):
        """
        Validator function for the url_name field
        """
        if url_name is None:
            return url_name  # nullable
        if ' ' in url_name or '/t' in url_name or '/n' in url_name:
            raise ValueError('url names cannot have whitespace')
        if url_name.isdigit():
            raise ValueError('url names cannot be integers')

        return url_name


class Post_Type(DB.Model):
    """
    Instead of having seperate classes for projects and posts, just make a table
    for post types, and then I can slim down my tables and classes, keep things
    cleaner.

    *Properties:*

        :``type_id``:           `int`   Primary key
        :``type_name``:         `str`   Pretty name of the post type
        :``type_url_name``:     `str`   URL-safe name for the type
        :``display_priority``:  `int`   priority/order for displaying this post
                                        type in UI. Low = first. Note that
                                        having multipe post types with the same
                                        priority could lead to bugs, so I've
                                        made this unique
        :``posts``:             `relationship<Post>` all posts of this type
    """

    type_id = DB.Column(DB.Integer, primary_key=True)
    type_name = DB.Column(DB.String(config.MAX_TYPE_NAME_LENGTH), unique=True)
    type_url_name = DB.Column(DB.String(config.MAX_TYPE_NAME_LENGTH), unique=True)
    display_priority = DB.Column(DB.Integer, unique=True)

    posts = DB.relationship('Post', backref='post_type', lazy='dynamic')

    # We can add observers here when
    _observers = set()

    @classmethod
    def add_observer(cls, observer):
        """
        add an observer function, which will be notified any time a post type
        is saved.
        """

        cls._observers.add(observer)

    def save(self, *args, **kwargs):
        """
        Extend DB.Model's save so that observer functions can be notified of
        added or modified post types
        """

        res = super().save(*args, **kwargs)

        # Notify all observers that a post type has been added or modified
        for observer in self._observers:
            observer(self)

        return res

    @classmethod
    def get_ordered(cls):
        """
        Return all class types ordered in the order that they should appear in
        UIs.
        """

        return cls.query.all().order_by(cls.display_priority)

    @classmethod
    def get_by_type_id(cls, type_id):

        return cls.query.filter(cls.type_id == type_id).first()


class Post(DB.Model):
    """
    Class for a post in a blog or any sort of other bloggy-type thing (projects
    area of the site eventually, etc.)

    *Properties:*

        :``id``:        `int`   primary key
        :``title``:     `str`   the title of the post
        :``slug``:      `str`   the URL slug for the post
        :``body``:      `str`   the body text of the post, with markdown
                                formatting.
        :``published``: `bool`  Set to True to publish
    """

    _POST_URL_BASE = '/{type_url_name}/{slug}'
    _EDIT_URL_BASE = '/{type_url_name}/edit/{slug}'

    __searchable__ = ['body', 'title']

    id = DB.Column(DB.Integer, primary_key=True)
    title = DB.Column(DB.String(config.MAX_POST_TITLE_LENGTH))
    slug = DB.Column(DB.String(config.MAX_SLUG_LENGTH), unique=True)
    body = DB.Column(DB.Text())
    published = DB.Column(DB.Boolean(), index=True)
    timestamp = DB.Column(DB.DateTime)

    @sqlalchemy.ext.declarative.declared_attr
    def user_id(cls):
        return DB.Column(DB.Integer, DB.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {0}>'.format(self.title)

    def save(self, *args, **kwargs):
        """
        Save the post, and ensure that there is a slug. Extend's DB.Model's
        save method.
        """
        if not self.slug:
            self.slug = re.sub('[^\w]+', '-', self.title.lower())

        ret = super(Post, self).save(*args, **kwargs)

        return ret

    @classmethod
    def public(cls, post_type=None):
        """
        Return a query object that only queries published posts
        """

        if post_type is None:
            return cls.query().filter(cls.published == True)

        else:
            return cls.query().filter(
                sqlalchemy.and_(
                    cls.post_type == post_type,
                    cls.published == True
                )
            )

    @classmethod
    def get_by_slug(cls, slug, published_only=False):
        if published_only:
            post = cls.query.filter(
                sqlalchemy.and_(
                    app.models.Post.slug == slug,
                    app.models.Post.published == True
                )
            )
        else:
            post = cls.query.filter(app.models.Post.slug == slug).one_or_none()
        return post

    def get_url(self, for_edit=False):
        """
        Return the url to the post's detail view, or for the edit view
        if for_edit is True
        """

        type_url_name = self.post_type.type_url_name

        if for_edit:
            url = self._EDIT_URL_BASE.format(
                type_url_name=type_url_name,
                post_slug=self.slug
            )
        else:
            url = self._POST_URL_BASE.format(
                type_url_name=type_url_name,
                slug=self.slug
            )

        return url


    def get_preview(self):
        # TODO
        return self.body

    def get_html_content(self):
        """
        Return the body of the post with markdown converted to HTML
        """

        hilite = codehilite.CodeHiliteExtension(
            linenums=False,
            css_class='highlight'
        )
        extras = extra.ExtraExtension()
        markdown_content = markdown.markdown(
            self.body,
            extensions=[hilite, extras]
        )
        oembed_content = micawber.parse_html(
            markdown_content,
            app.oembed_providers,
            urlize_all=True,
            # TODO maxwidth
            # maxwidth=app.config['SITE_WIDTH']
        )
        return flask.Markup(oembed_content)


@LM.user_loader
def load_user(id):
    return User.query.get(int(id))

