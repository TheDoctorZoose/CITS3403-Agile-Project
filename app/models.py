from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timezone
from app import db 

friendships = db.Table('friendships',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('friend_id', db.Integer, db.ForeignKey('user.id'))
)

gameentry_permissions = db.Table('gameentry_permissions',
    db.Column('entry_id', db.Integer, db.ForeignKey('game_entry.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.now)
    bio = db.Column(db.Text, default='', nullable=True)

    # Messages
    messages_sent = db.relationship(
        'Message',
        foreign_keys='Message.sender_id',
        back_populates='sender',
        lazy=True
    )
    messages_received = db.relationship(
        'Message',
        foreign_keys='Message.receiver_id',
        back_populates='receiver',
        lazy=True
    )

    # Other relationships
    posts = db.relationship('Post', backref='user', lazy=True)
    likes = db.relationship('Like', backref='user', lazy='dynamic')
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic')

    # Friend system
    friends = db.relationship(
        'User',
        secondary=friendships,
        primaryjoin=(friendships.c.user_id == id),
        secondaryjoin=(friendships.c.friend_id == id),
        backref='friends_with',
        lazy='dynamic'
    )

    sent_requests = db.relationship(
        'FriendRequest',
        foreign_keys='FriendRequest.sender_id',
        back_populates='sender',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )

    received_requests = db.relationship(
        'FriendRequest',
        foreign_keys='FriendRequest.receiver_id',
        back_populates='receiver',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



class FriendRequest(db.Model):
    __tablename__ = 'friend_request'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id], back_populates='sent_requests')
    receiver = db.relationship('User', foreign_keys=[receiver_id], back_populates='received_requests')

    __table_args__ = (
        db.UniqueConstraint('sender_id', 'receiver_id', name='unique_friend_request'),
    )

class GameEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_title = db.Column(db.String(100))
    date_played = db.Column(db.Date)
    win = db.Column(db.Boolean, default=False, nullable=False)
    went_first = db.Column(db.Boolean, default=False, nullable=False)
    first_time_playing = db.Column(db.Boolean, default=False, nullable=False)
    score = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.now)

    # 权限控制：哪些用户可以访问该上传记录
    allowed_users = db.relationship(
        'User',
        secondary=gameentry_permissions,
        backref='permitted_game_entries'
    )

    # 交互记录
    likes = db.relationship('Like', backref='entry', lazy='dynamic', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='entry', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='entry', lazy='dynamic', cascade='all, delete-orphan')

    user = db.relationship('User', backref='entries')



class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    entry_id = db.Column(db.Integer, db.ForeignKey('game_entry.id'), nullable=False)

    user = db.relationship('User', backref='comments')
    


class RawCSVEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    raw_data = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    entry_id = db.Column(db.Integer, db.ForeignKey('game_entry.id'))
    timestamp = db.Column(db.DateTime, default=datetime.now)


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    entry_id = db.Column(db.Integer, db.ForeignKey('game_entry.id'))
    timestamp = db.Column(db.DateTime, default=datetime.now)


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
   

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    sender = db.relationship('User', foreign_keys=[sender_id], back_populates='messages_sent')
    receiver = db.relationship('User', foreign_keys=[receiver_id], back_populates='messages_received')
