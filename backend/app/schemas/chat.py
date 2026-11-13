"""Pydantic schemas for Chat Session and Message contracts."""

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ChatSessionCreate(BaseModel):
    """Payload for creating a new chat session."""

    title: Optional[str] = Field(
        default="Nova Conversa",
        max_length=150,
        description="Friendly title for the conversation",
        examples=["Perguntas sobre Arquitetura"],
    )


class CitationItem(BaseModel):
    """Source citation reference supporting an assistant response."""

    model_config = ConfigDict(from_attributes=True)

    chunk_id: uuid.UUID = Field(..., description="Referenced chunk UUID")
    document_id: uuid.UUID = Field(..., description="Parent document UUID")
    document_name: str = Field(..., description="Source document filename")
    chunk_index: int = Field(..., description="Sequential position in document")
    similarity_score: float = Field(..., description="Cosine similarity score (0.0 to 1.0)")
    content_snippet: str = Field(..., description="Preview text of the chunk")


class ChatMessageResponse(BaseModel):
    """Schema representing a single message in a conversation."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Message UUID")
    chat_session_id: uuid.UUID = Field(..., description="Parent chat session UUID")
    role: str = Field(..., description="Role of sender: 'user' or 'assistant'")
    content: str = Field(..., description="Message text content")
    citations: List[CitationItem] = Field(default_factory=list, description="Cited sources for assistant")
    prompt_tokens: Optional[int] = Field(None, description="Input tokens consumed")
    completion_tokens: Optional[int] = Field(None, description="Output tokens generated")
    latency_ms: Optional[int] = Field(None, description="Generation latency in milliseconds")
    created_at: datetime = Field(..., description="Message creation UTC timestamp")


class ChatSessionResponse(BaseModel):
    """Schema representing a chat session summary in lists."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Session UUID")
    knowledge_base_id: uuid.UUID = Field(..., description="Knowledge base UUID")
    title: str = Field(..., description="Session title")
    message_count: int = Field(default=0, description="Total messages in session")
    created_at: datetime = Field(..., description="Session creation UTC timestamp")
    updated_at: datetime = Field(..., description="Last update UTC timestamp")


class ChatSessionDetailResponse(BaseModel):
    """Schema representing full chat session details including chronological messages."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Session UUID")
    knowledge_base_id: uuid.UUID = Field(..., description="Knowledge base UUID")
    title: str = Field(..., description="Session title")
    messages: List[ChatMessageResponse] = Field(default_factory=list, description="Chronological message history")
    created_at: datetime = Field(..., description="Session creation UTC timestamp")
    updated_at: datetime = Field(..., description="Last update UTC timestamp")


class SendMessageRequest(BaseModel):
    """Payload for submitting a user message to receive a RAG response."""

    content: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User question or statement",
        examples=["Como funciona a recuperação vetorial no Atlas AI?"],
    )
