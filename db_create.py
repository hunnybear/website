#!/usr/bin/env python3
from migrate.versioning import api
import app.config
import app
import os.path

app.db.create_all()
if not os.path.exists( app.config.SQLALCHEMY_MIGRATE_REPO ):
    api.create( app.config.SQLALCHEMY_MIGRATE_REPO, 'database repository' )
    api.version_control( app.config.SQLALCHEMY_DATABASE_URI, app.config.SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control( app.config.SQLALCHEMY_DATABASE_URI, app.config.SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))
