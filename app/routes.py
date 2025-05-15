# app/routes.py
from flask import Blueprint, render_template, current_app

main = Blueprint('main', __name__)


@main.route('/', strict_slashes=False)
def home():
    current_app.logger.info("Home route hit")
    return render_template('index.html')

