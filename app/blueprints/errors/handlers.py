import logging

from flask import render_template, request, jsonify

from app.extensions import db

logger = logging.getLogger("taskflow")


def _wants_json():
    return request.path.startswith("/api")


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        if _wants_json():
            return jsonify({"error": "Bad request"}), 400
        return render_template("errors/404.html"), 400

    @app.errorhandler(401)
    def unauthorized(error):
        if _wants_json():
            return jsonify({"error": "Authentication required"}), 401
        return render_template("errors/404.html"), 401

    @app.errorhandler(403)
    def forbidden(error):
        if _wants_json():
            return jsonify({"error": "Forbidden"}), 403
        return render_template("errors/404.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        if _wants_json():
            return jsonify({"error": "Not found"}), 404
        return render_template("errors/404.html"), 404

    @app.errorhandler(429)
    def rate_limited(error):
        if _wants_json():
            return jsonify({"error": "Too many requests, please slow down."}), 429
        return render_template("errors/500.html"), 429

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        logger.exception("Unhandled server error: %s", error)
        if _wants_json():
            return jsonify({"error": "Internal server error"}), 500
        return render_template("errors/500.html"), 500
