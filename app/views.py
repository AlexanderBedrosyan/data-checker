from flask.views import MethodView
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.models import User

auth_blueprint = Blueprint('auth', __name__)


class LoginView(MethodView):
    def get(self):
        if current_user.is_authenticated:
            return redirect(url_for('main.home'))
        return render_template('index.html')

    def post(self):
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(username=username, email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            flash('Invalid login credentials.', 'danger')
            return render_template('index.html')


class HomeView(MethodView):
    decorators = [login_required]

    def get(self):
        current_app.logger.info("Home route hit")
        return render_template('index.html')

