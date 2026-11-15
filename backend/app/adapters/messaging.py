"""Messaging adapter interface and Telegram implementation."""

from __future__ import annotations

import abc

import httpx

from app.core.config import get_settings


class MessagingChannel(abc.ABC):
    @abc.abstractmethod
    async def send_message(self, recipient_id: int | str, text: str) -> bool:
        raise NotImplementedError


class TelegramMessagingChannel(MessagingChannel):
    def __init__(self) -> None:
        self.settings = get_settings()

    async def send_message(self, recipient_id: int | str, text: str) -> bool:
        if not self.settings.telegram_bot_token:
            return False
        url = f"https://api.telegram.org/bot{self.settings.telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": recipient_id,
            "text": text,
            "parse_mode": "HTML",
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=payload)
                return res.status_code == 200
        except Exception:
            return False


class FakeMessagingChannel(MessagingChannel):
    def __init__(self) -> None:
        self.sent_messages: list[dict] = []

    async def send_message(self, recipient_id: int | str, text: str) -> bool:
        self.sent_messages.append({"recipient": recipient_id, "text": text})
        return True
