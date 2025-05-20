from .views import HomeView, LoginView, LogoutView
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app

auth = Blueprint('auth', __name__)
main = Blueprint('main', __name__)

main.add_url_rule('/', view_func=HomeView.as_view('home'))
main.add_url_rule('/login', view_func=LoginView.as_view('login'))
main.add_url_rule('/logout', view_func=LogoutView.as_view('logout'))

