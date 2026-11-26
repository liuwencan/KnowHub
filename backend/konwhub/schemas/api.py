from datetime import date
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    """所有 JSON API 共用的响应契约。"""

    success: bool = True
    message: str | None = None
    error_code: str | None = Field(default=None, alias="errorCode")
    data: T | None = None

    model_config = {"populate_by_name": True}

    @classmethod
    def success_response(cls, data: T | None = None, message: str | None = None) -> "Response[T]":
        return cls(success=True, message=message, data=data)

    @classmethod
    def fail(cls, message: str | None = None, error_code: str | None = None, data: Any = None) -> "Response[Any]":
        return cls(success=False, message=message, errorCode=error_code, data=data)


class LoginRequest(BaseModel):
    phone: str | None = None
    username: str | None = None
    password: str

    def identifier(self) -> str:
        return self.username or self.phone or ""


class StaffLoginRequest(BaseModel):
    emp_id: str | None = None
    employee_no: str | None = None
    username: str | None = None
    password: str

    def identifier(self) -> str:
        return self.employee_no or self.emp_id or self.username or ""


class RegisterRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    real_name: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=6, max_length=128)
    employee_no: str | None = Field(default=None, max_length=64)
    department_id: int | None = None


class DepartmentRequest(BaseModel):
    parent_id: int | None = None
    name: str = Field(min_length=1, max_length=128)
    path: str | None = None
    sort_order: int = 0
    status: int = Field(default=1, ge=0, le=1)


class RoleRequest(BaseModel):
    code: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=64)
    description: str | None = Field(default=None, max_length=255)


class UserUpdateRequest(BaseModel):
    real_name: str | None = Field(default=None, max_length=128)
    department_id: int | None = None
    avatar_url: str | None = Field(default=None, max_length=512)
    status: int | None = Field(default=None, ge=0, le=2)


class UserRoleRequest(BaseModel):
    user_id: int
    role_id: int
    department_id: int | None = None


class RoleDepartmentRequest(BaseModel):
    role_id: int
    department_id: int


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
