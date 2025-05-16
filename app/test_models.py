
import unittest
from app import db, create_app
from app.models import User, FriendRequest, Message, GameEntry, Like, Favorite
from flask_testing import TestCase
from datetime import datetime

class BaseTestCase(TestCase):
    def create_app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def setUp(self):
        db.create_all()
        self.user1 = User(username="user1", email="user1@example.com")
        self.user1.set_password("password")
        self.user2 = User(username="user2", email="user2@example.com")
        self.user2.set_password("password")
        db.session.add_all([self.user1, self.user2])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

class TestModels(BaseTestCase):
    def test_user_creation(self):
        self.assertEqual(User.query.count(), 2)

    def test_friend_request_creation(self):
        req = FriendRequest(sender_id=self.user1.id, receiver_id=self.user2.id)
        db.session.add(req)
        db.session.commit()
        self.assertEqual(FriendRequest.query.count(), 1)

    def test_like_model(self):
        entry = GameEntry(game_title="Test", date_played=datetime.today(), user_id=self.user1.id)
        db.session.add(entry)
        db.session.commit()
        like = Like(user_id=self.user2.id, entry_id=entry.id)
        db.session.add(like)
        db.session.commit()
        self.assertEqual(Like.query.count(), 1)

    def test_favorite_model(self):
        entry = GameEntry(game_title="Test2", date_played=datetime.today(), user_id=self.user1.id)
        db.session.add(entry)
        db.session.commit()
        fav = Favorite(user_id=self.user2.id, entry_id=entry.id)
        db.session.add(fav)
        db.session.commit()
        self.assertEqual(Favorite.query.count(), 1)

    def test_message_model(self):
        msg = Message(sender_id=self.user1.id, receiver_id=self.user2.id, content="hello")
        db.session.add(msg)
        db.session.commit()
        self.assertEqual(Message.query.count(), 1)
