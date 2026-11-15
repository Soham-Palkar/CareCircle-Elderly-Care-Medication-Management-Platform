"""Vision scan service for prescription photo extraction and wrong-pill check."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.vision import get_vision_extractor
from app.core.errors import ForbiddenError, NotFoundError, ValidationError
from app.domain.permissions import has_permission
from app.models.member import Member
from app.models.scan_draft import ScanDraft, ScanDraftStatus
from app.repositories.audit_repo import AuditRepository
from app.repositories.dose_repo import DoseRepository
from app.repositories.scan_repo import ScanRepository
from app.services.medication_service import MedicationService

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB


class ScanService:
    def __init__(self, db: AsyncSession, circle_id: UUID) -> None:
        self.db = db
        self.circle_id = circle_id
        self.scan_repo = ScanRepository(db, circle_id)
        self.audit_repo = AuditRepository(db)
        self.extractor = get_vision_extractor()

    async def upload_and_extract(
        self,
        actor: Member,
        recipient_id: UUID,
        image_bytes: bytes,
        mime_type: str,
    ) -> ScanDraft:
        if mime_type not in ALLOWED_MIME_TYPES:
            raise ValidationError(f"Invalid image type. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}")

        if len(image_bytes) > MAX_IMAGE_SIZE:
            raise ValidationError("Image exceeds maximum allowed size of 10 MB.")

        extracted_data = await self.extractor.extract_label(image_bytes, mime_type)
        confidence = extracted_data.get("confidence", 0.0)

        draft = await self.scan_repo.create(
            recipient_id=recipient_id,
            uploaded_by=actor.id,
            data={
                "extracted": extracted_data,
                "confidence": confidence,
                "status": ScanDraftStatus.pending,
            },
        )

        await self.audit_repo.log(
            circle_id=self.circle_id,
            actor_member_id=actor.id,
            action="scan_draft_created",
            entity_type="scan_draft",
            entity_id=draft.id,
            after={"confidence": float(confidence)},
        )
        await self.db.commit()
        return draft

    async def confirm_draft(
        self,
        actor: Member,
        draft_id: UUID,
        medication_data: dict[str, Any],
        schedule_data: dict[str, Any],
    ) -> dict[str, Any]:
        draft = await self.scan_repo.get_by_id(draft_id)
        if not draft:
            raise NotFoundError("Scan draft not found.")

        if draft.status != ScanDraftStatus.pending:
            raise ValidationError("Scan draft is no longer pending confirmation.")

        med_svc = MedicationService(self.db, self.circle_id)
        medication_data["source"] = "scan"
        med, advisory = await med_svc.create_medication(actor, draft.recipient_id, medication_data)
        schedule = await med_svc.create_schedule(actor, med.id, schedule_data)

        await self.scan_repo.update_status(draft_id, ScanDraftStatus.confirmed)
        await self.audit_repo.log(
            circle_id=self.circle_id,
            actor_member_id=actor.id,
            action="scan_draft_confirmed",
            entity_type="scan_draft",
            entity_id=draft_id,
            after={"medication_id": str(med.id)},
        )
        await self.db.commit()

        return {
            "status": "confirmed",
            "medication_id": med.id,
            "schedule_id": schedule.id,
            "advisory": advisory,
        }

    async def verify_dose_strip(
        self,
        actor: Member,
        dose_event_id: UUID,
        image_bytes: bytes,
        mime_type: str,
    ) -> dict[str, Any]:
        dose_repo = DoseRepository(self.db, self.circle_id)
        dose = await dose_repo.get_by_id(dose_event_id)
        if not dose or not dose.medication:
            raise NotFoundError("Dose event or associated medication not found.")

        res = await self.extractor.verify_strip_match(
            image_bytes=image_bytes,
            mime_type=mime_type,
            expected_name=dose.medication.name,
            expected_strength=dose.medication.strength,
        )
        return res
