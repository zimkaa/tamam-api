import smtplib
from email.message import EmailMessage

from celery import Celery

from back_end.settings import (
    SMTP_PASSWORD,
    SMTP_USER,
)


SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465

celery = Celery("tasks", broker="redis://redis:6379")


def get_email_template_code(codes: list[str], email_to: str):
    email = EmailMessage()
    email["Subject"] = "Code"
    email["From"] = SMTP_USER
    email["To"] = SMTP_USER
    code_string = ", ".join(codes)

    email.set_content(
        "<div>" f'<h1 style="color: red;">Вот ваши коды: {code_string} send to {email_to} 😊</h1>' "</div>",
        subtype="html",
    )
    return email


@celery.task
def send_email_with_codes(codes: list[str], email_to: str):
    email = get_email_template_code(codes, email_to)
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(email)
