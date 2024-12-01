from typing import List, Optional
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import Settings
from pathlib import Path

class EmailManager:
    def __init__(self, settings: Settings):
        self.conf = ConnectionConfig(
            MAIL_USERNAME=settings.SMTP_USER,
            MAIL_PASSWORD=settings.SMTP_PASSWORD,
            MAIL_FROM=settings.SMTP_USER,
            MAIL_PORT=settings.SMTP_PORT,
            MAIL_SERVER=settings.SMTP_HOST,
            MAIL_TLS=settings.SMTP_TLS,
            MAIL_SSL=False,
            TEMPLATE_FOLDER=Path(__file__).parent / 'email_templates'
        )
        self.fastmail = FastMail(self.conf)
    
    async def send_email(
        self,
        email_to: str,
        subject: str,
        body: str,
        template_name: Optional[str] = None,
        template_body: Optional[dict] = None
    ):
        message = MessageSchema(
            subject=subject,
            recipients=[email_to],
            body=body,
            subtype='html'
        )
        
        await self.fastmail.send_message(message, template_name=template_name)