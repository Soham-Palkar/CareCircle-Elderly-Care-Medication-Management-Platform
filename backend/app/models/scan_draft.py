"""ScanDraft entity representing unverified OCR / vision extraction drafts."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class ScanDraftStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    rejected = "rejected"
    expired = "expired"


class ScanDraft(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "scan_drafts"

    recipient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("care_recipients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("members.id", ondelete="CASCADE"),
        nullable=False,
    )
    extracted: Mapped[dict] = mapped_column(JSONB, nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(4, 3), default=Decimal("0.0"), nullable=False)
    status: Mapped[ScanDraftStatus] = mapped_column(
        Enum(ScanDraftStatus, name="scan_draft_status_enum", values_callable=lambda x: [e.value for e in x]),
        default=ScanDraftStatus.pending,
        nullable=False,
        index=True,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) + timedelta(hours=24),
        nullable=False,
    )
