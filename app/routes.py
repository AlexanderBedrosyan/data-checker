# app/routes.py
from flask import Blueprint, render_template
import logging
logging.basicConfig(level=logging.DEBUG)

main = Blueprint('main', __name__)


@main.route('/', strict_slashes=False)
def home():
    app.logger.info("Home route hit")
    return render_template('index.html')


