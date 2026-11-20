"""Reusable field validators/normalizers shared by request schemas."""
import re
from typing import Iterable, Optional
from urllib.parse import urlparse

from app.core.security import BCRYPT_MAX_BYTES

PASSWORD_MIN_LENGTH = 8

PASSWORD_RULES = [
    {"key": "length", "label": f"At least {PASSWORD_MIN_LENGTH} characters"},
    {"key": "upper", "label": "One uppercase letter"},
    {"key": "lower", "label": "One lowercase letter"},
    {"key": "number", "label": "One number"},
]


def normalize_email(value: str) -> str:
    return value.strip().lower()


def clean_name(value: str, field_label: str = "Name", min_len: int = 2, max_len: int = 100) -> str:
    v = re.sub(r"\s+", " ", (value or "")).strip()
    if len(v) < min_len:
        raise ValueError(f"{field_label} must be at least {min_len} characters")
    if len(v) > max_len:
        raise ValueError(f"{field_label} must be at most {max_len} characters")
    return v


def validate_password_strength(value: str) -> str:
    if len(value) < PASSWORD_MIN_LENGTH:
        raise ValueError(f"Password must be at least {PASSWORD_MIN_LENGTH} characters")
    if len(value.encode("utf-8")) > BCRYPT_MAX_BYTES:
        raise ValueError(f"Password must be at most {BCRYPT_MAX_BYTES} characters")
    if not re.search(r"[A-Z]", value):
        raise ValueError("Password must include an uppercase letter")
    if not re.search(r"[a-z]", value):
        raise ValueError("Password must include a lowercase letter")
    if not re.search(r"[0-9]", value):
        raise ValueError("Password must include a number")
    return value


def optional_text(value: Optional[str], max_len: int, label: str) -> Optional[str]:
    if value is None:
        return None
    v = value.strip()
    if not v:
        return None
    if len(v) > max_len:
        raise ValueError(f"{label} must be at most {max_len} characters")
    return v


_PHONE_RE = re.compile(r"^\+?[0-9][0-9\s\-().]{5,24}$")


def normalize_phone(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    v = value.strip()
    if not v:
        return None
    digits = re.sub(r"\D", "", v)
    if not _PHONE_RE.match(v) or not (7 <= len(digits) <= 15):
        raise ValueError("Enter a valid phone number")
    return re.sub(r"\s+", " ", v)


def normalize_url(
    value: Optional[str],
    label: str = "URL",
    allowed_hosts: Optional[Iterable[str]] = None,
) -> Optional[str]:
    if value is None:
        return None
    v = value.strip()
    if not v:
        return None
    if len(v) > 500:
        raise ValueError(f"{label} is too long")
    if not re.match(r"^https?://", v, re.IGNORECASE):
        v = "https://" + v
    parsed = urlparse(v)
    host = (parsed.hostname or "").lower()
    if parsed.scheme not in ("http", "https") or "." not in host or " " in v:
        raise ValueError(f"Enter a valid {label} (e.g. https://example.com)")
    if allowed_hosts:
        hosts = list(allowed_hosts)
        if not any(host == h or host.endswith("." + h) for h in hosts):
            raise ValueError(f"{label} must be a {hosts[0]} link")
    return v
