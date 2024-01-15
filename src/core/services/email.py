from pydantic import EmailStr
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from src.core import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME=settings.mail_from_name,
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    TEMPLATES_FOLDER="src/templates",
)


class EmailService:
    def __init__(self, email_to: EmailStr) -> None:
        self.email_to = email_to

    def send_verify_email(self, subject: str, body: str):
        pass

    async def send_reset_password_email(self, subject: str, body: dict):
        message = MessageSchema(
            subject=subject,
            recipients=[str(self.email_to)],
            template_body=body,
            subtype="html",
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="password_reset.html")
