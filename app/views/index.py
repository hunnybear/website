"""
views.py
"""

# 3rd party imports
import flask

# local imports
import app
import app.models

from app import config

APPLICATION = app.application


@APPLICATION.route('/')
@APPLICATION.route('/index')
def index():
    return flask.render_template(
        'index.html',
        title='Hunnybear Jamboree',
        is_splash=True,
    )
