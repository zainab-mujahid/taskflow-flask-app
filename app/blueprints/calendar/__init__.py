from flask import Blueprint

calendar_bp = Blueprint("calendar_bp", __name__, url_prefix="/calendar")

from app.blueprints.calendar import routes  # noqa: E402,F401
