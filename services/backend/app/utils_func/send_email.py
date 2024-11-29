import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from base64 import b64encode
from app.core.config import settings

from pathlib import Path

def send_verification_email(to_email: str, subject: str, verification_link: str, email_template: str):
    # Sender's email and password
    from_email = settings.MAIL_FROM
    username = settings.MAIL_USERNAME
    password = settings.MAIL_PASSWORD
    email_server = settings.MAIL_SERVER
    email_port = settings.MAIL_PORT

    app_directory = os.getcwd()

    # HTML template
    template_path = os.path.join(app_directory, "templates", email_template)
    with open(template_path, 'r') as file:
        original_html_content = file.read()

    # HTML content for the email
    html_content = original_html_content.replace("{{verification_link}}", verification_link)

    # construct the email
    msg = MIMEMultipart()
    msg["From"] = f"Sommai <{from_email}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg['X-Mailer'] = "Sommai"
    msg.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP(email_server, email_port)
        server.connect(email_server, email_port)
        print(f"Send {email_template} email to: {to_email} ({server})")

        server.starttls()
        server.ehlo()

        server.login(username, password)
        server.sendmail(from_email, to_email, msg.as_string())
    except Exception as e:
        print(f"Error sending email: {e}")
    finally:
        server.quit()
