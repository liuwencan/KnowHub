from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    phone: str
    password: str


class StaffLoginRequest(BaseModel):
    emp_id: str
    password: str


class Identity(BaseModel):
    user_id: str
    role: Literal["customer", "staff"]
    permissions: set[str] = Field(default_factory=set)


class LoginResponse(BaseModel):
    identity: Identity
    expires_in: int


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=20_000)
    conversation_id: str | None = None


class FeedbackRequest(BaseModel):
    helpful: bool
    comment: str | None = Field(default=None, max_length=1000)


class Citation(BaseModel):
    document_id: int | str
    version_id: int | str | None = None
    chunk_id: str | None = None
    source: str
    score: float = 0.0


class DocumentResponse(BaseModel):
    doc_id: int
    doc_title: str
    status: str
    current_version_id: int | None = None
    accessible_by: str | None = None
    expire_date: date | None = None


class HealthItem(BaseModel):
    status: Literal["up", "down", "degraded", "unconfigured"]
    required: bool
    detail: str | None = None
