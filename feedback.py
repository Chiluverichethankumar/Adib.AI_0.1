import smtplib
import os
from email.message import EmailMessage

# Read environment variables (works both locally and in live servers)
YOUR_EMAIL = os.getenv("YOUR_EMAIL")
YOUR_PASSWORD = os.getenv("YOUR_PASSWORD")
TO_EMAIL = os.getenv("FEEDBACK_TO_EMAIL")

def send_feedback(name: str, email: str, message: str) -> bool:
    """
    Sends feedback email using SMTP.
    
    Args:
        name (str): Name of the sender
        email (str): Email of the sender
        message (str): Message content

    Returns:
        bool: True if email sent successfully, False otherwise
    """

    # Validate environment variables
    if not YOUR_EMAIL or not YOUR_PASSWORD or not TO_EMAIL:
        print("Error: Missing environment variables for email.")
        return False

    try:
        # Create email message
        msg = EmailMessage()
        msg["Subject"] = f"Adib.AI Feedback from {name}"
        msg["From"] = YOUR_EMAIL
        msg["To"] = TO_EMAIL
        msg.set_content(f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}")

        # Send email via Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(YOUR_EMAIL, YOUR_PASSWORD)
            smtp.send_message(msg)

        print("Feedback email sent successfully.")
        return True

    except smtplib.SMTPAuthenticationError:
        print("Error: Authentication failed. Check your email credentials.")
        return False
    except Exception as e:
        print("Error sending feedback:", e)
        return False
