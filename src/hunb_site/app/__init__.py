
import inspect
import logging

import flask
import flask_sqlalchemy

import micawber

import app.log
import app.moment
import app.jinja_util
from app import config

_application = None


def set_application(application, force=False):
    global _application

    if _application is not None and not force:
        raise ValueError("app.application is already set!")

    _application = application


def get_application():
    if application is None:
        raise app.errors.SetupError("The application is not yet properly set up.")
    assert isinstance(application, flask.Flask)
    return application


application.config.from_object('app.config')

db = flask_sqlalchemy.SQLAlchemy(application)
_micawber_cache = micawber.cache.Cache()
oembed_providers = micawber.bootstrap_basic(_micawber_cache)

# Setup jinja function calls
application.jinja_env.globals['momentjs'] = app.moment.moment

# use tha abstract syntax tree to add all pubilc jijja util functions to jinja
for member_name, member in inspect.getmembers(app.jinja_util):
    if member_name.startswith('_'):
        continue
    if inspect.isfunction(member):
        application.jinja_env.globals[member_name] = member

application.logger.setLevel(logging.INFO)
app.log.setup_application_handler(application)
application.logger.info('microblog startup')

# importing views and models register them in the module. This stuff has to be
# imported after the application is initialized, which is why it's down here.
from app.views import *
import app.models
