import flask
import flask_login

import app
import app.forms
import app.models

import app.views.util

from app import config


@app.application.route('/user/<user_url_id>/<int:page>')
@app.application.route('/user/<user_url_id>')
def user(user_url_id, page=1):
    user = app.models.User.query_for_url(user_url_id)
    return _show_user(user, page=page)


def _show_user(user, page=1):
    if user is None:
        flask.flash('User not found')
        return flask.redirect(flask.url_for('index'))

    posts = user.posts.paginate(page, config.POSTS_PER_PAGE, False)

    return app.views.util.render_template(
        'user.html',
        user=user,
        posts=posts
    )


@app.application.route('/me/<int:page>')
@app.application.route('/me')
def me(page=1):
    user = flask.g.user

    return _show_user(user, page=page)


@app.application.route('/edit', methods=['GET', 'POST'])
@flask_login.login_required
def edit_user():
    form = app.forms.EditForm()
    if form.validate_on_submit():
        url_name = form.url_subpath.data or None

        flask.g.user.nickname = form.nickname.data
        flask.g.user.url_name = url_name

        app.db.session.add(flask.g.user)
        app.db.session.commit()

        flask.flash('Your changes have been saved')
        return flask.redirect(flask.url_for('edit_user'))

    else:
        form.nickname.data = flask.g.user.nickname
        form.about_me.data = flask.g.user.about_me
        form.url_subpath.data = flask.g.user.url_name

    return app.views.util.render_template('user_edit.html', form=form)
