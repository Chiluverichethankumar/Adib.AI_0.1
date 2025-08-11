import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

YOUR_EMAIL = os.getenv("YOUR_EMAIL")
YOUR_PASSWORD = os.getenv("YOUR_PASSWORD")
TO_EMAIL = os.getenv("FEEDBACK_TO_EMAIL")

def send_feedback(name, email, message):
    print(f"Email: {YOUR_EMAIL}")
    print(f"Password: {YOUR_PASSWORD}")
    print(f"To email: {TO_EMAIL}")

    try:
        msg = EmailMessage()
        msg["Subject"] = f"Adib.AI Feedback from {name}"
        msg["From"] = YOUR_EMAIL
        msg["To"] = TO_EMAIL
        msg.set_content(f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(YOUR_EMAIL, YOUR_PASSWORD)
            smtp.send_message(msg)

        return True
    except Exception as e:
        print("Error sending feedback:", e)
        return False