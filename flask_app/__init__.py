from flask import Flask
from .routes import bp

def create_app():

    app = Flask(__name__)
    app.register_blueprint(bp)
    app.secret_key = 'asiubdfgrretertedfgdfgaconbcyI'
    app.config["DEBUG"] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

    return app