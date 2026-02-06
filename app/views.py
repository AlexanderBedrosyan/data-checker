from flask.views import MethodView
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session, send_file, after_this_request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.models import EnvUser
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import unicodedata
import io
from statements import pdf_convert_to_excel, basic_model, diff_checker, company_mapper
from statements.bc_balances import bc_balance
from app.utils import extract_sheets_to_dicts, receivable_payable_preparation, ic_template_data_bs_preparation, column4_finder, process_excel_with_difference_logic

# Load the .env file
load_dotenv()

auth_blueprint = Blueprint('auth', __name__)


def change_pdf_to_excel_file():
    current_folder_path = os.getcwd().split("\\")
    folder_path = '/'.join(current_folder_path) + "/uploads"
    pdf_paths = pdf_convert_to_excel.find_pdf_file(folder_path)
    excel_path = folder_path + '/' + 'received_vendor_balance.xlsx'
    pdf_convert_to_excel.pdf_to_excel(pdf_paths, excel_path)


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

        captcha_input = request.form.get('captcha_input')

        if captcha_input != session.get('captcha', ''): # new
            flash('Incorrect CAPTCHA. Please try again.', 'danger')
            return redirect(url_for('main.login'))

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
        selected_file = request.form.get('selected_file')
        print(selected_file)
        change_pdf_to_excel_file()
        result = diff_checker.missing_doc_and_wrong_amount(bc_balance.bc_balance(), company_mapper.company_mapper[selected_file].vendor_balance(),
                                     company_mapper.company_mapper[selected_file])
        clear_upload_folder()
        # flash("Analysis complete!", "info")
        # return redirect(url_for('main.home'))
        return result


class CheckReports(MethodView):
    decorators = [login_required]

    def get(self):
        current_app.logger.info("Reports route hit")
        return render_template('report.html')
    

class UploadReportView(MethodView):
    decorators = [login_required]

    def post(self):
        uploaded_files = request.files.getlist('file')
        if not uploaded_files or not uploaded_files[0].filename:
            flash("Не е избран файл.", "danger")
            return redirect(url_for('main.reports'))

        try:
            # Get the uploaded file
            uploaded_file = uploaded_files[0]
            
            # Create a temporary file path for the output
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            # Generate output filename
            original_filename = secure_filename(uploaded_file.filename)
            filename_without_ext, file_ext = os.path.splitext(original_filename)
            output_filename = None
            if "processed"not in filename_without_ext:
                output_filename = f"{filename_without_ext}_processed{file_ext}"
            else:
                output_filename = f"{filename_without_ext}{file_ext}"
            output_path = os.path.join(upload_folder, output_filename)
            
            # Process the Excel file with the new logic
            result_path = process_excel_with_difference_logic(uploaded_file, output_path)
            
            # Load file into memory before cleanup to avoid file locking issues
            with open(result_path, 'rb') as f:
                file_data = io.BytesIO(f.read())
            file_data.seek(0)
            
            # Now safe to clean up the upload folder
            try:
                clear_upload_folder()
            except Exception as e:
                current_app.logger.error(f"Error cleaning upload folder: {e}")
            
            # Send the file from memory to the user
            flash("Файлът е обработен успешно. Изтеглянето започва автоматично.", "success")
            return send_file(
                file_data,
                as_attachment=True,
                download_name=output_filename,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
        except Exception as e:
            current_app.logger.error(f"Error processing file: {e}")
            flash(f"Грешка при обработка на файла: {str(e)}", "danger")
            clear_upload_folder()
            return redirect(url_for('main.reports'))
    

class DeleteReportsView(MethodView):
    decorators = [login_required]

    def post(self):
        clear_upload_folder()
        flash("Всички отчети са изтрити успешно.", "success")
        return redirect(url_for('main.reports'))