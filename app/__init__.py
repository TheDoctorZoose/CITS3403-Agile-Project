import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .config import Config
from flask_sock import Sock
from flask_mail import Mail
from dotenv import load_dotenv

mail = Mail()
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
sock = Sock()
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '..', '.env'))

def create_app():
    app = Flask(__name__)
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
    
    from app import chat  # 确保你的 chat.py 在 app 目录下
    chat.register_chat_routes(sock)


    return app
