from .views import HomeView, LoginView, LogoutView, UploadView, AnalyzeView
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, session
from flask_login import login_required

auth = Blueprint('auth', __name__)
main = Blueprint('main', __name__)


@main.route('/get-file-options')

@login_required
def get_file_options():
    # if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
    #     abort(403)
    query = request.args.get('q', '').lower()

    files = [
        {'id': 'ah_fragt', 'text': 'Ah Fragt'},
        {'id': 'egsj', 'text': 'Esbjerg Gods'},
        {'id': 'nordjysk_trailer', 'text': 'Nordjysk trailer udlejning'},
        {'id': 'dtk_road', 'text': 'DTK Road A/S'},
        {'id': 'transfennica_ltd', 'text': 'Transfennica LTD'},
        {'id': 'dsv_road_as', 'text': 'DSV ROAD A/S'},
        {'id': 'svend_e_sorensen', 'text': 'Svend E. Sorensen'},
    ]

    filtered = [f for f in files if query in f['text'].lower()]

    return jsonify(filtered)


@main.route('/set-captcha', methods=['POST'])
def set_captcha():
    captcha = request.json.get('captcha')
    session['captcha'] = captcha
    return '', 200

main.add_url_rule('/', view_func=HomeView.as_view('home'))
main.add_url_rule('/login', view_func=LoginView.as_view('login'))
main.add_url_rule('/logout', view_func=LogoutView.as_view('logout'))
main.add_url_rule('/upload', view_func=UploadView.as_view('upload'))
main.add_url_rule('/analyze', view_func=AnalyzeView.as_view('analyze'))

