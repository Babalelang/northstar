"""Password hashing + signed session tokens, stdlib only (no bcrypt/jwt
dependency to install). Good enough for a small admin/editor panel like
this one - if VUVA ever needs third-party login or SSO, swap this out,
but nothing else in the codebase needs to change since everything else
just calls hash_password/verify_password/create_token/decode_token.
"""

import base64
import hashlib
import hmac
import json
import os
import secrets
import time

# PBKDF2 params - 260k iterations is OWASP's current minimum recommendation
# for SHA256-based PBKDF2 (2023 guidance), fine for a login form this size
_PBKDF2_ITERATIONS = 260_000
_SALT_BYTES = 16

# Tokens are signed with this key so they can't be forged client-side.
# Falls back to a per-process random key in dev so nothing crashes if the
# .env var is missing, but that means logins won't survive a server
# restart - set SECRET_KEY in .env for anything beyond local testing.
SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_hex(32)
TOKEN_TTL_SECONDS = 60 * 60 * 24 * 7  # 7 days


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(_SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${_PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt_hex, digest_hex = stored_hash.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
    except (ValueError, AttributeError):
        return False

    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iterations))
    # constant-time compare - a plain == here would leak timing info about
    # how many leading bytes matched, letting an attacker guess the hash
    return hmac.compare_digest(candidate, expected)


def _sign(payload_b64: str) -> str:
    signature = hmac.new(SECRET_KEY.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(signature).decode("utf-8").rstrip("=")


def create_token(user_id: int) -> str:
    payload = {"user_id": user_id, "exp": int(time.time()) + TOKEN_TTL_SECONDS}
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8").rstrip("=")
    signature = _sign(payload_b64)
    return f"{payload_b64}.{signature}"


def decode_token(token: str) -> int | None:
    """Returns the user_id encoded in the token, or None if the token is
    missing, malformed, has been tampered with, or has expired.
    """
    try:
        payload_b64, signature = token.split(".")
    except ValueError:
        return None

    expected_signature = _sign(payload_b64)
    if not hmac.compare_digest(signature, expected_signature):
        return None

    try:
        padded = payload_b64 + "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded))
    except (ValueError, json.JSONDecodeError):
        return None

    if payload.get("exp", 0) < time.time():
        return None

    return payload.get("user_id")
