"""SQLAlchemy model for User entity."""

import uuid
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.chat_session import ChatSession
    from app.models.document import Document
    from app.models.knowledge_base import KnowledgeBase
    from app.models.user_gemini_credential import UserGeminiCredential


class User(Base, TimestampMixin):
    """User account entity for multi-tenant isolation and authentication."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # 1:1 relationship with UserGeminiCredential
    gemini_credential: Mapped[Optional["UserGeminiCredential"]] = relationship(
        "UserGeminiCredential",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Multi-tenant owned resources
    knowledge_bases: Mapped[List["KnowledgeBase"]] = relationship(
        "KnowledgeBase",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    documents: Mapped[List["Document"]] = relationship(
        "Document",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    chat_sessions: Mapped[List["ChatSession"]] = relationship(
        "ChatSession",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', active={self.is_active})>"
