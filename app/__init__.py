import os
from typing import Mapping

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sock import Sock
from flask_sqlalchemy import SQLAlchemy

from .config import Config

mail = Mail()
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "main.login"
sock = Sock()
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, "..", ".env"))


def create_app(alternate_config: Mapping = None):
    app = Flask(__name__)
    if alternate_config:
        app.config.from_mapping(**alternate_config)
    else:
        app.config.from_object(Config)
    mail.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    sock.init_app(app)

    from app.routes import main

    app.register_blueprint(main)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app import chat

    chat.register_chat_routes(sock)

    return app
