import datetime

import flask
import flask_login

import app

import app.forms
import app.models

import app.views.util


def _show_compose(post=None):

    form = app.forms.PostForm()

    # Set the post type choices
    post_types = app.models.Post_Type.get_ordered()
    form.post_type.choices = [(post_type.id, post_type.type_name) for post_type in post_types]

    if form.validate_on_submit():

        post_type = app.models.Post_Type.get_by_type_id(form.post_type.data)

        if post is None:
            post = app.models.Post(
                title=form.title.data,
                body=form.post.data,
                slug=form.slug.data,
                timestamp=datetime.datetime.utcnow(),
                author=flask.g.user,
                post_type=post_type
            )

        else:
            post.title = form.title.data
            post.slug = form.slug.data
            post.body = form.post.data

            post.post_type = post_type

        app.db.session.add(post)
        app.db.session.commit()

        flask.flash('Post Submitted!')
        # TODO maybe if submitted as draft redirect to edit
        return flask.redirect(flask.url_for(post.post_type.type_url_name))

    if post is not None:
        form.title.data = post.title
        form.post.data = post.body
        form.slug.data = post.slug
        form.post_type = post.post_type.id

    return app.views.util.render_template(
        'compose.html',
        title='Compose post',
        form=form
    )


@app.application.route('/compose', methods=['GET', 'POST'])
@flask_login.login_required
def compose():
    return _show_compose()


@app.application.route('/edit/<slug>', methods=['GET', 'POST'])
@flask_login.login_required
def edit(slug):
    post = app.models.Post.get_by_slug(slug)
    if post is None:
        return _show_compose(), 404
    else:
        return _show_compose(post)
