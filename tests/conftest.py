import pytest
import os
import tempfile

from app import create_app
from app.models import init_app
from app import models


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///'+db_path
    })

    yield app

    models.db.session.remove()
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


