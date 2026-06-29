import os
import logging
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from config import config_map

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Inicia sesión para acceder al sistema.'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(user_id):
    from .models import User

    return User.query.get(int(user_id))


def create_app(config_name='development'):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_map[config_name])

    db.init_app(app)
    login_manager.init_app(app)

    if not os.path.isdir(app.instance_path):
        os.makedirs(app.instance_path)
    if not os.path.isdir(os.path.join(os.getcwd(), 'logs')):
        os.makedirs(os.path.join(os.getcwd(), 'logs'))

    setup_logging(app)

    from . import auth, admin_routes, routes

    app.register_blueprint(routes.bp_api)
    app.register_blueprint(routes.bp_dashboard)
    app.register_blueprint(auth.bp_auth)
    app.register_blueprint(admin_routes.bp_admin)

    from . import models

    with app.app_context():
        db.create_all()

    return app


def setup_logging(app):
    if not app.debug:
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE_PATH'],
            maxBytes=10240,
            backupCount=10,
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Sensor Server Startup')
