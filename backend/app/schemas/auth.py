"""Pydantic schemas for authentication and user management."""

import re
import uuid
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class UserRegisterRequest(BaseModel):
    """Payload for user registration."""

    email: str = Field(..., description="Valid user email address")
    password: str = Field(..., min_length=8, description="User password (minimum 8 characters)")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, value: str) -> str:
        clean_email = value.strip().lower()
        if not EMAIL_REGEX.match(clean_email):
            raise ValueError("Formato de e-mail inválido")
        return clean_email


class UserLoginRequest(BaseModel):
    """Payload for user authentication."""

    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class TokenResponse(BaseModel):
    """Bearer token payload returned after successful login."""

    access_token: str = Field(..., description="Signed JWT Bearer access token")
    token_type: str = Field(default="bearer", description="Token type")


class UserResponse(BaseModel):
    """Public user response schema."""

    id: uuid.UUID
    email: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
