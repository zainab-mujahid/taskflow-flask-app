import pytest

from app import create_app
from app.extensions import db as _db
from app.models import Task

TEST_PASSWORD = "Sup3rSecret1!"


@pytest.fixture()
def app():
    """A Flask app configured for testing, with a fresh in-memory database
    created before each test and dropped after it."""
    application = create_app("testing")
    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    return _db


@pytest.fixture()
def make_user(db):
    """Factory fixture for creating a persisted User with a hashed password."""
    from app.models import User

    def _make_user(name="Jane Doe", email="jane@example.com", password=TEST_PASSWORD):
        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    return _make_user


@pytest.fixture()
def make_task(db):
    """Factory fixture for creating a persisted Task owned by the given user."""

    def _make_task(user, title="Write tests", **kwargs):
        task = Task(user_id=user.id, title=title, **kwargs)
        db.session.add(task)
        db.session.commit()
        return task

    return _make_task


@pytest.fixture()
def login(client):
    """Logs the test client in via the real /auth/login route so cookie-based
    auth (JWT in httpOnly cookies) behaves exactly as it does in the browser."""

    def _login(email, password=TEST_PASSWORD):
        return client.post("/auth/login", data={"email": email, "password": password})

    return _login


@pytest.fixture()
def auth_client(client, make_user, login):
    """A (client, user) pair where the client already holds a valid session cookie."""
    user = make_user()
    login(user.email)
    return client, user
