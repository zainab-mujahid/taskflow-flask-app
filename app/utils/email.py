import logging

from flask import current_app, render_template
from flask_mail import Message

from app.extensions import mail

logger = logging.getLogger("taskflow")


def send_reset_password_email(user, raw_token):
    reset_url = f"{current_app.config['APP_BASE_URL']}/auth/reset-password/{raw_token}"

    if current_app.config.get("MAIL_SUPPRESS_SEND"):
        logger.info("Password reset link for %s: %s", user.email, reset_url)

    msg = Message(
        subject="Reset your TaskFlow password",
        recipients=[user.email],
        body=(
            f"Hi {user.name},\n\n"
            f"We received a request to reset your TaskFlow password.\n"
            f"Click the link below to choose a new password (valid for 30 minutes):\n\n"
            f"{reset_url}\n\n"
            f"If you did not request this, you can safely ignore this email."
        ),
    )
    try:
        mail.send(msg)
    except Exception:
        logger.exception("Failed to send reset password email to %s", user.email)

    return reset_url
