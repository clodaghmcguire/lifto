from flask import Flask
import os
from datetime import datetime, timezone
import jwt
from . import routes
from .db import tokens

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config["DEBUG"] = True
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.config['JSON_SORT_KEYS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', "Th1s1sAS3cr3t")
    app.register_blueprint(routes.bp)
    authorised_systems = ['vasa', 'sqvd']
    for system in authorised_systems:
        payload = {"iat": datetime.now(tz=timezone.utc).timestamp(), "sub": system}  # keep datetime in this format or jwt.decode() errors
        system_jwt = jwt.encode(payload, app.config['SECRET_KEY'], algorithm="HS256")
        system_token = {
            "system": system,
            "token": system_jwt
        }
        tokens.insert_one(system_token)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app
