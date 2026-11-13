"""Pydantic schemas for Gemini API Key management and lifecycle."""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ApiKeyStatus(str, Enum):
    """Lifecycle status states for user's Gemini API Key."""

    NOT_CONFIGURED = "NOT_CONFIGURED"
    VALID = "VALID"
    INVALID = "INVALID"


class GeminiKeyCreateRequest(BaseModel):
    """Payload for registering or updating user's Gemini API Key."""

    api_key: str = Field(
        ...,
        min_length=15,
        description="Raw Google Gemini API Key starting with AIzaSy...",
    )


class GeminiKeyStatusResponse(BaseModel):
    """Safe status report schema returned without exposing full API Key."""

    status: ApiKeyStatus = Field(..., description="Current status of the credential")
    key_hint: Optional[str] = Field(None, description="Masked key ending, e.g., '...3aF1'")
    last_validated_at: Optional[datetime] = Field(None, description="Timestamp of last successful validation")
    updated_at: Optional[datetime] = Field(None, description="Timestamp of last modification")

    model_config = {"from_attributes": True}
