from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.email_domains import get_consumer_domains
from app.core.errors import ApiError, ok
from app.core.rate_limit import client_ip, limiter
from app.core.security import (
    TokenExpired,
    TokenInvalid,
    burn_password_check,
    create_password_reset_token,
    decode_jwt,
    hash_password,
    verify_password,
)
from app.models.candidate_profile import CandidateProfile
from app.models.company_profile import CompanyProfile
from app.models.otp_verification import OtpPurpose, OtpVerification
from app.models.user import User, UserRole
from app.schemas.auth import (
    CandidateRegisterRequest,
    CompanyRegisterRequest,
    ForgotPasswordRequest,
    LoginRequest,
    ResendOtpRequest,
    ResetPasswordRequest,
    VerifyOtpRequest,
)
from app.schemas.validators import PASSWORD_MIN_LENGTH, PASSWORD_RULES
from app.services import otp_service, session_service
from app.services.email_service import send_otp_email
from app.services.profile_service import session_payload

router = APIRouter(prefix="/auth", tags=["Auth"])

ROLE_LABEL = {UserRole.CANDIDATE.value: "candidate", UserRole.COMPANY.value: "company"}


def _ip_limit(request: Request, bucket: str, limit: int, window: int) -> None:
    limiter.check_and_hit(
        f"ip:{bucket}:{client_ip(request)}", limit, window,
        "Too many requests. Please slow down and try again shortly.",
    )


def _send_code(db: Session, background: BackgroundTasks, email: str, purpose: str) -> None:
    otp = otp_service.create_otp(db, email, purpose)
    background.add_task(send_otp_email, email, otp, purpose)


def _start_session(db: Session, request: Request, response: Response, user: User) -> dict:
    access, refresh = session_service.create_session(db, user, request)
    session_service.set_auth_cookies(response, access, refresh)
    return session_payload(db, user)


# --------------------------------------------------------------------------
# Policy (consumed by the UI for live validation; backend remains authoritative)
# --------------------------------------------------------------------------
@router.get("/policy")
def auth_policy():
    return ok("Auth policy", {
        "password": {"min_length": PASSWORD_MIN_LENGTH, "rules": PASSWORD_RULES},
        "otp": {
            "length": settings.OTP_LENGTH,
            "expires_in_seconds": settings.OTP_EXPIRE_MINUTES * 60,
            "resend_cooldown_seconds": settings.OTP_RESEND_COOLDOWN_SECONDS,
            "max_attempts": settings.OTP_MAX_ATTEMPTS,
        },
        "consumer_email_domains": sorted(get_consumer_domains()),
    })


# --------------------------------------------------------------------------
# Registration
# --------------------------------------------------------------------------
def _register(
    db: Session,
    request: Request,
    background: BackgroundTasks,
    role: UserRole,
    name: str,
    email: str,
    password: str,
):
    _ip_limit(request, "register", limit=10, window=3600)

    existing = db.query(User).filter(User.email == email).first()
    if existing is not None:
        if existing.email_verified:
            raise ApiError(
                409, "An account with this email already exists. Try signing in.",
                "EMAIL_TAKEN", errors={"email": "An account with this email already exists"},
            )
        # Unverified accounts are not owned yet: replace with the new registration.
        db.delete(existing)
        db.flush()

    user = User(
        name=name, email=email, password_hash=hash_password(password),
        role=role.value, email_verified=False,
    )
    db.add(user)
    db.flush()
    if role == UserRole.CANDIDATE:
        db.add(CandidateProfile(user_id=user.id, skills=[], education=[], experience=[]))
    else:
        db.add(CompanyProfile(user_id=user.id, company_name=name, business_email=email))
    db.commit()

    purpose = OtpPurpose.EMAIL_VERIFICATION.value
    try:
        otp_service.enforce_send_limits(email, purpose)
        _send_code(db, background, email, purpose)
    except ApiError as exc:
        # A code was sent moments ago; it stays valid. Don't fail registration.
        if exc.status_code != 429:
            raise

    return ok("Verification code sent to your email.", {
        "email": email,
        "purpose": purpose,
        "resend_in": otp_service.cooldown_remaining(email, purpose),
    })


