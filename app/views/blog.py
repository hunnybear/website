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


def _create_post_type_url_rules(post_type):
    main_rule = '/{0}'
    paginated_rule = main_rule + '/<int:page>'
    slug_rule = main_rule + '/<slug>'

    endpoint = post_type.type_url_name

    # horay closures.
    def posts_function(page=1):

        user = flask.g.user
        # TODO maybe move this from a const to the post type.
        posts = post_type.posts.query.paginate(page, config.POSTS_PER_PAGE, False)

        return flask.render_template(
            'blog.html',
            title="Hunnybear Jamboree",
            user=user,
            posts=posts
        )

    APPLICATION.add_url_rule(main_rule, endpoint, posts_function)
    # TODO not sure if I need to provide the post function again, I should
    # investigate this.
    APPLICATION.add_url_rule(paginated_rule, endpoint, post_function)

    slug_endpoint = 'slug_{0}'.format( endpoint )

    def slug_function(slug):
        published_only = not flask.g.user.is_authenticated

        post = post_type.get_by_slug(slug, published_only=published_only)
        if post is None:
            return app.views.util.render_template('post_detail.html', post=post), 404
        else:
            return app.views.util.render_template('post_detail.html', post=post)

    APPLICATION.add_url_rule(slug_rule, slug_endpoint, slug_function)

# Register views for all post types.
for post_type in app.models.Post_Type.query.all():
    _create_post_type_url_rules(post_type)

app.models.Post_Type.add_observer(_create_post_type_url_rules)
