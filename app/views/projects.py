"""
projects.py

view for displaying past and current projects. Similar-ish to blog, but more portfolio-y
"""

# 3rd party imports
import flask

# local imports
import app
import app.models

from app import config

APPLICATION = app.application


@APPLICATION.route('/projects')
@APPLICATION.route('/projects/<int:page>' )
def projects(page=1):
    """
    view for the projects page
    """

    user = flask.g.user
    posts = app.models.Project.query.paginate(page, config.POSTS_PER_PAGE, False)

    return flask.render_template(
        'projects.html',
        title='Hunnybear Jamboree',
        user=user,
        posts=posts
    )

@APPLICATION.route('/projects/<slug>')
def detail_project(slug):
    """
    View for viewing an individual project page.
    """
    published_only = not flask.g.user.is_authenticated

    post = app.models.Project.get_by_slug(slug, published_only=published_only)
    if post is None:
        return render_template('post_detail.html', post=post), 404
    else:
        return render_template('post_detail.html', post=post)