from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


def load_json_config_from_envvar(envvar):
    import os
    import json

    app.config.path = os.environ[envvar]
    with open(app.config.path) as stream:
        app.config.update(json.load(stream))


app = Flask('inventario')
load_json_config_from_envvar('INV_CONFIG')
db = SQLAlchemy(app)


from . import models
