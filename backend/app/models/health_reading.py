"""HealthReading entity representing biometric inputs (manual or simulated)."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin


class ReadingKind(str, enum.Enum):
    heart_rate = "heart_rate"
    sleep_hours = "sleep_hours"
    steps = "steps"
    bp_sys = "bp_sys"
    bp_dia = "bp_dia"
    glucose = "glucose"
    mood = "mood"


class ReadingSource(str, enum.Enum):
    simulated = "simulated"
    manual = "manual"
    device = "device"


class HealthReading(UUIDMixin, Base):
    __tablename__ = "health_readings"
    __table_args__ = (
        Index("ix_health_readings_recipient_kind", "recipient_id", "kind", "recorded_at"),
    )

    recipient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("care_recipients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kind: Mapped[ReadingKind] = mapped_column(
        Enum(ReadingKind, name="reading_kind_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    value: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    source: Mapped[ReadingSource] = mapped_column(
        Enum(ReadingSource, name="reading_source_enum", values_callable=lambda x: [e.value for e in x]),
        default=ReadingSource.manual,
        nullable=False,
    )

    # Relationships
    recipient: Mapped[CareRecipient] = relationship("CareRecipient", back_populates="health_readings")
