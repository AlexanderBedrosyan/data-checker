# app/routes.py
from flask import Blueprint, render_template

main = Blueprint('main', __name__)


@main.route('/', strict_slashes=False)
def home():
    return render_template('index.html')


