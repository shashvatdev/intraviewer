"""OTP issuing and verification.

- Raw OTPs are never persisted (keyed HMAC only).
- Each new OTP invalidates previous unverified ones for the same email+purpose.
- Send limits are applied per email regardless of whether an account exists,
  so responses don't leak account existence.
"""
from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import ApiError
from app.core.rate_limit import limiter
from app.core.security import generate_otp, hash_otp, verify_otp_hash
from app.db.types import utcnow
from app.models.otp_verification import OtpVerification


def _cooldown_key(email: str, purpose: str) -> str:
    return f"otp:cooldown:{purpose}:{email}"


def _hourly_key(email: str) -> str:
    return f"otp:hourly:{email}"


def cooldown_remaining(email: str, purpose: str) -> int:
    return limiter.retry_after(_cooldown_key(email, purpose), settings.OTP_RESEND_COOLDOWN_SECONDS)


def enforce_send_limits(email: str, purpose: str) -> None:
    """Raise 429 if a code was sent too recently or too many codes this hour."""
    wait = cooldown_remaining(email, purpose)
    if wait > 0:
        raise ApiError(
            429,
            f"Please wait {wait} seconds before requesting a new code.",
            "OTP_COOLDOWN",
            headers={"Retry-After": str(wait)},
        )
    hourly = _hourly_key(email)
    if limiter.count(hourly, 3600) >= settings.OTP_MAX_SENDS_PER_HOUR:
        wait = limiter.retry_after(hourly, 3600)
        raise ApiError(
            429,
            "Too many codes requested. Please try again later.",
            "OTP_RATE_LIMITED",
            headers={"Retry-After": str(wait)},
        )
    limiter.hit(_cooldown_key(email, purpose))
    limiter.hit(hourly)


def create_otp(db: Session, email: str, purpose: str) -> str:
    db.query(OtpVerification).filter(
        OtpVerification.email == email,
        OtpVerification.purpose == purpose,
        OtpVerification.verified.is_(False),
    ).delete(synchronize_session=False)

    otp = generate_otp()
    db.add(
        OtpVerification(
            email=email,
            otp_hash=hash_otp(email, purpose, otp),
            purpose=purpose,
            expires_at=utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
            attempts=0,
            verified=False,
        )
    )
    db.commit()
    return otp


def verify_otp(db: Session, email: str, purpose: str, otp: str) -> OtpVerification:
    record = (
        db.query(OtpVerification)
        .filter(
            OtpVerification.email == email,
            OtpVerification.purpose == purpose,
            OtpVerification.verified.is_(False),
        )
        .order_by(OtpVerification.created_at.desc())
        .first()
    )
    if record is None:
        raise ApiError(400, "Invalid or expired code. Request a new one.", "OTP_INVALID",
                       errors={"otp": "Invalid or expired code"})

    if utcnow() >= record.expires_at:
        raise ApiError(400, "This code has expired. Request a new one.", "OTP_EXPIRED",
                       errors={"otp": "Code expired"})

    if record.attempts >= settings.OTP_MAX_ATTEMPTS:
        raise ApiError(429, "Too many incorrect attempts. Request a new code.", "OTP_LOCKED",
                       errors={"otp": "Too many attempts"})

    if not verify_otp_hash(email, purpose, otp, record.otp_hash):
        record.attempts += 1
        db.commit()
        remaining = settings.OTP_MAX_ATTEMPTS - record.attempts
        if remaining <= 0:
            raise ApiError(429, "Too many incorrect attempts. Request a new code.", "OTP_LOCKED",
                           errors={"otp": "Too many attempts"})
        plural = "attempt" if remaining == 1 else "attempts"
        raise ApiError(400, f"Incorrect code. {remaining} {plural} remaining.", "OTP_INVALID",
                       errors={"otp": "Incorrect code"})

    record.verified = True
    db.commit()
    return record
