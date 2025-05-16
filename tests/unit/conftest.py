from typing import Iterator

import flask_unittest
from flask import Flask

from app import create_app, db


def _create_app(_) -> Iterator[Flask]:
    """
    Create and configure a new app instance for each test.
    :param use_memory_db: whether to use an in-memory SQLite db, or a temp file.
    """
    db_uri = "sqlite:///:memory:"

    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": db_uri,
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


class TestBase(flask_unittest.AppClientTestCase):
    create_app = _create_app
