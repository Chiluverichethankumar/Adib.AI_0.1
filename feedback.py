# feedback.py
import os
import requests
import smtplib
from email.message import EmailMessage
from typing import Optional

# Read environment variables (works both locally and in live servers)
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
YOUR_EMAIL = os.getenv("YOUR_EMAIL")            # sender (used by both Resend and SMTP)
TO_EMAIL = os.getenv("FEEDBACK_TO_EMAIL")       # destination/receiver
YOUR_PASSWORD = os.getenv("YOUR_PASSWORD")      # only used for SMTP fallback

# Optional: configure an HTTP timeout for external API calls
HTTP_TIMEOUT = 10  # seconds

def _send_via_resend(name: str, email: str, message: str) -> bool:
    """Send using Resend API (recommended for live hosting)."""
    if not RESEND_API_KEY or not YOUR_EMAIL or not TO_EMAIL:
        print("Resend: missing RESEND_API_KEY, YOUR_EMAIL or FEEDBACK_TO_EMAIL")
        return False

    payload = {
        "from": f"Adib.AI <{YOUR_EMAIL}>",
        "to": [TO_EMAIL],
        "subject": f"Feedback from {name}",
        "text": f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
    }

    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(
            "https://api.resend.com/emails",
            headers=headers,
            json=payload,
            timeout=HTTP_TIMEOUT
        )
        # Log helpful info
        print("Resend: status_code=", resp.status_code)
        try:
            print("Resend: response_json=", resp.json())
        except Exception:
            print("Resend: response_text=", resp.text)

        return resp.status_code in (200, 201)
    except requests.exceptions.Timeout:
        print("Resend: request timed out")
        return False
    except Exception as e:
        print("Resend: exception sending feedback:", e)
        return False


def _send_via_smtp(name: str, email: str, message: str) -> bool:
    """Fallback SMTP (works locally if your environment allows SMTP)."""
    if not YOUR_EMAIL or not YOUR_PASSWORD or not TO_EMAIL:
        print("SMTP: missing YOUR_EMAIL, YOUR_PASSWORD, or FEEDBACK_TO_EMAIL")
        return False

    try:
        msg = EmailMessage()
        msg["Subject"] = f"Adib.AI Feedback from {name}"
        msg["From"] = YOUR_EMAIL
        msg["To"] = TO_EMAIL
        # set Reply-To so you can reply directly to user
        if email:
            msg["Reply-To"] = email
        msg.set_content(f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}")

        # Use SMTP_SSL with a short socket timeout
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=HTTP_TIMEOUT) as smtp:
            smtp.login(YOUR_EMAIL, YOUR_PASSWORD)
            smtp.send_message(msg)

        print("SMTP: email sent successfully.")
        return True
    except smtplib.SMTPAuthenticationError:
        print("SMTP: authentication failed - check YOUR_EMAIL and YOUR_PASSWORD (or app password).")
        return False
    except Exception as e:
        print("SMTP: exception sending email:", e)
        return False


def send_feedback(name: str, email: Optional[str], message: str) -> bool:
    """
    Tries Resend API first (recommended on hosts like Render). If RESEND_API_KEY is not configured,
    falls back to SMTP (useful for local dev).
    Returns True on success, False otherwise.
    """
    # debug prints to help you see what's available in the environment
    print(f"DEBUG: RESEND_API_KEY={'SET' if RESEND_API_KEY else 'MISSING'}")
    print(f"DEBUG: YOUR_EMAIL={'SET' if YOUR_EMAIL else 'MISSING'}")
    print(f"DEBUG: YOUR_PASSWORD={'SET' if YOUR_PASSWORD else 'MISSING'}")
    print(f"DEBUG: FEEDBACK_TO_EMAIL={'SET' if TO_EMAIL else 'MISSING'}")

    # Prefer API-based sending for hosted environments
    if RESEND_API_KEY:
        ok = _send_via_resend(name, email or "no-reply@example.com", message)
        if ok:
            return True
        else:
            print("Resend failed; attempting SMTP fallback if available...")

    # SMTP fallback for local development only
    return _send_via_smtp(name, email or "no-reply@example.com", message)
