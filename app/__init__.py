import logging
import os
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

from flask import Flask, g

from config import config_by_name
from app.extensions import db, migrate, jwt, mail, csrf, cors, limiter


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_CONFIG", "development")
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    _init_extensions(app)
    _configure_logging(app)
    _register_blueprints(app)
    _register_jwt_callbacks(app)
    _register_context_processors(app)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    return app


def _init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["APP_BASE_URL"]}})
    limiter.init_app(app)


def _configure_logging(app):
    log_dir = os.path.join(app.config["BASE_DIR"], "logs")
    os.makedirs(log_dir, exist_ok=True)

    handler = RotatingFileHandler(
        os.path.join(log_dir, "taskflow.log"), maxBytes=1_000_000, backupCount=3
    )
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger("taskflow")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    if app.config["DEBUG"]:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)


def _register_blueprints(app):
    from app.blueprints.auth import auth_bp
    from app.blueprints.dashboard import dashboard_bp
    from app.blueprints.projects import projects_bp
    from app.blueprints.tasks import tasks_bp
    from app.blueprints.tags import tags_bp
    from app.blueprints.calendar import calendar_bp
    from app.blueprints.profile import profile_bp
    from app.blueprints.api import api_bp
    from app.blueprints.errors.handlers import register_error_handlers

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(tags_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(api_bp)

    register_error_handlers(app)


def _register_jwt_callbacks(app):
    from app.models import TokenBlocklist

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar() is not None


def _register_context_processors(app):
    @app.context_processor
    def inject_globals():
        from app.utils.notifications import get_notifications

        notifications = []
        current_user = g.get("current_user")
        if current_user:
            notifications = get_notifications(current_user.id)

        return {
            "now": datetime.now(timezone.utc),
            "notifications": notifications,
        }
