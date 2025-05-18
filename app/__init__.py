from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.models import User
from flask_wtf import CSRFProtect
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()


db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()  # just instantiate here, don't init yet


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdb.sqlite3'

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)  # init CSRF with app here

    # Import and register blueprints
    from app.routes import main
    app.register_blueprint(main)

    # Where to redirect for @login_required
    login_manager.login_view = 'main.login'

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
