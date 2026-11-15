"""Audit log schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: int
    circle_id: UUID
    actor_member_id: UUID | None = None
    action: str
    entity_type: str
    entity_id: UUID
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    created_at: datetime
