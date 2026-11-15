"""Authentication router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.deps import get_circle_id, get_current_member, get_db, require_caretaker_or_elder
from app.models.member import Member
from app.schemas.auth import (
    CreateCircleRequest,
    CreateCircleResponse,
    CreateInviteRequest,
    InviteResponse,
    LoginRequest,
    LoginResponse,
    RedeemInviteRequest,
    RedeemInviteResponse,
)
from app.schemas.common import MessageResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    current_settings = get_settings()
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=current_settings.effective_cookie_secure,
        samesite=current_settings.cookie_samesite,
        max_age=current_settings.access_token_minutes * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=current_settings.effective_cookie_secure,
        samesite=current_settings.cookie_samesite,
        max_age=current_settings.refresh_token_days * 86400,
    )


@router.post("/circles", response_model=CreateCircleResponse)
async def create_circle(
    payload: CreateCircleRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> CreateCircleResponse:
    auth_svc = AuthService(db)
    circle, member, _ = await auth_svc.create_circle(
        circle_name=payload.circle_name,
        elder_name=payload.elder_name,
        passcode=payload.passcode,
    )

    from app.core.security import create_access_token, create_refresh_token
    access = create_access_token(member.id, circle.id, member.role.value)
    refresh = create_refresh_token(member.id)
    _set_auth_cookies(response, access, refresh)

    return CreateCircleResponse(
        circle_id=circle.id,
        circle_code=circle.circle_code,
        member_id=member.id,
        display_name=member.display_name,
        role=member.role.value,
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    auth_svc = AuthService(db)
    ip = request.client.host if request.client else None
    member, access, refresh, circle_name = await auth_svc.login(
        circle_code=payload.circle_code,
        passcode=payload.passcode,
        ip=ip,
    )
    _set_auth_cookies(response, access, refresh)

    return LoginResponse(
        member_id=member.id,
        circle_id=member.circle_id,
        role=member.role.value,
        display_name=member.display_name,
        circle_name=circle_name,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(response: Response) -> MessageResponse:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return MessageResponse(message="Successfully logged out.")


@router.post("/invites", response_model=InviteResponse)
async def create_invite(
    payload: CreateInviteRequest,
    actor: Member = Depends(require_caretaker_or_elder),
    db: AsyncSession = Depends(get_db),
) -> InviteResponse:
    auth_svc = AuthService(db)
    invite, raw_code = await auth_svc.create_invite(
        circle_id=actor.circle_id,
        created_by_id=actor.id,
        role=payload.role,
        expires_hours=payload.expires_hours,
    )
    return InviteResponse(
        id=invite.id,
        role=invite.role.value,
        invite_code=raw_code,
        expires_at=invite.expires_at,
    )


@router.post("/invites/redeem", response_model=RedeemInviteResponse)
async def redeem_invite(
    payload: RedeemInviteRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> RedeemInviteResponse:
    auth_svc = AuthService(db)
    ip = request.client.host if request.client else None
    member, access, refresh = await auth_svc.redeem_invite(
        raw_code=payload.invite_code,
        display_name=payload.display_name,
        email=payload.email,
        passcode=payload.passcode,
        ip=ip,
    )
    _set_auth_cookies(response, access, refresh)

    return RedeemInviteResponse(
        member_id=member.id,
        circle_id=member.circle_id,
        role=member.role.value,
        display_name=member.display_name,
    )
