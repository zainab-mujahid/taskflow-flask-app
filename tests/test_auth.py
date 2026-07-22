from urllib.parse import urlparse

from app.models import User

TEST_PASSWORD = "Sup3rSecret1!"  # must match tests/conftest.py's TEST_PASSWORD


def _redirect_path(response):
    return urlparse(response.headers["Location"]).path


def register(client, **overrides):
    data = {
        "name": "New User",
        "email": "newuser@example.com",
        "password": TEST_PASSWORD,
        "confirm_password": TEST_PASSWORD,
    }
    data.update(overrides)
    return client.post("/auth/register", data=data)


class TestRegister:
    def test_valid_registration_creates_user_and_redirects_to_login(self, client):
        response = register(client)

        assert response.status_code == 302
        assert _redirect_path(response) == "/auth/login"

        user = User.query.filter_by(email="newuser@example.com").first()
        assert user is not None
        assert user.check_password(TEST_PASSWORD)

    def test_duplicate_email_is_rejected(self, client, make_user):
        make_user(email="taken@example.com")

        response = register(client, email="taken@example.com")

        assert response.status_code == 400
        assert b"already exists" in response.data
        assert User.query.filter_by(email="taken@example.com").count() == 1

    def test_mismatched_passwords_are_rejected(self, client):
        response = register(client, confirm_password="a-different-password")

        assert response.status_code == 400
        assert User.query.filter_by(email="newuser@example.com").first() is None

    def test_weak_password_is_rejected(self, client):
        response = register(client, password="short", confirm_password="short")

        assert response.status_code == 400
        assert User.query.filter_by(email="newuser@example.com").first() is None


class TestLogin:
    def test_valid_login_sets_auth_cookie_and_redirects_to_dashboard(self, client, make_user):
        user = make_user(email="login@example.com")

        response = client.post(
            "/auth/login", data={"email": user.email, "password": TEST_PASSWORD}
        )

        assert response.status_code == 302
        assert _redirect_path(response) == "/"
        cookie_headers = response.headers.get_all("Set-Cookie")
        assert any("access_token" in header for header in cookie_headers)

    def test_invalid_password_is_rejected(self, client, make_user):
        user = make_user(email="login2@example.com")

        response = client.post(
            "/auth/login", data={"email": user.email, "password": "wrong-password"}
        )

        assert response.status_code == 401
        assert b"Invalid email or password" in response.data

    def test_unknown_email_is_rejected(self, client):
        response = client.post(
            "/auth/login", data={"email": "nobody@example.com", "password": TEST_PASSWORD}
        )

        assert response.status_code == 401


class TestProtectedPages:
    def test_dashboard_requires_login(self, client):
        response = client.get("/")

        assert response.status_code == 302
        assert _redirect_path(response) == "/auth/login"

    def test_logged_in_user_can_reach_dashboard(self, auth_client):
        client, _user = auth_client

        response = client.get("/")

        assert response.status_code == 200


class TestLogout:
    def test_logout_ends_the_session(self, auth_client):
        client, _user = auth_client
        assert client.get("/").status_code == 200

        logout_response = client.get("/auth/logout")
        assert logout_response.status_code == 302
        assert _redirect_path(logout_response) == "/auth/login"

        response = client.get("/")
        assert response.status_code == 302
        assert _redirect_path(response) == "/auth/login"
