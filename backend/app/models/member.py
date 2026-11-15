"""Member entity representing users in a CareCircle."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Role(str, enum.Enum):
    elder = "elder"
    caretaker = "caretaker"
    family = "family"
    doctor = "doctor"


class Member(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "members"

    circle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("care_circles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[Role] = mapped_column(
        Enum(Role, name="member_role_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    passcode_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    telegram_chat_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    notify_prefs: Mapped[dict] = mapped_column(
        JSONB,
        default=lambda: {
            "email_enabled": True,
            "telegram_enabled": False,
            "quiet_hours_start": None,
            "quiet_hours_end": None,
        },
        nullable=False,
    )
    failed_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    circle: Mapped[CareCircle] = relationship("CareCircle", back_populates="members")
    permissions: Mapped[MemberPermission] = relationship(
        "MemberPermission",
        back_populates="member",
        uselist=False,
        cascade="all, delete-orphan",
    )
    notifications: Mapped[list[Notification]] = relationship("Notification", back_populates="member")
