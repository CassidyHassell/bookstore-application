import smtplib
from email.mime.text import MIMEText

def send_email(recipient, subject, html_body):
    try:
        msg = MIMEText(html_body, "html")
        msg["Subject"] = subject
        msg["From"] = "noreply@310bookstoreproject.com"
        msg["To"] = recipient

        with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
            server.starttls()
            server.login("8a587d82658f52", "b663cf4abd8a1c")
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email to {recipient}: {e}")
        return False

# Looking to send emails in production? Check out our Email API/SMTP product!
# import smtplib

# sender = "Private Person <from@example.com>"
# receiver = "A Test User <to@example.com>"

# message = f"""\
# Subject: Hi Mailtrap
# To: {receiver}
# From: {sender}

# This is a test e-mail message."""

#     server.sendmail(sender, receiver, message)