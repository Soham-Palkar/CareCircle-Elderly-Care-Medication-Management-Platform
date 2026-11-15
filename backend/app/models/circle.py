"""CareCircle entity."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin


class CareCircle(UUIDMixin, Base):
    __tablename__ = "care_circles"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    circle_code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    recipient: Mapped[CareRecipient] = relationship("CareRecipient", back_populates="circle", uselist=False)
    members: Mapped[list[Member]] = relationship("Member", back_populates="circle")
    invites: Mapped[list[Invite]] = relationship("Invite", back_populates="circle")
