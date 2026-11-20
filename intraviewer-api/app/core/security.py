"""Cryptographic primitives: password hashing, OTP hashing, tokens."""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import bcrypt
from jose import ExpiredSignatureError, JWTError, jwt

from app.core.config import settings

BCRYPT_ROUNDS = 12
# bcrypt only uses the first 72 bytes; we reject longer passwords at validation.
BCRYPT_MAX_BYTES = 72

# Pre-computed hash used to equalize timing when a user does not exist.
_DUMMY_HASH = bcrypt.hashpw(b"timing-equalizer-password", bcrypt.gensalt(BCRYPT_ROUNDS))


# --- Passwords ---------------------------------------------------------------

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(BCRYPT_ROUNDS)).decode("utf-8")


def verify_password(password: str, password_hash: Optional[str]) -> bool:
    pw = password.encode("utf-8")
    if len(pw) > BCRYPT_MAX_BYTES:
        return False
    if not password_hash:
        bcrypt.checkpw(pw, _DUMMY_HASH)
        return False
    try:
        return bcrypt.checkpw(pw, password_hash.encode("utf-8"))
    except ValueError:
        return False


def burn_password_check(password: str) -> None:
    """Run a bcrypt check against a dummy hash (anti user-enumeration timing)."""
    pw = password.encode("utf-8")[:BCRYPT_MAX_BYTES]
    bcrypt.checkpw(pw, _DUMMY_HASH)


# --- OTP ---------------------------------------------------------------------

def generate_otp(length: Optional[int] = None) -> str:
    n = length or settings.OTP_LENGTH
    return "".join(str(secrets.randbelow(10)) for _ in range(n))


def hash_otp(email: str, purpose: str, otp: str) -> str:
    """Keyed HMAC-SHA256 bound to email + purpose. Raw OTP is never stored."""
    msg = f"{email.lower()}|{purpose}|{otp}".encode("utf-8")
    return hmac.new(settings.SECRET_KEY.encode("utf-8"), msg, hashlib.sha256).hexdigest()


def verify_otp_hash(email: str, purpose: str, otp: str, otp_hash: str) -> bool:
    return hmac.compare_digest(hash_otp(email, purpose, otp), otp_hash)


# --- Opaque refresh tokens ---------------------------------------------------

def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


# --- JWT ---------------------------------------------------------------------

class TokenExpired(Exception):
    pass


class TokenInvalid(Exception):
    pass


def _encode(payload: Dict[str, Any], expires_in: timedelta) -> str:
    now = datetime.now(timezone.utc)
    body = {**payload, "iat": int(now.timestamp()), "exp": int((now + expires_in).timestamp())}
    return jwt.encode(body, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_jwt(token: str, expected_type: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except ExpiredSignatureError as exc:
        raise TokenExpired() from exc
    except JWTError as exc:
        raise TokenInvalid() from exc
    if payload.get("type") != expected_type:
        raise TokenInvalid()
    return payload


def create_access_token(user_id: str, role: str, session_id: str) -> str:
    return _encode(
        {"sub": user_id, "role": role, "sid": session_id, "type": "access"},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_password_reset_token(user_id: str, otp_id: str) -> str:
    return _encode(
        {"sub": user_id, "oid": otp_id, "type": "password_reset"},
        timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES),
    )
