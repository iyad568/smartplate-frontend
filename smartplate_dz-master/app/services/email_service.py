"""
Async email service used by the auth flow.

Priority:
  1. Resend HTTP API  — works on Render free tier (no SMTP port needed)
  2. SMTP / aiosmtplib — fallback if RESEND_API_KEY is not set

Failures are logged but never raised — we don't want a transient outage
to roll back a signup. The OTP record is still in the DB so the user can
request a resend. The OTP code is always printed to stdout as an emergency
fallback so it is visible in server logs.
"""
from __future__ import annotations

import re

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


def _extract_otp(html_body: str) -> str | None:
    m = re.search(r"\b(\d{6})\b", html_body)
    return m.group(1) if m else None


async def _send(to: str, subject: str, html_body: str) -> None:
    otp = _extract_otp(html_body)

    # Dev convenience: always log OTP to stdout
    if not settings.is_production and otp:
        logger.info("DEV — OTP for %s: %s", to, otp)
        print(f"[email_service] DEV — OTP for {to}: {otp}", flush=True)

    # ── 1. Try Resend (HTTP — works everywhere) ──────────────────────────────
    if settings.RESEND_API_KEY:
        from_addr = (
            f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
            if settings.EMAILS_FROM_EMAIL
            else f"{settings.EMAILS_FROM_NAME} <onboarding@resend.dev>"
        )
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={"from": from_addr, "to": [to], "subject": subject, "html": html_body},
                )
                resp.raise_for_status()
            logger.info("Resend: email sent to %s | subject: %s", to, subject)
            print(f"[email_service] OK (Resend) — sent to {to}", flush=True)
            return
        except Exception as exc:
            logger.error("Resend failed for %s: %s: %s", to, type(exc).__name__, exc)
            print(f"[email_service] Resend FAIL — {type(exc).__name__}: {exc}", flush=True)
            if otp:
                print(f"[email_service]    ⚠️  OTP CODE → {otp}", flush=True)
            return  # don't fall through to SMTP — it's blocked on Render anyway

    # ── 2. SMTP fallback ─────────────────────────────────────────────────────
    smtp_configured = bool(
        settings.SMTP_USERNAME and settings.SMTP_PASSWORD and settings.EMAILS_FROM_EMAIL
    )
    if not smtp_configured:
        logger.warning("No email provider configured — email NOT sent to %s", to)
        if otp:
            print(f"[email_service] ⚠️  NO EMAIL PROVIDER — OTP for {to}: {otp}", flush=True)
        print(
            "[email_service] → Set RESEND_API_KEY in the Render dashboard to enable email.",
            flush=True,
        )
        return

    import aiosmtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

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
        logger.info("SMTP: email sent to %s | subject: %s", to, subject)
        print(f"[email_service] OK (SMTP) — sent to {to}", flush=True)
    except Exception as exc:
        logger.error(
            "SMTP failed for %s: %s: %s",
            to, type(exc).__name__, exc,
        )
        print(f"[email_service] SMTP FAIL — {type(exc).__name__}: {exc}", flush=True)
        if otp:
            print(f"[email_service]    ⚠️  OTP CODE → {otp}", flush=True)


# ─── HTML templates ─────────────────────────────────────────────────────────


def _otp_email_html(
    *, full_name: str, code: str, headline: str,
    accent: str = "#3b82f6", code_color: str = "#60a5fa",
) -> str:
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


# Backwards-compatible alias
send_verification_email = send_signup_otp_email
