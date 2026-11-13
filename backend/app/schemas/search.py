"""Pydantic schemas for semantic similarity search contracts."""

import uuid
from pydantic import BaseModel, ConfigDict, Field


class SimilaritySearchRequest(BaseModel):
    """Payload schema for running vector similarity queries."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Natural language query string",
        examples=["Como funciona o algoritmo de busca vetorial?"],
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of relevant chunks to return",
    )
    similarity_threshold: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum cosine similarity score (0.0 to 1.0)",
    )


class SimilaritySearchResult(BaseModel):
    """Schema returned for each matching vector chunk."""

    model_config = ConfigDict(from_attributes=True)

    chunk_id: uuid.UUID = Field(..., description="Chunk unique UUID")
    document_id: uuid.UUID = Field(..., description="Source document UUID")
    document_name: str = Field(..., description="Source document filename")
    chunk_index: int = Field(..., description="Sequential position in source document")
    content: str = Field(..., description="Text content slice of the chunk")
    similarity_score: float = Field(..., description="Cosine similarity score (0.0 to 1.0)")
