
import logging
import logging.handlers

from app import config

_FORMAT_STRING = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'

# instantiate the file handler
FILE_HANDLER = logging.handlers.RotatingFileHandler(
    config.BASE_DIR + '/tmp/' + config.LOG_FILENAME,
    'a',
    1 * 1024 * 1024, 10
)

# Set the file handler formatter
FILE_HANDLER.setFormatter(logging.Formatter(_FORMAT_STRING))


def add_file_handler_to_root():
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(FILE_HANDLER)
