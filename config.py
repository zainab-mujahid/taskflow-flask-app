import os
from datetime import timedelta

from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def _bool(name, default="False"):
    return os.environ.get(name, default).strip().lower() in ("1", "true", "yes", "on")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    DEBUG = _bool("DEBUG", "True")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/taskmanager"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT (stored in httpOnly cookies since the UI is server-rendered)
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_ACCESS_COOKIE_NAME = "access_token"
    JWT_REFRESH_COOKIE_NAME = "refresh_token"
    JWT_ACCESS_COOKIE_PATH = "/"
    JWT_REFRESH_COOKIE_PATH = "/"
    # CSRF protection for all state-changing requests (web forms and /api/* alike)
    # is handled by Flask-WTF's CSRFProtect instead, so flask-jwt-extended's own
    # double-submit CSRF layer is disabled here to avoid two competing mechanisms.
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_COOKIE_SECURE = _bool("JWT_COOKIE_SECURE", "False")
    JWT_COOKIE_SAMESITE = "Lax"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "30"))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.environ.get("JWT_REFRESH_TOKEN_EXPIRES_DAYS", "7"))
    )

    # Mail
    MAIL_SUPPRESS_SEND = _bool("MAIL_SUPPRESS_SEND", "True")
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_USE_TLS = _bool("MAIL_USE_TLS", "True")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "no-reply@taskflow.local")

    # Uploads
    BASE_DIR = BASE_DIR
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads", "avatars")
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_UPLOAD_SIZE_MB", "2")) * 1024 * 1024
    ALLOWED_AVATAR_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}

    APP_BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:5000")

    WTF_CSRF_TIME_LIMIT = None

    RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    JWT_COOKIE_SECURE = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL", "sqlite:///:memory:"
    )
    MAIL_SUPPRESS_SEND = True
    # Forms/API calls in tests don't carry a CSRF token or a real client IP,
    # so both protections are disabled for the testing profile only.
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
