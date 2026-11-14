"""SQLAlchemy model for Document Chunk entity with pgvector embedding."""

import uuid
from typing import TYPE_CHECKING, Any, Dict
from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Index, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.user import User


class DocumentChunk(Base, TimestampMixin):
    """Document Chunk entity containing slice text and dense vector embedding."""

    __tablename__ = "document_chunks"
    __table_args__ = (
        Index("ix_document_chunks_user_kb", "user_id", "knowledge_base_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    knowledge_base_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_bases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    # Dense vector embedding using pgvector extension (768 dimensions for Gemini gemini-embedding-001)
    embedding = mapped_column(
        Vector(settings.EMBEDDING_DIMENSION),
        nullable=False,
    )
    chunk_metadata: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User")
    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="chunks",
    )

    def __repr__(self) -> str:
        return f"<DocumentChunk(id={self.id}, user_id={self.user_id}, doc_id={self.document_id}, index={self.chunk_index})>"
