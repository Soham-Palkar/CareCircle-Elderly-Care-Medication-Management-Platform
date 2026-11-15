"""Voice intent schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class VoiceIntentRequest(BaseModel):
    text: str
    language: str = "en"
    dose_event_id: UUID | None = None


class VoiceIntentResponse(BaseModel):
    intent: str
    confidence: float
    action_taken: bool
    reply_text: str
    reply_hi: str | None = None
    advisory: str | None = None
