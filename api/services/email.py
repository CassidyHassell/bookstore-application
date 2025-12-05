import smtplib
from email.mime.text import MIMEText
from utils.config import Config

def send_email(recipient, subject, html_body):
    try:
        msg = MIMEText(html_body, "html")
        msg["Subject"] = subject
        msg["From"] = "noreply@310bookstoreproject.com"
        msg["To"] = recipient

        with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
            server.starttls()
            server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email to {recipient}: {e}")
        return False
