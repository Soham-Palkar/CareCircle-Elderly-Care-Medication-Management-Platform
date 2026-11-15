"""Notification outbox dispatcher with exponential retry backoff."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.adapters.email import SmtpEmailSender
from app.adapters.messaging import TelegramMessagingChannel
from app.models.notification import Notification, NotificationChannel, NotificationStatus
from app.models.member import Member


async def dispatch_outbox(
    db: AsyncSession,
    email_sender: SmtpEmailSender | None = None,
    msg_channel: TelegramMessagingChannel | None = None,
    batch_size: int = 50,
) -> int:
    now = datetime.now(timezone.utc)
    email_client = email_sender or SmtpEmailSender()
    telegram_client = msg_channel or TelegramMessagingChannel()

    stmt = (
        select(Notification)
        .where(
            Notification.status == NotificationStatus.pending,
            Notification.next_attempt_at <= now,
        )
        .options(selectinload(Notification.member))
        .order_by(Notification.next_attempt_at.asc())
        .limit(batch_size)
        .with_for_update(skip_locked=True)
    )

    res = await db.execute(stmt)
    notifications = list(res.scalars().all())

    dispatched = 0
    for notif in notifications:
        success = False
        payload = notif.payload or {}
        subject = payload.get("subject", "CareCircle Notification")
        body = payload.get("message", subject)

        try:
            if notif.channel == NotificationChannel.email:
                to_addr = notif.member.email if notif.member else None
                if to_addr:
                    success = await email_client.send_email(
                        to_email=to_addr,
                        subject=subject,
                        html_body=f"<p>{body}</p>",
                        text_body=body,
                    )
            elif notif.channel == NotificationChannel.telegram:
                chat_id = notif.member.telegram_chat_id if notif.member else None
                if chat_id:
                    success = await telegram_client.send_message(chat_id, body)
            else:
                # in_app notifications are considered immediately delivered
                success = True
        except Exception:
            success = False

        if success:
            notif.status = NotificationStatus.sent
            notif.sent_at = datetime.now(timezone.utc)
            dispatched += 1
        else:
            notif.attempts += 1
            if notif.attempts >= 5:
                notif.status = NotificationStatus.failed
            else:
                backoff_minutes = 2 ** notif.attempts
                notif.next_attempt_at = now + timedelta(minutes=backoff_minutes)

    await db.commit()
    return dispatched
