# stock imports
import datetime

# 3rd party imports
import flask
import flask_login

# blaaawwwg imports
import app
import app.auth
import app.flash_messages
import app.forms
import app.models


@app.application.before_request
def before_request():
    flask.g.user = flask_login.current_user
    if flask.g.user.is_authenticated:
        flask.g.user.last_seen = datetime.datetime.utcnow()
        app.db.session.commit()


@app.application.route('/authorize/<provider>')
def authorize(provider):
    if not flask_login.current_user.is_anonymous:
        return flask.redirect(flask.url_for('index'))
    oauth = app.auth.OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.application.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('index'))


@app.application.route('/login')
def login():
    """
    I'm only using google authentication, so this is just a
    convenience URL for me
    """

    return authorize('google')


@app.application.route('/callback/<provider>')
def callback(provider):
    commit_session = False
    app.application.logger.debug("auth callback for provider {0}".format(provider))

    if not flask_login.current_user.is_anonymous:
        return flask.redirect(flask.url_for('index'))

    oauth = app.auth.OAuthSignIn.get_provider(provider)
    social_id, name, email, picture = oauth.callback()

    if email is None:
        # I need a valid email address
        flask.flash(app.flash_messages.AUTH_FAILED)
        return flask.redirect(flask.url_for('index'))

    user = app.models.User.query.filter_by(email=email).first()
    if not user:
        user = app.models.User(social_id=social_id, name=name, email=email)
        app.db.session.add(user)
        commit_session = True

    else:
        if user.name != name:
            user.name = name
            commit_session = True

        if user.avatar_path != picture:
            user.avatar_path = picture
            commit_session = True

    if commit_session:
        app.db.session.commit()

    flask_login.login_user(user, True)
    return flask.redirect(flask.url_for('index'))
