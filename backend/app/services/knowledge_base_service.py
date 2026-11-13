"""Business logic service for managing Knowledge Bases."""

import uuid
from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateEntityException, EntityNotFoundException
from app.models.knowledge_base import KnowledgeBase
from app.models.document import Document
from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseResponse, KnowledgeBaseUpdate


class KnowledgeBaseService:
    """Service handling CRUD operations and queries for Knowledge Bases."""

    @staticmethod
    async def create(db: AsyncSession, data: KnowledgeBaseCreate) -> KnowledgeBaseResponse:
        """Create a new Knowledge Base ensuring unique name."""
        # Check for existing knowledge base with same name
        stmt = select(KnowledgeBase).where(KnowledgeBase.name == data.name)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            raise DuplicateEntityException(
                entity_name="KnowledgeBase",
                field="name",
                value=data.name,
            )

        kb = KnowledgeBase(
            name=data.name,
            description=data.description,
        )
        db.add(kb)
        await db.commit()
        await db.refresh(kb)

        return KnowledgeBaseResponse(
            id=kb.id,
            name=kb.name,
            description=kb.description,
            document_count=0,
            created_at=kb.created_at,
            updated_at=kb.updated_at,
        )

    @staticmethod
    async def get_by_id(db: AsyncSession, kb_id: uuid.UUID) -> KnowledgeBaseResponse:
        """Fetch a knowledge base by ID, computing document count."""
        stmt = (
            select(
                KnowledgeBase,
                func.count(Document.id).label("doc_count"),
            )
            .outerjoin(Document, Document.knowledge_base_id == KnowledgeBase.id)
            .where(KnowledgeBase.id == kb_id)
            .group_by(KnowledgeBase.id)
        )
        result = await db.execute(stmt)
        row = result.first()
        if not row:
            raise EntityNotFoundException("KnowledgeBase", kb_id)

        kb, doc_count = row
        return KnowledgeBaseResponse(
            id=kb.id,
            name=kb.name,
            description=kb.description,
            document_count=doc_count,
            created_at=kb.created_at,
            updated_at=kb.updated_at,
        )

    @staticmethod
    async def list_all(
        db: AsyncSession, skip: int = 0, limit: int = 20
    ) -> List[KnowledgeBaseResponse]:
        """List knowledge bases with pagination and document counts."""
        stmt = (
            select(
                KnowledgeBase,
                func.count(Document.id).label("doc_count"),
            )
            .outerjoin(Document, Document.knowledge_base_id == KnowledgeBase.id)
            .group_by(KnowledgeBase.id)
            .order_by(KnowledgeBase.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        rows = result.all()

        return [
            KnowledgeBaseResponse(
                id=kb.id,
                name=kb.name,
                description=kb.description,
                document_count=doc_count,
                created_at=kb.created_at,
                updated_at=kb.updated_at,
            )
            for kb, doc_count in rows
        ]

    @staticmethod
    async def delete(db: AsyncSession, kb_id: uuid.UUID) -> None:
        """Delete a knowledge base and cascade all documents and vector chunks."""
        stmt = select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
        result = await db.execute(stmt)
        kb = result.scalar_one_or_none()
        if not kb:
            raise EntityNotFoundException("KnowledgeBase", kb_id)

        await db.delete(kb)
        await db.commit()
