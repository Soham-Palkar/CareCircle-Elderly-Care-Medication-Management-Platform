"""Realtime Server-Sent Events (SSE) router."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.deps import get_current_member
from app.models.member import Member
from app.services.realtime import realtime_broker

router = APIRouter(tags=["realtime"])


@router.get("/stream")
async def stream_circle_events(
    current_member: Member = Depends(get_current_member),
) -> StreamingResponse:
    """Stream real-time circle updates (dose state transitions, alerts)."""
    return StreamingResponse(
        realtime_broker.stream(current_member.circle_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
