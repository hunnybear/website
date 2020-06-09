import app
from app import config

def setup_db(application):

    db = flask_sqlalchemy.SQLAlchemy(application)
    return db


def setup_app():
    application = flask.Flask(config.SITE_NAME, template_folder=config.TEMPLATE_DIR)

    application.config.from_object('app.config')

    db = setup_db(application)

    # use tha abstract syntax tree to add all pubilc jijja util functions to jinja
    for member_name, member in inspect.getmembers(app.jinja_util):
        if member_name.startswith('_'):
            continue
        if inspect.isfunction(member):
            application.jinja_env.globals[member_name] = member

    application.logger.setLevel(logging.INFO)
    app.log.setup_application_handler(application)
    application.logger.info('microblog startup')
