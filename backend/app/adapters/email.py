"""Email adapter interface and implementations."""

from __future__ import annotations

import abc
from email.message import EmailMessage

import aiosmtplib

from app.core.config import get_settings


class EmailSender(abc.ABC):
    @abc.abstractmethod
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str = "",
    ) -> bool:
        raise NotImplementedError


class SmtpEmailSender(EmailSender):
    def __init__(self) -> None:
        self.settings = get_settings()

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str = "",
    ) -> bool:
        msg = EmailMessage()
        msg["From"] = self.settings.email_from
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(text_body or html_body)
        if html_body:
            msg.add_alternative(html_body, subtype="html")

        try:
            await aiosmtplib.send(
                msg,
                hostname=self.settings.smtp_host,
                port=self.settings.smtp_port,
                username=self.settings.smtp_user or None,
                password=self.settings.smtp_password or None,
                use_tls=False,
            )
            return True
        except Exception:
            return False


class FakeEmailSender(EmailSender):
    def __init__(self) -> None:
        self.sent_emails: list[dict] = []

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str = "",
    ) -> bool:
        self.sent_emails.append({
            "to": to_email,
            "subject": subject,
            "html": html_body,
            "text": text_body,
        })
        return True
