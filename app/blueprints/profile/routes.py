from flask import render_template, request, redirect, url_for, flash, g, jsonify
from marshmallow import ValidationError

from app.blueprints.profile import profile_bp
from app.extensions import db
from app.models import User
from app.schemas.user_schema import UpdateProfileSchema
from app.schemas.auth_schema import ChangePasswordSchema
from app.utils.decorators import web_login_required
from app.utils.helpers import allowed_avatar_file, save_avatar, delete_avatar


@profile_bp.before_request
@web_login_required
def _require_login():
    pass


@profile_bp.route("/")
def index():
    return render_template(
        "profile/index.html",
        profile_errors={},
        password_errors={},
    )


@profile_bp.route("/", methods=["POST"])
def update_profile():
    schema = UpdateProfileSchema()
    try:
        data = schema.load(request.form)
    except ValidationError as err:
        return render_template("profile/index.html", profile_errors=err.messages, password_errors={}), 400

    existing = User.query.filter(User.email == data["email"].lower(), User.id != g.current_user.id).first()
    if existing:
        return render_template(
            "profile/index.html",
            profile_errors={"email": ["This email is already in use."]},
            password_errors={},
        ), 400

    g.current_user.name = data["name"].strip()
    g.current_user.email = data["email"].lower()
    db.session.commit()
    flash("Profile updated successfully.", "success")
    return redirect(url_for("profile.index"))


@profile_bp.route("/password", methods=["POST"])
def change_password():
    schema = ChangePasswordSchema()
    try:
        data = schema.load(request.form)
    except ValidationError as err:
        return render_template("profile/index.html", profile_errors={}, password_errors=err.messages), 400

    if not g.current_user.check_password(data["current_password"]):
        return render_template(
            "profile/index.html",
            profile_errors={},
            password_errors={"current_password": ["Current password is incorrect."]},
        ), 400

    g.current_user.set_password(data["new_password"])
    db.session.commit()
    flash("Password changed successfully.", "success")
    return redirect(url_for("profile.index"))


@profile_bp.route("/avatar", methods=["POST"])
def upload_avatar():
    file = request.files.get("avatar")
    if not file or file.filename == "":
        flash("Please choose an image to upload.", "error")
        return redirect(url_for("profile.index"))

    if not allowed_avatar_file(file.filename):
        flash("Unsupported file type. Please upload a PNG, JPG, WEBP or GIF.", "error")
        return redirect(url_for("profile.index"))

    old_avatar = g.current_user.avatar_url
    g.current_user.avatar_url = save_avatar(file)
    db.session.commit()
    delete_avatar(old_avatar)

    flash("Profile picture updated.", "success")
    return redirect(url_for("profile.index"))


@profile_bp.route("/theme", methods=["POST"])
def update_theme():
    payload = request.get_json(silent=True) or {}
    theme = payload.get("theme")
    if theme not in ("light", "dark"):
        return jsonify({"error": "Invalid theme"}), 400
    g.current_user.theme = theme
    db.session.commit()
    return jsonify({"theme": theme})
