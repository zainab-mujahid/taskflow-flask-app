from flask import Blueprint

tags_bp = Blueprint("tags", __name__, url_prefix="/tags")

from app.blueprints.tags import routes  # noqa: E402,F401