@router.post("/candidate/register", status_code=201)
def register_candidate(
    payload: CandidateRegisterRequest, request: Request,
    background: BackgroundTasks, db: Session = Depends(get_db),
):
    return _register(db, request, background, UserRole.CANDIDATE,
                     payload.name, payload.email, payload.password)


@router.post("/company/register", status_code=201)
def register_company(
    payload: CompanyRegisterRequest, request: Request,
    background: BackgroundTasks, db: Session = Depends(get_db),
):
    return _register(db, request, background, UserRole.COMPANY,
                     payload.company_name, payload.email, payload.password)


# --------------------------------------------------------------------------
# OTP
# --------------------------------------------------------------------------
@router.post("/verify-otp")
def verify_otp(
    payload: VerifyOtpRequest, request: Request, response: Response,
    db: Session = Depends(get_db),
):
    _ip_limit(request, "verify-otp", limit=30, window=600)
    record = otp_service.verify_otp(db, payload.email, payload.purpose, payload.otp)

    user = db.query(User).filter(User.email == payload.email).first()
    if user is None:
        raise ApiError(400, "Invalid or expired code. Request a new one.", "OTP_INVALID")

    if payload.purpose == OtpPurpose.EMAIL_VERIFICATION.value:
        user.email_verified = True
        db.commit()
        data = _start_session(db, request, response, user)
        return ok("Email verified successfully.", {"user": data})

    # PASSWORD_RESET: hand back a short-lived, single-use reset token.
    token = create_password_reset_token(user.id, record.id)
    return ok("Code verified. Create a new password.", {
        "reset_token": token,
        "expires_in": settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES * 60,
    })


@router.post("/resend-otp")
def resend_otp(
    payload: ResendOtpRequest, request: Request,
    background: BackgroundTasks, db: Session = Depends(get_db),
):
    _ip_limit(request, "resend-otp", limit=20, window=3600)
    otp_service.enforce_send_limits(payload.email, payload.purpose)

    user = db.query(User).filter(User.email == payload.email).first()
    should_send = user is not None and (
        payload.purpose == OtpPurpose.PASSWORD_RESET.value or not user.email_verified
    )
    if should_send:
        _send_code(db, background, payload.email, payload.purpose)

    return ok("A new code has been sent.", {
        "resend_in": otp_service.cooldown_remaining(payload.email, payload.purpose),
    })


