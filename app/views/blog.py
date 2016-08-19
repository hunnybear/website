"""
blog.py

Module containing view for reading the blog
"""

# 3rd party imports
import flask

# local imports
import app
import app.models

from app import config

import app.views.util

APPLICATION = app.application


@APPLICATION.route('/blog')
@APPLICATION.route('/blog/<int:page>')
def blog(page=1):
    user = flask.g.user
    posts = app.models.Post.query.paginate(page, config.POSTS_PER_PAGE, False)

    return flask.render_template(
        'blog.html',
        title='Hunnybear Jamboree',
        user=user,
        posts=posts
    )


@APPLICATION.route('/blog/<slug>')
def detail_blog(slug):
    published_only = not flask.g.user.is_authenticated

    post = app.models.Post.get_by_slug(slug, published_only=published_only)
    if post is None:
        return app.views.util.render_template('post_detail.html', post=post), 404
    else:
        return app.views.util.render_template('post_detail.html', post=post)
