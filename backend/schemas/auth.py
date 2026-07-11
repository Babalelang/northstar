from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    username: str
    email: str
    role: str
    is_active: bool
    last_login: datetime | None = None
    created_at: datetime


class LoginResponse(BaseModel):
    token: str
    user: UserOut


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    password: str
    role: str = "editor"

    @field_validator("role")
    @classmethod
    def role_must_be_admin_or_editor(cls, value: str) -> str:
        if value not in ("admin", "editor"):
            raise ValueError("role must be 'admin' or 'editor'")
        return value

    @field_validator("password")
    @classmethod
    def password_minimum_length(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("password must be at least 8 characters")
        return value


class UserUpdate(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    role: str
    is_active: bool = True
    # blank/omitted = keep the current password
    password: str | None = None

    @field_validator("role")
    @classmethod
    def role_must_be_admin_or_editor(cls, value: str) -> str:
        if value not in ("admin", "editor"):
            raise ValueError("role must be 'admin' or 'editor'")
        return value
