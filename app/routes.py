from .views import HomeView, LoginView, LogoutView, UploadView, AnalyzeView
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify

auth = Blueprint('auth', __name__)
main = Blueprint('main', __name__)


@main.route('/get-file-options')
def get_file_options():
    query = request.args.get('q', '').lower()

    files = [
        {'id': '1', 'text': 'Gosho'},
        {'id': '2', 'text': 'Ivan'},
        {'id': '3', 'text': 'Dragan'},
        {'id': '3', 'text': 'Petkan'},
    ]

    filtered = [f for f in files if query in f['text'].lower()]

    return jsonify(filtered)


main.add_url_rule('/', view_func=HomeView.as_view('home'))
main.add_url_rule('/login', view_func=LoginView.as_view('login'))
main.add_url_rule('/logout', view_func=LogoutView.as_view('logout'))
main.add_url_rule('/upload', view_func=UploadView.as_view('upload'))
main.add_url_rule('/analyze', view_func=AnalyzeView.as_view('analyze'))

