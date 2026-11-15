"""Reward entity representing relationship-based rewards for streaks."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDMixin


class RewardType(str, enum.Enum):
    call = "call"
    photo = "photo"
    message = "message"


class Reward(UUIDMixin, Base):
    __tablename__ = "rewards"

    recipient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("care_recipients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    threshold_days: Mapped[int] = mapped_column(Integer, nullable=False)
    reward_type: Mapped[RewardType] = mapped_column(
        Enum(RewardType, name="reward_type_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    reward_ref: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    unlocked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
