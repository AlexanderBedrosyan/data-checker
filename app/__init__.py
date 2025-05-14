# app/__init__.py
from flask import Flask


def create_app(config_class=None):
    app = Flask(__name__)

    if config_class:
        app.config.from_object(config_class)
    else:
        from .config import Config
        app.config.from_object(Config)

    from .routes import main
    app.register_blueprint(main)

    return app
