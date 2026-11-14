"""SQLAlchemy model for Knowledge Base entity."""

import uuid
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.user import User


class KnowledgeBase(Base, TimestampMixin):
    """Knowledge Base entity representing an isolated topical collection belonging to a user."""

    __tablename__ = "knowledge_bases"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_knowledge_bases_user_id_name"),
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
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship("User")
    documents: Mapped[List["Document"]] = relationship(
        "Document",
        back_populates="knowledge_base",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<KnowledgeBase(id={self.id}, user_id={self.user_id}, name='{self.name}')>"
