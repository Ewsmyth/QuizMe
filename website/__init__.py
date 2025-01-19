import time
from sqlalchemy.exc import OperationalError
from flask import Flask
from flask_login import LoginManager
from . import config
from .models import db, User
from .utils import create_admin_user, create_roles

def create_app():
    app = Flask(__name__)

    # Load configuration settings from config.py
    app.config['SECRET_KEY'] = config.SECRET_KEY

    # Load configuration for database
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)

    # Setup Flask-Login manager
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.auth_login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    # Import and register blueprints
    from .auth import auth
    from .user import user
    from .admin import admin

    app.register_blueprint(auth)
    app.register_blueprint(user)
    app.register_blueprint(admin)

    max_retries = 5
    for attempt in range(max_retries):
        try:
            with app.app_context():
                # Initialize database tables
                db.create_all()
                print("Database tables initialized successfully.")
                # Ensure roles are created
                create_roles()
                # Create admin user
                create_admin_user()
            break
        except OperationalError as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print("Max retries reached. Raising exception.")
                raise e

    return app