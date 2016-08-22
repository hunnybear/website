"""
blog.py

Module containing view for reading the blog
"""

# 3rd party imports
import flask
import sqlalchemy.exc

# local imports
import app
import app.models

import app.views.util

APPLICATION = app.application


def _make_posts_function(post_type):

    # horay closures.
    def posts_function(page=1):

        user = flask.g.user
        # TODO maybe move this from a const to the post type.
        posts = post_type.get_posts_paginated(page=page)

        return app.views.util.render_template(
            'blog.html',
            title="Hunnybear Jamboree",
            user=user,
            posts=posts
        )

    return posts_function


def _make_slug_function(post_type):
    def slug_function(slug):
        published_only = not flask.g.user.is_authenticated

        post = post_type.get_by_slug(slug, published_only=published_only)
        if post is None:
            return app.views.util.render_template('post_detail.html', post=post), 404
        else:
            return app.views.util.render_template('post_detail.html', post=post)

    return slug_function


def _create_post_type_url_rules(post_type):
    main_rule = '/{0}'
    paginated_rule = main_rule + '/<int:page>'
    slug_rule = main_rule + '/<slug>'

    endpoint = post_type.type_url_name

    posts_function = _make_posts_function(post_type)

    APPLICATION.add_url_rule(main_rule, endpoint, posts_function)
    # TODO not sure if I need to provide the post function again, I should
    # investigate this.
    APPLICATION.add_url_rule(paginated_rule, endpoint, posts_function)

    slug_endpoint = 'slug_{0}'.format(endpoint)

    slug_function = _make_slug_function(post_type)

    APPLICATION.add_url_rule(slug_rule, slug_endpoint, slug_function)

# Register views for all post types. Might want to move this into a function,
# but for now I'm sticking with the convention I'm using with other views of
# 'views get registered on module import'

try:
    _post_types = app.models.Post_Type.query.all()
except sqlalchemy.exc.OperationalError:
    # when we're first creating the DB, this table doens't exist, that's fine
    # (only in the case that we're starting the app to create the DB)
    # should probably put some better catching here to make sure this doesn't
    # happen after db creation
    _post_types = []
for post_type in _post_types:
    _create_post_type_url_rules(post_type)

app.models.Post_Type.add_observer(_create_post_type_url_rules)
