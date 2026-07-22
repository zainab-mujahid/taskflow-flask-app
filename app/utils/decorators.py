from functools import wraps

from flask import g, redirect, request, url_for, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask_jwt_extended.exceptions import NoAuthorizationError
from jwt.exceptions import PyJWTError

from app.models import User


def _load_current_user():
    user_id = get_jwt_identity()
    if user_id is None:
        return None
    return User.query.get(int(user_id))


def web_login_required(view_func):
    """Protects server-rendered pages: redirects to login instead of a 401 JSON body."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except (NoAuthorizationError, PyJWTError):
            return redirect(url_for("auth.login", next=request.path))

        user = _load_current_user()
        if user is None:
            return redirect(url_for("auth.login", next=request.path))

        g.current_user = user
        return view_func(*args, **kwargs)

    return wrapper


def api_login_required(view_func):
    """Protects JSON /api endpoints: returns 401 JSON instead of redirecting."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except (NoAuthorizationError, PyJWTError):
            return jsonify({"error": "Authentication required"}), 401

        user = _load_current_user()
        if user is None:
            return jsonify({"error": "Authentication required"}), 401

        g.current_user = user
        return view_func(*args, **kwargs)

    return wrapper


def load_logged_in_user():
    """Best-effort loader used on public pages so the navbar can reflect auth state."""
    try:
        verify_jwt_in_request(optional=True)
        g.current_user = _load_current_user()
    except (NoAuthorizationError, PyJWTError):
        g.current_user = None
