"""Login sessions: access JWT (short-lived) + rotating opaque refresh token.

Both are delivered as httpOnly cookies. Every access token carries the session
id (sid); the session must still be active, so logout/revocation is immediate.
"""
from datetime import timedelta
from typing import Optional, Tuple

from fastapi import Request, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.rate_limit import client_ip
from app.core.security import create_access_token, generate_refresh_token, hash_token
from app.db.types import utcnow
from app.models.auth_session import AuthSession
from app.models.user import User


def create_session(db: Session, user: User, request: Request) -> Tuple[str, str]:
    refresh = generate_refresh_token()
    session = AuthSession(
        user_id=user.id,
        refresh_token_hash=hash_token(refresh),
        expires_at=utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        user_agent=(request.headers.get("user-agent") or "")[:255],
        ip_address=client_ip(request)[:64],
    )
    db.add(session)
    db.commit()
    return create_access_token(user.id, user.role, session.id), refresh


def get_active_session_by_refresh(db: Session, refresh_token: str) -> Optional[AuthSession]:
    session = (
        db.query(AuthSession)
        .filter(AuthSession.refresh_token_hash == hash_token(refresh_token))
        .first()
    )
    if session is None or session.revoked_at is not None or utcnow() >= session.expires_at:
        return None
    return session


def rotate_session(db: Session, session: AuthSession, user: User) -> Tuple[str, str]:
    refresh = generate_refresh_token()
    session.refresh_token_hash = hash_token(refresh)
    session.last_used_at = utcnow()
    db.commit()
    return create_access_token(user.id, user.role, session.id), refresh


def revoke_session(db: Session, session: AuthSession) -> None:
    if session.revoked_at is None:
        session.revoked_at = utcnow()
        db.commit()


def revoke_all_sessions(db: Session, user_id: str) -> None:
    db.query(AuthSession).filter(
        AuthSession.user_id == user_id, AuthSession.revoked_at.is_(None)
    ).update({AuthSession.revoked_at: utcnow()}, synchronize_session=False)
    db.commit()


def is_session_active(db: Session, session_id: str, user_id: str) -> bool:
    session = db.get(AuthSession, session_id)
    return (
        session is not None
        and session.user_id == user_id
        and session.revoked_at is None
        and utcnow() < session.expires_at
    )


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    common = dict(
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
        path="/",
    )
    response.set_cookie(
        settings.ACCESS_COOKIE_NAME, access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, **common,
    )
    response.set_cookie(
        settings.REFRESH_COOKIE_NAME, refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400, **common,
    )


def clear_auth_cookies(response: Response) -> None:
    for name in (settings.ACCESS_COOKIE_NAME, settings.REFRESH_COOKIE_NAME):
        response.delete_cookie(
            name, path="/", domain=settings.COOKIE_DOMAIN,
            secure=settings.COOKIE_SECURE, httponly=True, samesite=settings.COOKIE_SAMESITE,
        )
