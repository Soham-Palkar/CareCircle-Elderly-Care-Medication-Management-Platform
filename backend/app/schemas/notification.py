"""Notification schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: UUID
    member_id: UUID
    circle_id: UUID
    channel: str
    type: str
    status: str
    attempts: int
    sent_at: datetime | None = None
    created_at: datetime
