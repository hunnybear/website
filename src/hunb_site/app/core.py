import flask
import flask_sqlalchemy

from app import config

CONFIG_OBJECT_NAME = 'app.config'

class HunnybearSiteApplication(flask.Flask):
    def __init__(self):
        super(HunnybearSiteApplication, self).__init__()
