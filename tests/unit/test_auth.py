from app import db
from app.models import User, FriendRequest
from conftest import TestBase


class TestUserRegistration(TestBase):

    def test_register_page(self, app, client):
        """GET /register returns the registration form."""
        response = client.get('/register')
        self.assertStatus(response, 200)
        self.assertIn(b"Register", response.data)

    def test_user_registration(self, app, client):
        """Test user registration functionality."""
        response = client.post('/register', data={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': "hunter7",
            "confirm_password": "hunter7",
        })
        self.assertEqual(302, response.status_code)

class TestUserLogin(TestBase):

    def setUp(self, app, client):
        with app.app_context():
            user = User(username="testuser", email="testuser@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()

    def test_login_page(self, app, client):
        """Test if the login page is accessible."""
        response = client.get('/login')
        self.assertEqual(200, response.status_code)
        self.assertIn(b"Login", response.data)

    def test_user_login(self, app, client):
        """Test user login functionality."""
        response = client.post('/login', data={
            'email': 'testuser@example.com',
            'password': "password123",
        })
        self.assertEqual(302, response.status_code)

    def test_incorrect_password(self, app, client):
        """Test prevent user logging in badly."""
        response = client.post('/login', data={
            'email': 'testuser@example.com',
            'password': 'hunter7',
        })
        self.assertEqual(200, response.status_code)

class TestFriendRequests(TestBase):

    def setUp(self, app, client):
        with app.app_context():
            user1 = User(username="Alice", email="user1@example.com")
            user1.set_password("password123")
            user2 = User(username="Bob", email="user2@example.com")
            user2.set_password("password123")

            db.session.add_all([user1, user2])
            db.session.commit()

    def test_send_friend_request(self, app, client):
        """Test sending a friend request."""
        client.post('/login', data={'email': 'user1@example.com', 'password': "password123"})
        response = client.post('/send_request/2')
        self.assertEqual(302, response.status_code)

    def test_accept_friend_request(self, app, client):
        """Test accepting a friend request."""
        with app.app_context():
            user1 = User.query.filter_by(email="user1@example.com").first()
            user2 = User.query.filter_by(email="user2@example.com").first()

            request = FriendRequest(sender=user2, receiver=user1)
            db.session.add(request)
            db.session.commit()


        client.post('/login', data={'email': 'user1@example.com', 'password': 'password123'})
        response = client.post('/accept_request/1')
        self.assertEqual(302, response.status_code)
