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

    if show_blog is None:
        show_blog = bool(app.models.Post.query.all())
    print("Show blog:{0}".format(show_blog))

    if show_projects is None:
        show_projects = bool(app.models.Project.query.all())

    return flask.render_template(
        source,
        show_blog=show_blog,
        show_projects=show_projects,
        **context
    )
