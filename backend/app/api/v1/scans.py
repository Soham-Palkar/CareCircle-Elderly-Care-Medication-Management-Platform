"""Vision scan and medication extraction router (Feature F5)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_member, get_db
from app.core.errors import NotFoundError
from app.models.member import Member
from app.models.recipient import CareRecipient
from app.schemas.scan import ScanConfirmRequest, ScanDraftOut, VerifyDoseResponse
from app.services.scan_service import ScanService

router = APIRouter(prefix="/scans", tags=["scans"])


async def _get_recipient_id_for_circle(db: AsyncSession, circle_id: UUID) -> UUID:
    res = await db.execute(select(CareRecipient.id).where(CareRecipient.circle_id == circle_id))
    r_id = res.scalar_one_or_none()
    if not r_id:
        raise NotFoundError("Care recipient not configured for this circle.")
    return r_id


@router.post("", response_model=ScanDraftOut)
async def upload_scan(
    file: UploadFile = File(...),
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> ScanDraftOut:
    recipient_id = await _get_recipient_id_for_circle(db, current_member.circle_id)
    content = await file.read()
    mime = file.content_type or "image/jpeg"

    svc = ScanService(db, current_member.circle_id)
    draft = await svc.upload_and_extract(
        actor=current_member,
        recipient_id=recipient_id,
        image_bytes=content,
        mime_type=mime,
    )
    return ScanDraftOut(
        id=draft.id,
        recipient_id=draft.recipient_id,
        uploaded_by=draft.uploaded_by,
        extracted=draft.extracted,
        confidence=draft.confidence,
        status=draft.status.value,
        expires_at=draft.expires_at,
        created_at=draft.created_at,
    )


@router.post("/{draft_id}/confirm")
async def confirm_scan(
    draft_id: UUID,
    payload: ScanConfirmRequest,
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> dict:
    svc = ScanService(db, current_member.circle_id)
    return await svc.confirm_draft(
        actor=current_member,
        draft_id=draft_id,
        medication_data=payload.medication_data.model_dump(),
        schedule_data=payload.schedule_data.model_dump(),
    )


@router.post("/verify-dose", response_model=VerifyDoseResponse)
async def verify_dose_strip(
    dose_event_id: UUID = Form(...),
    file: UploadFile = File(...),
    current_member: Member = Depends(get_current_member),
    db: AsyncSession = Depends(get_db),
) -> VerifyDoseResponse:
    content = await file.read()
    mime = file.content_type or "image/jpeg"

    svc = ScanService(db, current_member.circle_id)
    res = await svc.verify_dose_strip(
        actor=current_member,
        dose_event_id=dose_event_id,
        image_bytes=content,
        mime_type=mime,
    )
    return VerifyDoseResponse(
        match=res.get("match", False),
        confidence=float(res.get("confidence", 0.0)),
        message=res.get("message", "Verification completed."),
    )
