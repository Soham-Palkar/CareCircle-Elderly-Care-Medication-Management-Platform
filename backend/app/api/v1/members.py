"""Members and permissions management router."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_member, get_db, require_elder
from app.models.member import Member
from app.schemas.common import MessageResponse
from app.schemas.member import MemberOut, MemberPermissionOut, MemberWithPermissions, NotifyPrefsUpdate, UpdatePermissionsRequest
from app.services.member_service import MemberService

router = APIRouter(prefix="/members", tags=["members"])


@router.get("", response_model=list[MemberWithPermissions])
async def list_members(
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> list[MemberWithPermissions]:
    svc = MemberService(db, current_member.circle_id)
    members = await svc.list_members()
    result = []
    for m in members:
        p_out = None
        if m.permissions:
            p_out = MemberPermissionOut(
                member_id=m.permissions.member_id,
                can_view_meds=m.permissions.can_view_meds,
                can_edit_meds=m.permissions.can_edit_meds,
                can_mark_doses=m.permissions.can_mark_doses,
                can_view_appointments=m.permissions.can_view_appointments,
                can_edit_appointments=m.permissions.can_edit_appointments,
                can_view_health=m.permissions.can_view_health,
                receives_alerts=m.permissions.receives_alerts,
                alert_level_min=m.permissions.alert_level_min,
            )
        result.append(
            MemberWithPermissions(
                id=m.id,
                circle_id=m.circle_id,
                display_name=m.display_name,
                role=m.role.value,
                email=m.email,
                telegram_chat_id=m.telegram_chat_id,
                is_active=m.is_active,
                created_at=m.created_at,
                permissions=p_out,
            )
        )
    return result


@router.patch("/{member_id}/permissions", response_model=MemberPermissionOut)
async def update_member_permissions(
    member_id: UUID,
    payload: UpdatePermissionsRequest,
    elder: Member = Depends(require_elder),
    db: AsyncSession = Depends(get_db),
) -> MemberPermissionOut:
    svc = MemberService(db, elder.circle_id)
    updated = await svc.update_permissions(elder, member_id, payload.model_dump(exclude_unset=True))
    return MemberPermissionOut(
        member_id=updated.member_id,
        can_view_meds=updated.can_view_meds,
        can_edit_meds=updated.can_edit_meds,
        can_mark_doses=updated.can_mark_doses,
        can_view_appointments=updated.can_view_appointments,
        can_edit_appointments=updated.can_edit_appointments,
        can_view_health=updated.can_view_health,
        receives_alerts=updated.receives_alerts,
        alert_level_min=updated.alert_level_min,
    )


@router.delete("/{member_id}", response_model=MessageResponse)
async def deactivate_member(
    member_id: UUID,
    elder: Member = Depends(require_elder),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    svc = MemberService(db, elder.circle_id)
    await svc.deactivate_member(elder, member_id)
    return MessageResponse(message="Member successfully deactivated.")


@router.patch("/me/notify-prefs", response_model=MessageResponse)
async def update_notify_prefs(
    payload: NotifyPrefsUpdate,
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    svc = MemberService(db, current_member.circle_id)
    await svc.update_notify_prefs(current_member.id, payload.model_dump(exclude_unset=True))
    return MessageResponse(message="Notification preferences updated.")
