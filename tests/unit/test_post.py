from app import db
from app.models import User, GameEntry

from tests.unit.conftest import TestBase


class TestGameEntrySubmission(TestBase):

    def setUp(self, app, client):
        with app.app_context():
            user = User(username="testuser", email="<EMAIL>")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()

    def test_submit_game_entry_with_multiple_players(self, app, client):
        # Log in as the test user
        client.post(
            "/login", data={"email": "testuser@example.com", "password": "password123"}
        )

        # Submit a game entry with multiple players
        response = client.post(
            "/forum",
            data={
                "gameTitle": "Catan",
                "datePlayed": "2025-04-20",
                "visibility": "public",
                "player_name": ["Alice", "Bob"],
                "player_username": ["", ""],
                "score": ["10", "8"],
                "win": ["0"],  # Alice won
                "went_first": ["0"],  # Alice went first
                "first_time_playing": [
                    "1",
                    "1",
                ],  # Both players played for the first time
            },
        )

        # Assert the response redirects (successful submission)
        self.assertEqual(response.status_code, 302)

        # Verify the game entry and players in the database
        with app.app_context():
            entries = GameEntry.query.all()
            self.assertEqual(
                2, len(entries), "Expected there to be two entries for two players."
            )  # Two players, two entries
            self.assertEqual("Catan", entries[0].game_title)
            self.assertEqual(10, entries[0].score)
            self.assertTrue(entries[0].win)
            self.assertTrue(entries[0].went_first)
            self.assertTrue(entries[0].first_time_playing)
            self.assertEqual(8, entries[1].score)
            self.assertFalse(entries[1].win)
