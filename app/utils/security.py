import hashlib
import secrets
from datetime import datetime, timedelta, timezone

RESET_TOKEN_TTL_MINUTES = 30


def generate_reset_token():
    """Returns (raw_token, token_hash, expires_at). Only the hash is stored."""
    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_TTL_MINUTES)
    return raw_token, token_hash, expires_at


def hash_token(raw_token):
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
