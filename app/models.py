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
      :``about_me``:    `str` user description, might phase this out
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
    about_me = DB.Column(DB.String(config.ABOUT_ME_LENGTH))
    last_seen = DB.Column(DB.DateTime)

    posts = DB.relationship('Post', backref='author', lazy='dynamic')
    projects = DB.relationship('Project', backref='author', lazy='dynamic')

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

class _Base_Post(object):
    """
    Abstract base object for posts, which includes blog posts and project posts.
    """

    _POST_URL_BASE = '/blog/{slug}'
    _EDIT_URL_BASE = '/blog/edit/{slug}'
    _INDEX_NAME = 'blog'

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
        return '<Post {0}>'.format(self.body)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = re.sub('[^\w]+', '-', self.title.lower())

        ret = super(Post, self).save(*args, **kwargs)

        return ret

    @classmethod
    def public(cls):
        """
        Return a query object that only queries published posts
        """

        return cls.query().filter(cls.published == True)

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

        if for_edit:
            url = self._EDIT_URL_BASE.format(slug=self.slug)
        else:
            url = self._POST_URL_BASE.format(slug=self.slug)

        return url

    @classmethod
    def get_index_name(cls):
        """
        Just expose the index name, probably not actually worth a function.
        consider pulling this out and just directly accessing the INDEX_NAME
        constant externally.
        """
        return cls._INDEX_NAME

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


class Post(_Base_Post, DB.Model):
    """
    Blog posts
    """


class Project(_Base_Post, DB.Model):
    """
    Subclass of post used for projects
    """
    _EDIT_URL_BASE = r'/projects/edit/{slug}'
    _POST_URL_BASE = r'/projects/{slug}'
    _INDEX_NAME = 'projects'


@LM.user_loader
def load_user(id):
    return User.query.get(int(id))

