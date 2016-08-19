import datetime

import flask
import flask_login

import app

import app.forms
import app.models


def _show_compose(post=None, post_class=app.models.Post):

    form = app.forms.PostForm()
    if form.validate_on_submit():
        if post is None:
            post = post_class(
                title=form.title.data,
                body=form.post.data,
                slug=form.slug.data,
                timestamp=datetime.datetime.utcnow(),
                author=flask.g.user
            )

        else:
            post.title = form.title.data
            post.slug = form.slug.data
            post.body = form.post.data

        app.db.session.add(post)
        app.db.session.commit()

        flask.flash('Post Submitted!')
        # TODO maybe if submitted as draft redirect
        # to edit
        return flask.redirect(flask.url_for(post.get_index_name()))

    if post is not None:
        form.title.data = post.title
        form.post.data = post.body
        form.slug.data = post.slug

    return flask.render_template(
        'compose.html',
        title='Compose post',
        form=form
    )

@app.application.route('/blog/compose', methods=['GET', 'POST'])
@flask_login.login_required
def compose():
    return _show_compose()


@app.application.route('/blog/edit/<slug>', methods=['GET', 'POST'])
@flask_login.login_required
def edit(slug):
    post = app.models.Post.get_by_slug(slug)
    if post is None:
        return _show_compose(), 404
    else:
        return _show_compose(post)


@app.application.route('/projects/compose', methods=['GET', 'POST'])
@flask_login.login_required
def compose_project():
    return _show_compose(post_class=app.models.Project)

@app.application.route('/projects/edit/<slug>', methods=['GET', 'POST'])
@flask_login.login_required
def edit_project(slug):
    project = app.models.Project.get_by_slug(slug)
    if project is None:
        return _show_compose(post_class=app.models.Project), 404
    else:
        return _show_compose(project)



    
