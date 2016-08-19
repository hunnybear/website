
# ONLY BUILTIN IMPORTS HERE.
import os
import os.path
import sys

sys.path.append(os.getcwd())

BRANCH_BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INTERP = os.path.abspath(BRANCH_BASE_DIR + '/../main_venv/bin/python3')

# If we're using the wrong executable (we probably are on first run,
# unless i've fixed that bug (no way I'm ever getting to that)).
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# imports not needed for checking the environment should all be done after
import app
import app.log

app.log.add_file_handler_to_root()

# importing views registers the views in the module
import app.views

application = app.application
