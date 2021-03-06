#!bin/python3
import imp
from migrate.versioning import api
import app
from app import config

v = api.db_version(
    config.SQLALCHEMY_DATABASE_URI, config.SQLALCHEMY_MIGRATE_REPO
)

migration = config.SQLALCHEMY_MIGRATE_REPO + ('/versions/%03d_migration.py' % (v+1))
tmp_module = imp.new_module('old_model')

old_model = api.create_model(
    config.SQLALCHEMY_DATABASE_URI,
    config.SQLALCHEMY_MIGRATE_REPO
)

exec(old_model, tmp_module.__dict__)

script = api.make_update_script_for_model(
    config.SQLALCHEMY_DATABASE_URI,
    config.SQLALCHEMY_MIGRATE_REPO, tmp_module.meta, app.db.metadata
)

open(migration, "wt").write(script)
api.upgrade( config.SQLALCHEMY_DATABASE_URI, config.SQLALCHEMY_MIGRATE_REPO)
v = api.db_version( config.SQLALCHEMY_DATABASE_URI, config.SQLALCHEMY_MIGRATE_REPO)
print('New migration saved as ' + migration)
print('Current database version: ' + str(v))