# --------------------------------------------------------------------------
# Login / session
# --------------------------------------------------------------------------
@router.post("/login")
def login(
    payload: LoginRequest, request: Request, response: Response,
    background: BackgroundTasks, db: Session = Depends(get_db),
):
    _ip_limit(request, "login", settings.LOGIN_MAX_ATTEMPTS_PER_IP, settings.LOGIN_IP_WINDOW_SECONDS)

    fail_key = f"login:fail:{payload.email}"
    window = settings.LOGIN_FAILURE_WINDOW_SECONDS
    if limiter.count(fail_key, window) >= settings.LOGIN_MAX_FAILURES_PER_EMAIL:
        wait = limiter.retry_after(fail_key, window)
        minutes = max(1, (wait + 59) // 60)
        raise ApiError(
            429, f"Too many failed sign-in attempts. Try again in {minutes} minute{'s' if minutes > 1 else ''}.",
            "LOGIN_LOCKED", headers={"Retry-After": str(wait)},
        )

    user = db.query(User).filter(User.email == payload.email).first()
    if user is None:
        burn_password_check(payload.password)
        limiter.hit(fail_key)
        raise ApiError(401, "Incorrect email or password.", "INVALID_CREDENTIALS")

    if not verify_password(payload.password, user.password_hash):
        limiter.hit(fail_key)
        raise ApiError(401, "Incorrect email or password.", "INVALID_CREDENTIALS")

    # Only revealed after the correct password, so no account enumeration.
    if user.role != payload.role:
        actual = ROLE_LABEL[user.role]
        raise ApiError(
            403, f"This is a {actual} account. Switch to {actual} sign-in to continue.",
            "ROLE_MISMATCH", errors={"role": user.role},
        )

    if not user.email_verified:
        purpose = OtpPurpose.EMAIL_VERIFICATION.value
        try:
            otp_service.enforce_send_limits(user.email, purpose)
            _send_code(db, background, user.email, purpose)
        except ApiError as exc:
            if exc.status_code != 429:
                raise
        raise ApiError(
            403, "Please verify your email to continue. We've sent you a code.",
            "EMAIL_NOT_VERIFIED", errors={"email": user.email},
        )

    limiter.reset(fail_key)
    data = _start_session(db, request, response, user)
    return ok("Signed in successfully.", {"user": data})


@router.post("/refresh")
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    _ip_limit(request, "refresh", limit=120, window=300)
    token = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    session = session_service.get_active_session_by_refresh(db, token) if token else None
    user = db.get(User, session.user_id) if session else None
    if session is None or user is None or not user.email_verified:
        expired = JSONResponse(status_code=401, content={
            "success": False, "code": "SESSION_EXPIRED", "errors": {},
            "message": "Your session has expired. Please sign in again.",
        })
        session_service.clear_auth_cookies(expired)
        return expired

    access, new_refresh = session_service.rotate_session(db, session, user)
    session_service.set_auth_cookies(response, access, new_refresh)
    return ok("Session refreshed.", {"user": session_payload(db, user)})


@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if token:
        session = session_service.get_active_session_by_refresh(db, token)
        if session:
            session_service.revoke_session(db, session)
    session_service.clear_auth_cookies(response)
    return ok("Signed out successfully.")


@router.get("/me")
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ok("Current user", {"user": session_payload(db, user)})


# --------------------------------------------------------------------------
# Password reset
# --------------------------------------------------------------------------
@router.post("/forgot-password")
def forgot_password(
    payload: ForgotPasswordRequest, request: Request,
    background: BackgroundTasks, db: Session = Depends(get_db),
):
    _ip_limit(request, "forgot-password", limit=10, window=3600)
    purpose = OtpPurpose.PASSWORD_RESET.value
    otp_service.enforce_send_limits(payload.email, purpose)

    user = db.query(User).filter(User.email == payload.email).first()
    if user is not None:
        _send_code(db, background, payload.email, purpose)

    # Identical response whether or not the account exists.
    return ok("If an account exists for this email, we've sent a reset code.", {
        "email": payload.email,
        "resend_in": otp_service.cooldown_remaining(payload.email, purpose),
    })


@router.post("/reset-password")
def reset_password(
    payload: ResetPasswordRequest, request: Request, response: Response,
    db: Session = Depends(get_db),
):
    _ip_limit(request, "reset-password", limit=10, window=600)
    try:
        claims = decode_jwt(payload.reset_token, "password_reset")
    except TokenExpired:
        raise ApiError(400, "Your reset session expired. Please request a new code.", "RESET_EXPIRED")
    except TokenInvalid:
        raise ApiError(400, "Invalid reset session. Please request a new code.", "RESET_INVALID")

    user = db.get(User, claims.get("sub"))
    record = db.get(OtpVerification, claims.get("oid"))
    if (
        user is None or record is None or not record.verified
        or record.purpose != OtpPurpose.PASSWORD_RESET.value or record.email != user.email
    ):
        raise ApiError(400, "This reset link was already used or is invalid. Please request a new code.",
                       "RESET_INVALID")

    if verify_password(payload.new_password, user.password_hash):
        raise ApiError(422, "New password must be different from your current password.",
                       "PASSWORD_REUSED", errors={"new_password": "Choose a different password"})

    user.password_hash = hash_password(payload.new_password)
    user.email_verified = True  # inbox ownership was just proven
    db.query(OtpVerification).filter(
        OtpVerification.email == user.email,
        OtpVerification.purpose == OtpPurpose.PASSWORD_RESET.value,
    ).delete(synchronize_session=False)
    db.commit()

    session_service.revoke_all_sessions(db, user.id)
    session_service.clear_auth_cookies(response)
    limiter.reset(f"login:fail:{user.email}")
    return ok("Password updated. Sign in with your new password.", {"role": user.role})
