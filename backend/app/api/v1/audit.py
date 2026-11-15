"""Audit log router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_member, get_db
from app.models.member import Member
from app.schemas.audit import AuditLogOut
from app.schemas.common import PaginatedResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=PaginatedResponse[AuditLogOut])
async def list_audit_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[AuditLogOut]:
    svc = AuditService(db)
    items, total = await svc.list_logs(current_member.circle_id, page, page_size)
    return PaginatedResponse(
        items=[
            AuditLogOut(
                id=a.id,
                circle_id=a.circle_id,
                actor_member_id=a.actor_member_id,
                action=a.action,
                entity_type=a.entity_type,
                entity_id=a.entity_id,
                before=a.before,
                after=a.after,
                created_at=a.created_at,
            )
            for a in items
        ],
        total=total,
        page=page,
        page_size=page_size,
    )
