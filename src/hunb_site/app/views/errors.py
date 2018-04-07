import app

import app.views.util


@app.application.errorhandler(404)
def not_found_error(error):
    return app.views.util.render_template('404.html'), 404


@app.application.errorhandler(500)
def internal_error(error):
    app.db.session.rollback()
    return app.views.util.render_template('500.html'), 500
