"""
Async email service used by the auth flow.

Failures are logged but never raised — we don't want a transient SMTP
outage to roll back a signup. The OTP record is still in the DB, so the
user can request a resend.
"""
from __future__ import annotations

import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


async def _send(to: str, subject: str, html_body: str) -> None:
    smtp_configured = bool(
        settings.SMTP_USERNAME and settings.SMTP_PASSWORD and settings.EMAILS_FROM_EMAIL
    )

    # Belt-and-suspenders: print directly to stdout so output is visible
    # even if the application logger is being swallowed by uvicorn's config.
    print(
        f"[email_service] _send called: to={to!r} subject={subject!r} "
        f"smtp_configured={smtp_configured} env={settings.APP_ENV}",
        flush=True,
    )

    # Dev-mode convenience: also log the OTP to stdout so you can test
    # without reaching for your inbox. This NEVER replaces the real send —
    # if SMTP is configured we still attempt delivery below.
    if not settings.is_production:
        import re
        code_match = re.search(r"(\d{6})", html_body)
        if code_match:
            otp = code_match.group(1)
            logger.info("🔔 DEV — OTP for %s: %s", to, otp)
            print(f"[email_service] 🔔 DEV — OTP for {to}: {otp}", flush=True)

    if not smtp_configured:
        # When SMTP is not yet configured, extract the OTP from the HTML body
        # and print it directly to stdout so it is visible in Render / server logs.
        # This allows testing the auth flow without a real email server.
        import re
        code_match = re.search(r"\b(\d{6})\b", html_body)
        otp_hint = f" | ⚠️  OTP CODE → {code_match.group(1)}" if code_match else ""
        logger.warning(
            "SMTP not configured — email NOT sent to %s%s",
            to, otp_hint,
        )
        print(
            f"[email_service] ⚠️  SMTP NOT CONFIGURED\n"
            f"[email_service]    TO      : {to}\n"
            f"[email_service]    SUBJECT : {subject}\n"
            f"[email_service]    {otp_hint.strip()}\n"
            f"[email_service] → Set SMTP_USERNAME, SMTP_PASSWORD, EMAILS_FROM_EMAIL in Render dashboard.",
            flush=True,
        )
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    msg["To"] = to
    msg.attach(MIMEText(html_body, "html"))

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
        logger.info("Email sent to %s | subject: %s", to, subject)
        print(f"[email_service] OK — sent to {to}", flush=True)
    except Exception as exc:  # pragma: no cover - SMTP failures are logged
        logger.error(
            "Failed to send email to %s: %s: %s — check SMTP_HOST/PORT and "
            "that SMTP_PASSWORD is a Gmail App Password (not your account password).",
            to, type(exc).__name__, exc,
        )
        print(
            f"[email_service] FAIL — {type(exc).__name__}: {exc}\n"
            f"[email_service] HOST={settings.SMTP_HOST}:{settings.SMTP_PORT} "
            f"USER={settings.SMTP_USERNAME!r} "
            f"PWD_LEN={len(settings.SMTP_PASSWORD)} "
            f"FROM={settings.EMAILS_FROM_EMAIL!r}",
            flush=True,
        )


# ─── HTML templates ─────────────────────────────────────────────────────────


def _otp_email_html(*, full_name: str, code: str, headline: str, accent: str = "#3b82f6", code_color: str = "#60a5fa") -> str:
    return f"""
    <html><body style="font-family:Arial,sans-serif;background:#0d1b3e;color:#fff;padding:40px">
      <div style="max-width:520px;margin:auto;background:#132147;border-radius:12px;padding:36px">
        <h2 style="color:#fff;margin-bottom:4px">{headline}</h2>
        <p>Hi <strong>{full_name}</strong>,</p>
        <p>Use the code below to continue. It expires in
           <strong>{settings.OTP_EXPIRE_MINUTES} minutes</strong> and can only be used once.</p>

        <div style="background:#1e3a8a;border:2px solid {accent};border-radius:8px;padding:20px;margin:24px 0;text-align:center">
          <div style="font-size:36px;font-weight:bold;color:{code_color};letter-spacing:8px;margin:15px 0">
            {code}
          </div>
          <p style="color:#93c5fd;margin:10px 0 0 0;font-size:14px">
            Expires in {settings.OTP_EXPIRE_MINUTES} minutes
          </p>
        </div>

        <p style="font-size:12px;color:#aaa">
          For your security, never share this code with anyone — SmartPlate staff
          will never ask you for it.
        </p>
        <p style="font-size:12px;color:#aaa">
          If you did not request this, you can safely ignore this email.
        </p>
      </div>
    </body></html>
    """


# ─── Public senders ─────────────────────────────────────────────────────────


async def send_signup_otp_email(*, to: str, full_name: str, code: str) -> None:
    html = _otp_email_html(
        full_name=full_name,
        code=code,
        headline="Verify your SmartPlate email",
    )
    await _send(to, "Verify your SmartPlate email", html)


async def send_login_otp_email(*, to: str, full_name: str, code: str) -> None:
    html = _otp_email_html(
        full_name=full_name,
        code=code,
        headline="Your SmartPlate login code",
        accent="#10b981",
        code_color="#34d399",
    )
    await _send(to, "Your SmartPlate login code", html)


# Backwards-compatible alias kept so any other module that still imports the
# old name keeps working.
send_verification_email = send_signup_otp_email
