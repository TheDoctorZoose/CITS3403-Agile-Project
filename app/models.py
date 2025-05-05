from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from app import db 

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.relationship('Like', backref='user', lazy='dynamic')
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic')


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class GameEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_title = db.Column(db.String(100))
    date_played = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.relationship('Like', backref='entry', lazy='dynamic')
    favorites = db.relationship('Favorite', backref='entry', lazy='dynamic')

    user = db.relationship('User', backref='entries')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    entry_id = db.Column(db.Integer, db.ForeignKey('game_entry.id'), nullable=False)

    user = db.relationship('User', backref='comments')
    entry = db.relationship('GameEntry', backref='comments')


class RawCSVEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    raw_data = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    entry_id = db.Column(db.Integer, db.ForeignKey('game_entry.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    entry_id = db.Column(db.Integer, db.ForeignKey('game_entry.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

