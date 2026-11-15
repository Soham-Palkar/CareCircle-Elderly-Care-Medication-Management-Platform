"""Authentication, registration, and invite schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateCircleRequest(BaseModel):
    circle_name: str = Field(min_length=2, max_length=100)
    elder_name: str = Field(min_length=2, max_length=100)
    passcode: str = Field(min_length=6, max_length=100)


class CreateCircleResponse(BaseModel):
    circle_id: UUID
    circle_code: str
    member_id: UUID
    display_name: str
    role: str


class LoginRequest(BaseModel):
    circle_code: str = Field(min_length=4, max_length=30)
    passcode: str = Field(min_length=6, max_length=100)


class LoginResponse(BaseModel):
    member_id: UUID
    circle_id: UUID
    role: str
    display_name: str
    circle_name: str


class CreateInviteRequest(BaseModel):
    role: str = Field(pattern="^(caretaker|family|doctor)$")
    expires_hours: int = Field(default=48, ge=1, le=168)


class InviteResponse(BaseModel):
    id: UUID
    role: str
    invite_code: str
    expires_at: datetime


class RedeemInviteRequest(BaseModel):
    invite_code: str = Field(min_length=6)
    display_name: str = Field(min_length=2, max_length=100)
    email: str | None = None
    passcode: str = Field(min_length=6, max_length=100)


class RedeemInviteResponse(BaseModel):
    member_id: UUID
    circle_id: UUID
    role: str
    display_name: str
