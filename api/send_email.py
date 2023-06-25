import os
from typing import Dict

from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

load_dotenv()


class Envs:
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_FROM = os.getenv("MAIL_FROM")
    MAIL_PORT = os.getenv("MAIL_PORT" or 587)
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME")


conf = ConnectionConfig(
    MAIL_USERNAME=Envs.MAIL_USERNAME,
    MAIL_PASSWORD=Envs.MAIL_PASSWORD,
    MAIL_FROM=Envs.MAIL_FROM,
    MAIL_PORT=Envs.MAIL_PORT,
    MAIL_SERVER=Envs.MAIL_SERVER,
    MAIL_FROM_NAME=Envs.MAIL_FROM_NAME,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False,
    TEMPLATE_FOLDER="api/templates",
)


async def send_registration_mail(subject: str, email_to: str, body: dict):
    message = MessageSchema(
        subject=subject, recipients=[email_to], template_body=body, subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message=message, template_name="registered.html")


async def password_reset(subject: str, email_to: str, body: dict):
    message = MessageSchema(
        subject=subject, recipients=[email_to], template_body=body, subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message=message, template_name="password-reset.html")
