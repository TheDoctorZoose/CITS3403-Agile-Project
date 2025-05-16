import os
import tempfile
from typing import Iterator

import flask_unittest
from flask import Flask

from app import create_app, db


def create_test_app(use_memory_db: bool = True) -> Iterator[Flask]:
    """
    Create and configure a new app instance for each test.
    :param use_memory_db: whether to use an in-memory SQLite db, or a temp file.
    """
    if use_memory_db:
        db_uri = "sqlite:///:memory:"
        db_fd = None
        db_path = None
    else:
        db_fd, db_path = tempfile.mkstemp()
        db_uri = f"sqlite:///{db_path}"

    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_uri}",
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

    if not use_memory_db and db_fd is not None:
        os.close(db_fd)
        os.remove(db_path)

class TestBaseMemoryDB(flask_unittest.AppClientTestCase):
    def create_app(self):
        yield from create_test_app(use_memory_db=True)

class TestBaseWithFileDB(flask_unittest.AppClientTestCase):
    def create_app(self):
        yield from create_test_app(use_memory_db=False)
