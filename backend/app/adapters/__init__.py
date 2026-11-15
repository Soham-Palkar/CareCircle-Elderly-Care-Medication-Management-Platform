"""Adapters registry."""

from app.adapters.email import EmailSender, FakeEmailSender, SmtpEmailSender
from app.adapters.messaging import FakeMessagingChannel, MessagingChannel, TelegramMessagingChannel
from app.adapters.vision import FakeVisionExtractor, VisionExtractor, get_vision_extractor

__all__ = [
    "EmailSender",
    "SmtpEmailSender",
    "FakeEmailSender",
    "MessagingChannel",
    "TelegramMessagingChannel",
    "FakeMessagingChannel",
    "VisionExtractor",
    "FakeVisionExtractor",
    "get_vision_extractor",
]
