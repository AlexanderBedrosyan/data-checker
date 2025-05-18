from .views import HomeView, LoginView
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app

main = Blueprint('main', __name__)

main.add_url_rule('/', view_func=HomeView.as_view('home'))
main.add_url_rule('/login', view_func=LoginView.as_view('login'))

