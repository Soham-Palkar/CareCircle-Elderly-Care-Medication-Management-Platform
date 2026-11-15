"""Main v1 API router assembling all sub-routers."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.actions import router as actions_router
from app.api.v1.adherence import router as adherence_router
from app.api.v1.appointments import router as appointments_router
from app.api.v1.audit import router as audit_router
from app.api.v1.auth import router as auth_router
from app.api.v1.doses import router as doses_router
from app.api.v1.health import router as health_router
from app.api.v1.medications import router as medications_router
from app.api.v1.members import router as members_router
from app.api.v1.messaging import router as messaging_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.proposals import router as proposals_router
from app.api.v1.scans import router as scans_router
from app.api.v1.stream import router as stream_router
from app.api.v1.twin import router as twin_router
from app.api.v1.voice import router as voice_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(members_router)
api_v1_router.include_router(medications_router)
api_v1_router.include_router(doses_router)
api_v1_router.include_router(adherence_router)
api_v1_router.include_router(appointments_router)
api_v1_router.include_router(notifications_router)
api_v1_router.include_router(actions_router)
api_v1_router.include_router(scans_router)
api_v1_router.include_router(twin_router)
api_v1_router.include_router(proposals_router)
api_v1_router.include_router(voice_router)
api_v1_router.include_router(messaging_router)
api_v1_router.include_router(audit_router)
api_v1_router.include_router(stream_router)
