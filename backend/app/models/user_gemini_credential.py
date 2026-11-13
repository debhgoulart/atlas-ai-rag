"""SQLAlchemy model for UserGeminiCredential entity."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class UserGeminiCredential(Base, TimestampMixin):
    """Encrypted Gemini API credential associated exclusively with a user account."""

    __tablename__ = "user_gemini_credentials"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    encrypted_api_key: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    key_hint: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="NOT_CONFIGURED",
        nullable=False,
        index=True,
    )
    last_validated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationship to parent User
    user: Mapped["User"] = relationship(
        "User",
        back_populates="gemini_credential",
    )

    def __repr__(self) -> str:
        return f"<UserGeminiCredential(id={self.id}, user_id={self.user_id}, status='{self.status}')>"
