from flask import Flask, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, logout_user, current_user
from app.models import EnvUser
from flask_wtf import CSRFProtect
import os
from dotenv import load_dotenv
from datetime import timedelta, datetime
from app.routes import auth, main

# Load the .env file
load_dotenv()


db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()  # just instantiate here, don't init yet


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdb.sqlite3'

    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_EXTENSIONS'] = ['.pdf', '.xls', '.xlsx']
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)  # init CSRF with app here

    # Import and register blueprints
    app.register_blueprint(main)
    app.register_blueprint(auth)

    # Where to redirect for @login_required
    login_manager.login_view = 'main.login'

    @login_manager.user_loader
    def load_user(user_id):
        if user_id == "1":
            return EnvUser(email=os.getenv("EMAIL"))
        return None

    @app.before_request
    def manage_session_timeout():
        if current_user.is_authenticated:
            now = datetime.utcnow()
            last_active = session.get('last_active')

            if last_active:
                elapsed = now - datetime.fromisoformat(last_active)
                if elapsed > timedelta(minutes=30):
                    logout_user()
                    flash("Your session has expired due to inactivity.", "warning")
                    return redirect(url_for('main.login'))

            session['last_active'] = now.isoformat()
        else:
            session.pop('last_active', None)

    return app

