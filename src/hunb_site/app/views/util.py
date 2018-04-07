import flask

import app.models


def render_template( source, **context):
    """
    Making a specialized render_template function that defaults some context in.
    This should be used any time we're rendering a template, so that defaults
    are always used.

    *Arguments:*

        :``source``:    `str` the name of the template to render

    """

    post_types = [ ]

    for post_type in app.models.Post_Type.get_ordered():
        if post_type.posts:
            post_types.append((post_type.type_url_name, post_type.type_name))

    return flask.render_template(source, post_types=post_types, **context)
