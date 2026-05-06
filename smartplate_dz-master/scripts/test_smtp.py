"""
Standalone SMTP smoke-test.

Loads your .env, attempts to send a single email to the recipient passed
on the command line, and prints exactly what went wrong if it fails.

Usage (from inside smartplate_auth/):
    python scripts/test_smtp.py ahlam.akacha45@gmail.com
"""
from __future__ import annotations

import asyncio
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
import dotenv

dotenv.load_dotenv()

import os

HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
PORT = int(os.getenv("SMTP_PORT", "587"))
USER = os.getenv("SMTP_USERNAME", "")
PWD = os.getenv("SMTP_PASSWORD", "")
FROM_NAME = os.getenv("EMAILS_FROM_NAME", "SmartPlate")
FROM_EMAIL = os.getenv("EMAILS_FROM_EMAIL", "")


async def main(to: str) -> None:
    print(f"\n=== SMTP test ===")
    print(f"  HOST      = {HOST}")
    print(f"  PORT      = {PORT}")
    print(f"  USERNAME  = {USER!r}")
    print(f"  PASSWORD  = {'***' + PWD[-4:] if PWD else '<empty>'} (len={len(PWD)})")
    print(f"  FROM      = {FROM_NAME} <{FROM_EMAIL}>")
    print(f"  TO        = {to}\n")

    if not (USER and PWD and FROM_EMAIL):
        print("FAIL: SMTP_USERNAME / SMTP_PASSWORD / EMAILS_FROM_EMAIL must all be set in .env")
        sys.exit(2)

    # Gmail App Passwords are 16 chars (often shown as 4×4 with spaces).
    # Extra spaces in the env value will cause auth to fail.
    if " " in PWD:
        print("WARNING: SMTP_PASSWORD contains spaces. Gmail shows App Passwords")
        print("         as 'xxxx xxxx xxxx xxxx' for readability, but you should")
        print("         enter it WITHOUT the spaces. Strip them and try again.\n")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "SmartPlate SMTP test"
    msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"] = to
    msg.attach(MIMEText(
        "<h2>It works!</h2><p>If you can read this, your Gmail SMTP credentials are correct.</p>",
        "html",
    ))

    try:
        await aiosmtplib.send(
            msg,
            hostname=HOST,
            port=PORT,
            username=USER,
            password=PWD,
            start_tls=True,
        )
    except aiosmtplib.SMTPAuthenticationError as e:
        print(f"FAIL: SMTP authentication rejected by Gmail.")
        print(f"      Code={e.code}  Message={e.message!r}")
        print()
        print("Most common causes:")
        print("  • SMTP_PASSWORD is your Gmail account password — it must be a 16-char")
        print("    App Password from https://myaccount.google.com/apppasswords")
        print("  • 2-Step Verification is OFF on the Gmail account (App Passwords")
        print("    only work when 2-Step Verification is enabled)")
        print("  • You typed the App Password with the spaces Gmail displays")
        sys.exit(3)
    except (TimeoutError, ConnectionRefusedError, OSError) as e:
        print(f"FAIL: Network error connecting to {HOST}:{PORT}")
        print(f"      {type(e).__name__}: {e}")
        print()
        print("Most common causes:")
        print("  • Firewall / corporate network blocking outbound port 587")
        print("  • SMTP_HOST or SMTP_PORT typo in .env")
        sys.exit(4)
    except Exception as e:
        print(f"FAIL: {type(e).__name__}: {e}")
        sys.exit(5)

    print(f"OK — message accepted by {HOST}. Check your inbox (and spam folder).")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/test_smtp.py recipient@gmail.com")
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))
