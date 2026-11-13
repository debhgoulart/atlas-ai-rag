"""Pydantic schemas for Document contracts."""

import enum
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class DocumentStatusEnum(str, enum.Enum):
    """Lifecycle processing state for documents."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentResponse(BaseModel):
    """Schema returned for document representations."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Document UUID")
    knowledge_base_id: uuid.UUID = Field(..., description="Parent knowledge base UUID")
    filename: str = Field(..., description="Original file name")
    content_type: str = Field(..., description="MIME content type")
    file_size_bytes: int = Field(..., description="File size in bytes")
    status: DocumentStatusEnum = Field(..., description="Ingestion processing status")
    error_message: Optional[str] = Field(None, description="Failure reason if status is failed")
    chunk_count: int = Field(default=0, description="Total chunks generated")
    created_at: datetime = Field(..., description="Upload timestamp in UTC")
    updated_at: datetime = Field(..., description="Last update timestamp in UTC")
