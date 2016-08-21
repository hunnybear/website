import flask

import app.models


def render_template( source, show_blog=None, show_projects=None, **context):
    """
    making a specialized render_template function that defaults some context in

    *Arguments:*

        :``source``:    `str` the name of the template to render

    *Keyword Arguments:*

        :``show_blog``:     `bool`  Set this to True or False to force showing
                                    or not showing the blog in the navbar
        :``show_projects``: `bool`  Set this to True or False to force showing
                                    or not showing the projects link in the
                                    navbar.

    """

    post_types = [ ]

    for post_type in app.models.Post_Type.get_ordered():
        if post_type.posts:
            post_types.append(post_type.type_url_name, post_type.type_name)

    return flask.render_template(
        source,
        post_types=post_types,
        **context
    )
