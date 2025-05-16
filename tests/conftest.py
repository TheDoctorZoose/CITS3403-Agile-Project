import os
import tempfile
from typing import Iterator

import flask_unittest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app, db

# with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
#     _data_sql = f.read().decode("utf-8")

def _create_app(self) -> Iterator[Flask]:
    """Create and configure a new app instance for each test."""
    db_fd, db_path = tempfile.mkstemp()
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "testing-secret",
        }
    )
    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()

    os.close(db_fd)
    os.remove(db_path)

class TestBase(flask_unittest.AppClientTestCase):
    create_app = _create_app