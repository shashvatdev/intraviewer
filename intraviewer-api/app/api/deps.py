"""Authorization dependencies.

Backend verifies: authenticated user + active session + account type (role).
The role is read from the database, never from client input.
"""
from typing import Optional

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.errors import ApiError
from app.core.security import TokenExpired, TokenInvalid, decode_jwt
from app.models.user import User, UserRole
from app.services.session_service import is_session_active


def _extract_access_token(request: Request) -> Optional[str]:
    auth = request.headers.get("authorization")
    if auth and auth.lower().startswith("bearer "):
        return auth[7:].strip() or None
    return request.cookies.get(settings.ACCESS_COOKIE_NAME)


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = _extract_access_token(request)
    if not token:
        raise ApiError(401, "Please sign in to continue.", "UNAUTHENTICATED")
    try:
        payload = decode_jwt(token, "access")
    except TokenExpired:
        raise ApiError(401, "Your session has expired.", "TOKEN_EXPIRED")
    except TokenInvalid:
        raise ApiError(401, "Please sign in to continue.", "UNAUTHENTICATED")

    user_id, session_id = payload.get("sub"), payload.get("sid")
    if not user_id or not session_id or not is_session_active(db, session_id, user_id):
        raise ApiError(401, "Your session has ended. Please sign in again.", "SESSION_REVOKED")

    user = db.get(User, user_id)
    if user is None or not user.email_verified:
        raise ApiError(401, "Please sign in to continue.", "UNAUTHENTICATED")

    request.state.session_id = session_id
    return user


def require_role(role: UserRole):
    def _dep(user: User = Depends(get_current_user)) -> User:
        if user.role != role.value:
            raise ApiError(403, "You don't have access to this resource.", "FORBIDDEN")
        return user

    return _dep


require_candidate = require_role(UserRole.CANDIDATE)
require_company = require_role(UserRole.COMPANY)
