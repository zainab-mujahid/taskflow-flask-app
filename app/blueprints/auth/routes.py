from flask import render_template, request, redirect, url_for, flash, g
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
    verify_jwt_in_request,
    get_jwt,
)
from marshmallow import ValidationError

from app.blueprints.auth import auth_bp
from app.extensions import db, limiter
from app.models import User, PasswordResetToken, TokenBlocklist
from app.schemas.auth_schema import (
    RegisterSchema,
    LoginSchema,
    ForgotPasswordSchema,
    ResetPasswordSchema,
)
from app.utils.security import generate_reset_token, hash_token
from app.utils.email import send_reset_password_email
from app.utils.decorators import load_logged_in_user


@auth_bp.before_request
def _load_user():
    load_logged_in_user()


@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("10 per hour", methods=["POST"])
def register():
    if g.get("current_user"):
        return redirect(url_for("dashboard.index"))

    if request.method == "GET":
        return render_template("auth/register.html", errors={}, form_data={})

    schema = RegisterSchema()
    try:
        data = schema.load(request.form)
    except ValidationError as err:
        return render_template(
            "auth/register.html", errors=err.messages, form_data=request.form
        ), 400

    if User.query.filter_by(email=data["email"].lower()).first():
        return render_template(
            "auth/register.html",
            errors={"email": ["An account with this email already exists."]},
            form_data=request.form,
        ), 400

    user = User(name=data["name"].strip(), email=data["email"].lower())
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    flash("Account created successfully. Please sign in.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"])
def login():
    if g.get("current_user"):
        return redirect(url_for("dashboard.index"))

    next_url = request.args.get("next") or request.form.get("next")

    if request.method == "GET":
        return render_template("auth/login.html", errors={}, form_data={}, next=next_url)

    schema = LoginSchema()
    try:
        data = schema.load(request.form)
    except ValidationError as err:
        return render_template(
            "auth/login.html", errors=err.messages, form_data=request.form, next=next_url
        ), 400

    user = User.query.filter_by(email=data["email"].lower()).first()
    if not user or not user.check_password(data["password"]):
        return render_template(
            "auth/login.html",
            errors={"password": ["Invalid email or password."]},
            form_data=request.form,
            next=next_url,
        ), 401

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    redirect_to = next_url if next_url and next_url.startswith("/") else url_for("dashboard.index")
    response = redirect(redirect_to)
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    flash(f"Welcome back, {user.name.split(' ')[0]}!", "success")
    return response


@auth_bp.route("/logout")
def logout():
    response = redirect(url_for("auth.login"))
    try:
        verify_jwt_in_request(optional=True)
        claims = get_jwt()
        if claims:
            db.session.add(TokenBlocklist(jti=claims["jti"]))
            db.session.commit()
    except Exception:
        pass
    unset_jwt_cookies(response)
    flash("You have been signed out.", "info")
    return response


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
@limiter.limit("5 per hour", methods=["POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("auth/forgot_password.html", errors={}, form_data={})

    schema = ForgotPasswordSchema()
    try:
        data = schema.load(request.form)
    except ValidationError as err:
        return render_template(
            "auth/forgot_password.html", errors=err.messages, form_data=request.form
        ), 400

    user = User.query.filter_by(email=data["email"].lower()).first()
    if user:
        raw_token, token_hash, expires_at = generate_reset_token()
        db.session.add(
            PasswordResetToken(user_id=user.id, token_hash=token_hash, expires_at=expires_at)
        )
        db.session.commit()
        send_reset_password_email(user, raw_token)

    flash(
        "If an account exists for that email, a reset link has been sent.",
        "info",
    )
    return redirect(url_for("auth.login"))


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    token_hash = hash_token(token)
    reset_record = PasswordResetToken.query.filter_by(token_hash=token_hash).first()

    if not reset_record or not reset_record.is_valid():
        flash("This reset link is invalid or has expired. Please request a new one.", "error")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "GET":
        return render_template("auth/reset_password.html", errors={}, token=token)

    schema = ResetPasswordSchema()
    try:
        data = schema.load(request.form)
    except ValidationError as err:
        return render_template(
            "auth/reset_password.html", errors=err.messages, token=token
        ), 400

    user = User.query.get(reset_record.user_id)
    user.set_password(data["password"])
    reset_record.used = True
    db.session.commit()

    flash("Your password has been reset. Please sign in.", "success")
    return redirect(url_for("auth.login"))
