"""SQLAlchemy model for ChatSession entity."""

import uuid
from typing import TYPE_CHECKING, List
from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.knowledge_base import KnowledgeBase
    from app.models.chat_message import ChatMessage
    from app.models.user import User


class ChatSession(Base, TimestampMixin):
    """Chat session entity representing an ongoing conversation scoped to a Knowledge Base and User."""

    __tablename__ = "chat_sessions"
    __table_args__ = (
        Index("ix_chat_sessions_user_kb", "user_id", "knowledge_base_id"),
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
    knowledge_base_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_bases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(150),
        default="Nova Conversa",
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User")
    knowledge_base: Mapped["KnowledgeBase"] = relationship(
        "KnowledgeBase",
    )
    messages: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<ChatSession(id={self.id}, user_id={self.user_id}, title='{self.title}', kb_id={self.knowledge_base_id})>"
