import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "2b_is_great"

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'cits3403groupproject0309@gmail.com'
    MAIL_PASSWORD = 'xzqytcwiajplxlsj'
    MAIL_DEFAULT_SENDER = ('CITS3403','cits3403groupproject0309@gmail.com')
