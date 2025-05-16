import unittest

from app import db
from app.models import User, GameEntry, FriendRequest

from tests.conftest import TestBase

class TestRoutes(TestBase):

    def setUp(self, app, client):
        with app.app_context():
            user = User(username="testuser", email="testuser@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()

    def test_index_route(self, _, client):
        response = client.get("/")
        self.assertEqual(200, response.status_code)
        self.assertIn(b"index", response.data)

    def test_profile_route(self, _, client):
        client.post("/login", data={
            "email": "testuser@example.com",
            "password": "password123",
        })
        response = client.get("/profile/1")
        self.assertEqual(200, response.status_code)
        self.assertIn(b"testuser", response.data)

    def test_forum_post_route(self, _, client):
        client.post("/login", data={
            'email': "testuser@example.com",
            "password": "password123",
        })
        response = client.post('/forum', data={
            'gameTitle': "Catan",
            'datePlayed': '2025-04-20',
            'visibility': 'public',
            'player_name': ['Player1'],
            'player_username': [''],
            'score': ['10'],
            'win': ['0'],
            'went_first': ['0'],
            'first_time_playing': ['0'],
        })
        self.assertEqual(302, response.status_code)
        self.assertEqual(1, GameEntry.query.count())

    def test_friend_request_routes(self, app, client):
        with app.app_context():
            user2 = User(username="frienduser", email="friend@example.com")
            user2.set_password("password123")
            db.session.add(user2)
            db.session.commit()

        client.post('/login', data={
            'email': 'testuser@example.com',
            'password': 'password123',
        })
        response = client.post('/send_request/2')
        self.assertEqual(302, response.status_code)
        with app.app_context():
            self.assertEqual(1, FriendRequest.query.count())



if __name__ == "__main__":
    unittest.main()