"""Transactional email.

If SMTP_HOST is not configured (local dev), emails are printed to the API
console instead of being sent, so the full OTP flow is testable offline.
"""
import logging
import smtplib
import ssl
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger("intraviewer.email")

_SUBJECTS = {
    "EMAIL_VERIFICATION": "Your Intraviewer verification code",
    "PASSWORD_RESET": "Your Intraviewer password reset code",
}

_INTROS = {
    "EMAIL_VERIFICATION": "Use this code to verify your email address.",
    "PASSWORD_RESET": "Use this code to reset your password.",
}


def _render(otp: str, purpose: str):
    intro = _INTROS.get(purpose, "Your verification code:")
    minutes = settings.OTP_EXPIRE_MINUTES
    text = (
        f"{intro}\n\n{otp}\n\nThis code expires in {minutes} minutes.\n"
        "If you didn't request this, you can safely ignore this email."
    )
    html = f"""\
<div style="font-family:Inter,Segoe UI,Arial,sans-serif;background:#FAF9F6;padding:32px">
  <div style="max-width:480px;margin:0 auto;background:#fff;border:1px solid #E7E3DC;padding:32px">
    <div style="font-weight:700;font-size:15px;letter-spacing:-0.01em;color:#0B0B0C">
      <span style="display:inline-block;width:10px;height:10px;background:#F55036;margin-right:8px"></span>Intraviewer
    </div>
    <p style="color:#57534E;font-size:14px;margin:28px 0 12px">{intro}</p>
    <div style="font-family:'JetBrains Mono',Menlo,monospace;font-size:32px;letter-spacing:10px;font-weight:700;color:#0B0B0C;padding:16px 0">{otp}</div>
    <p style="color:#8A847C;font-size:12px;margin-top:16px">This code expires in {minutes} minutes. If you didn't request it, ignore this email.</p>
  </div>
</div>"""
    return text, html


def send_otp_email(to_email: str, otp: str, purpose: str) -> None:
    subject = _SUBJECTS.get(purpose, "Your Intraviewer code")
    text, html = _render(otp, purpose)

    if not settings.SMTP_HOST:
        banner = "=" * 60
        print(
            f"\n{banner}\n[DEV EMAIL] to={to_email} purpose={purpose}\n"
            f"[DEV EMAIL] subject={subject}\n[DEV EMAIL] OTP CODE: {otp}\n{banner}\n",
            flush=True,
        )
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to_email
    msg.set_content(text)
    msg.add_alternative(html, subtype="html")

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            if settings.SMTP_USE_TLS:
                server.starttls(context=ssl.create_default_context())
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
    except Exception:  # pragma: no cover - network dependent
        logger.exception("Failed to send %s email to %s", purpose, to_email)
