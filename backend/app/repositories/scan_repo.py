"""Scan draft repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.models.recipient import CareRecipient
from app.models.scan_draft import ScanDraft, ScanDraftStatus
from app.repositories.base import BaseRepository


class ScanRepository(BaseRepository):

    async def create(self, recipient_id: UUID, uploaded_by: UUID, data: dict) -> ScanDraft:
        draft = ScanDraft(
            recipient_id=recipient_id,
            uploaded_by=uploaded_by,
            **data,
        )
        self.db.add(draft)
        await self.db.flush()
        return draft

    async def get_by_id(self, scan_id: UUID) -> ScanDraft | None:
        stmt = (
            select(ScanDraft)
            .join(CareRecipient, ScanDraft.recipient_id == CareRecipient.id)
            .where(
                ScanDraft.id == scan_id,
                CareRecipient.circle_id == self.circle_id,
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def update_status(self, scan_id: UUID, status: ScanDraftStatus) -> ScanDraft | None:
        draft = await self.get_by_id(scan_id)
        if draft:
            draft.status = status
            await self.db.flush()
        return draft
