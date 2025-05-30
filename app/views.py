from flask.views import MethodView
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.models import EnvUser
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import unicodedata

# Load the .env file
load_dotenv()

auth_blueprint = Blueprint('auth', __name__)


def clear_upload_folder():
    upload_folder = current_app.config['UPLOAD_FOLDER']
    for filename in os.listdir(upload_folder):
        file_path = os.path.join(upload_folder, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            current_app.logger.error(f'Error deleting file {file_path}: {e}')


class LoginView(MethodView):
    def get(self):
        if current_user.is_authenticated:
            return redirect(url_for('main.home'))
        return render_template('index.html')

    def post(self):
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        private_username = os.getenv("USER")
        private_password = os.getenv("PASSWORD")
        private_email = os.getenv("EMAIL")

        if username == private_username and email == private_email and password == private_password:
            user = EnvUser(email)
            login_user(user)
            return redirect(url_for('main.home'))

        else:
            flash('Invalid login credentials.', 'danger')
            return render_template('index.html')


class HomeView(MethodView):
    decorators = [login_required]

    def get(self):
        current_app.logger.info("Home route hit")
        return render_template('home.html')


class LogoutView(MethodView):
    decorators = [login_required]

    def post(self):
        logout_user()
        flash("Logged out successfully.", "success")
        return redirect(url_for('main.login'))


class UploadView(MethodView):
    decorators = [login_required]

    def post(self):
        uploaded_files = request.files.getlist('file')
        if not uploaded_files:
            flash("Не е избран файл.", "danger")
            return redirect(url_for('main.home'))

        for current_file in uploaded_files:
            filename = unicodedata.normalize('NFKD', current_file.filename).encode('ascii', 'ignore').decode('ascii')
            file_ext = os.path.splitext(filename)[1].lower()
            allowed_extensions = current_app.config['UPLOAD_EXTENSIONS']
            if file_ext not in allowed_extensions:
                flash("Неразрешен тип файл.", "danger")
                return redirect(url_for('main.home'))

            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            current_file.save(upload_path)
            flash("Файлът е качен успешно.", "success")
        return redirect(url_for('main.home'))


class AnalyzeView(MethodView):
    decorators = [login_required]

    def post(self):

        clear_upload_folder()
        # Тук ще добавиш логиката си по-късно
        flash("Analysis complete!", "info")
        return redirect(url_for('main.home'))

