"""Member and permission schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MemberPermissionOut(BaseModel):
    member_id: UUID
    can_view_meds: bool
    can_edit_meds: bool
    can_mark_doses: bool
    can_view_appointments: bool
    can_edit_appointments: bool
    can_view_health: bool
    receives_alerts: bool
    alert_level_min: int


class UpdatePermissionsRequest(BaseModel):
    can_view_meds: bool | None = None
    can_edit_meds: bool | None = None
    can_mark_doses: bool | None = None
    can_view_appointments: bool | None = None
    can_edit_appointments: bool | None = None
    can_view_health: bool | None = None
    receives_alerts: bool | None = None
    alert_level_min: int | None = None


class MemberOut(BaseModel):
    id: UUID
    circle_id: UUID
    display_name: str
    role: str
    email: str | None = None
    telegram_chat_id: int | None = None
    is_active: bool
    created_at: datetime


class MemberWithPermissions(MemberOut):
    permissions: MemberPermissionOut | None = None


class NotifyPrefsUpdate(BaseModel):
    email_enabled: bool | None = None
    telegram_enabled: bool | None = None
    quiet_hours_start: str | None = None
    quiet_hours_end: str | None = None
