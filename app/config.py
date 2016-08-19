# settings for the deployment
import os.path

LOG_FILENAME = 'server_logs.log'

BRAND_IMG = "me_2_{size}_square.png"

# BASIC CONFIG
ABOUT_ME_LENGTH = 140
URL_NAME_LENGTH = 64
MAX_NICKNAME_LENGTH = 64
MAX_SLUG_LENGTH = 128
MAX_POST_LENGTH = 1024
MAX_POST_TITLE_LENGTH = 128
SEARCH_WORKING = False

POSTS_PER_PAGE = 5

DEFAULT_NAME = 'Happy Mutant'
DEFAULT_AVATAR_SIZE = 64
SITE_NAME = 'Tyler Jachetta'

SHOW_GITHUB = False
SHOW_LINKEDIN = True
LINKEDIN_URL = r'https://www.linkedin.com/in/tyler-jachetta-4526a713'
SHOW_FACEBOOK = False

TEMPLATE_DIR_NAME = 'templates'

BASE_APP_DIR = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = os.path.split(BASE_APP_DIR)[0]
TEMPLATE_DIR = os.path.join(BASE_APP_DIR, TEMPLATE_DIR_NAME)

# FLASK config values
DEBUG = True
SECRET_KEY = '7E89F498D8C22'
WTF_CSRF_ENABLED = True

# Database stuff

# Main database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(BASE_DIR, 'db_repository')

# Search database
WHOOSH_BASE = os.path.join(BASE_DIR, 'search.db')

# Open auth stuff

OAUTH_CREDENTIALS = {
    'google': {
        'id': '238505662740-muou8aqt46ans77e05v0ukoqsv016d7b.apps.googleusercontent.com',
        'secret': 'xOTwrvPwgcLPFiM-3Qb2KK7B'
    }

}

# Mail server settings

# mail server settings
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USERNAME = None
MAIL_PASSWORD = None

# administrator list
ADMINS = ['you@example.com']

ALLOWED_USERS = ['me@tylerjachetta.net']
