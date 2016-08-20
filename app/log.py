
import logging
import logging.handlers

from app import config

_FORMAT_STRING = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'

# instantiate the file handler
try:
    FILE_HANDLER = logging.handlers.RotatingFileHandler(
        config.BASE_DIR + '/tmp/' + config.LOG_FILENAME,
        'a',
        1 * 1024 * 1024, 10
    )
except FileNotFoundError:
    # The file wasn't found, could mean our environment isn't set up
    # properly, or we're in a dev environment/testing environment
    FILE_HANDLER = None

else:
    # Set the file handler formatter
    FILE_HANDLER.setFormatter(logging.Formatter(_FORMAT_STRING))


def setup_application_handler(application):
    if FILE_HANDLER is None:
        return False
    application.logger.addHandler(FILE_HANDLER)
    return True


def add_file_handler_to_root():
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    if FILE_HANDLER is not None:
        logger.addHandler(FILE_HANDLER)
