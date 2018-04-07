"""
views.py
"""

# local imports
import app
import app.models
import app.views.util

APPLICATION = app.application


@APPLICATION.route('/')
@APPLICATION.route('/index')
def index():
    return app.views.util.render_template(
        'index.html',
        title='Hunnybear Jamboree',
        is_splash=True,
    )
