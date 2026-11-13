"""Pydantic schemas for Knowledge Base contracts."""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class KnowledgeBaseBase(BaseModel):
    """Base schema attributes for Knowledge Base."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique name for the knowledge base",
        examples=["Engenharia de Software"],
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional description or domain summary",
        examples=["Manuais e documentações técnicas de microsserviços."],
    )


class KnowledgeBaseCreate(KnowledgeBaseBase):
    """Schema for creating a new Knowledge Base."""
    pass


class KnowledgeBaseUpdate(BaseModel):
    """Schema for updating an existing Knowledge Base."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class KnowledgeBaseResponse(KnowledgeBaseBase):
    """Response schema returning full Knowledge Base details."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Unique UUID identifier")
    document_count: int = Field(default=0, description="Total documents in this knowledge base")
    created_at: datetime = Field(..., description="Creation UTC timestamp")
    updated_at: datetime = Field(..., description="Last modification UTC timestamp")
