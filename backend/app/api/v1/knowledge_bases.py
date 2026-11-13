"""API endpoints for Knowledge Base operations."""

import uuid
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseResponse
from app.services.knowledge_base_service import KnowledgeBaseService

router = APIRouter(prefix="/knowledge-bases", tags=["Knowledge Bases"])


@router.post(
    "",
    response_model=KnowledgeBaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Knowledge Base",
)
async def create_knowledge_base(
    payload: KnowledgeBaseCreate,
    db: AsyncSession = Depends(get_db),
) -> KnowledgeBaseResponse:
    """Create a new isolated knowledge base collection."""
    return await KnowledgeBaseService.create(db, payload)


@router.get(
    "",
    response_model=List[KnowledgeBaseResponse],
    status_code=status.HTTP_200_OK,
    summary="List all Knowledge Bases",
)
async def list_knowledge_bases(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Limit for pagination"),
    db: AsyncSession = Depends(get_db),
) -> List[KnowledgeBaseResponse]:
    """Retrieve all knowledge bases with document counts."""
    return await KnowledgeBaseService.list_all(db, skip=skip, limit=limit)


@router.get(
    "/{kb_id}",
    response_model=KnowledgeBaseResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Knowledge Base by ID",
)
async def get_knowledge_base(
    kb_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> KnowledgeBaseResponse:
    """Retrieve details of a specific knowledge base."""
    return await KnowledgeBaseService.get_by_id(db, kb_id)


@router.delete(
    "/{kb_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Knowledge Base",
)
async def delete_knowledge_base(
    kb_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a knowledge base and cascade delete all its documents and vector chunks."""
    await KnowledgeBaseService.delete(db, kb_id)
