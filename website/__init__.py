from flask import Flask
from . import config

def create_app():
    app = Flask(__name__)

    # Load configuration settings from config.py
    app.config['SECRET_KEY'] = config.SECRET_KEY

    # Import and register blueprints
    from .auth import auth
    from .user import user
    from .admin import admin

    app.register_blueprint(auth)
    app.register_blueprint(user)
    app.register_blueprint(admin)

    return app