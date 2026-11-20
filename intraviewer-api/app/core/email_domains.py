"""Consumer (free/personal) email providers.

Company accounts must register with a business/work email for the MVP. This is
ONLY a business-email requirement, not legal company verification.

Extend the list without code changes via EXTRA_CONSUMER_EMAIL_DOMAINS in .env
(comma separated).
"""
from typing import FrozenSet

from app.core.config import settings

_BASE_CONSUMER_DOMAINS = {
    # Google
    "gmail.com", "googlemail.com",
    # Microsoft
    "outlook.com", "outlook.in", "hotmail.com", "hotmail.co.uk", "hotmail.in",
    "live.com", "live.in", "msn.com",
    # Yahoo / AOL
    "yahoo.com", "yahoo.co.in", "yahoo.in", "yahoo.co.uk", "ymail.com",
    "rocketmail.com", "aol.com",
    # Apple
    "icloud.com", "me.com", "mac.com",
    # Privacy / misc consumer providers
    "proton.me", "protonmail.com", "pm.me", "tutanota.com", "tuta.io",
    "zoho.com", "zohomail.com", "zohomail.in", "mail.com", "gmx.com", "gmx.net",
    "yandex.com", "yandex.ru", "rediffmail.com", "inbox.com", "hey.com",
    "fastmail.com",
    # Common disposable providers
    "mailinator.com", "guerrillamail.com", "10minutemail.com", "tempmail.com",
    "temp-mail.org", "yopmail.com", "sharklasers.com", "trashmail.com",
}


def get_consumer_domains() -> FrozenSet[str]:
    extra = {
        d.strip().lower()
        for d in settings.EXTRA_CONSUMER_EMAIL_DOMAINS.split(",")
        if d.strip()
    }
    return frozenset(_BASE_CONSUMER_DOMAINS | extra)


def email_domain(email: str) -> str:
    return email.rsplit("@", 1)[-1].lower()


def is_consumer_email(email: str) -> bool:
    return email_domain(email) in get_consumer_domains()
