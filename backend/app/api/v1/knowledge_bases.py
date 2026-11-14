"""API endpoints for Knowledge Base operations (Scoped to Authenticated User)."""

import uuid
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> KnowledgeBaseResponse:
    """Create a new isolated knowledge base collection belonging to the authenticated user."""
    return await KnowledgeBaseService.create(db, payload, user_id=current_user.id)


@router.get(
    "",
    response_model=List[KnowledgeBaseResponse],
    status_code=status.HTTP_200_OK,
    summary="List all Knowledge Bases",
)
async def list_knowledge_bases(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Limit for pagination"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[KnowledgeBaseResponse]:
    """Retrieve all knowledge bases belonging strictly to the authenticated user."""
    return await KnowledgeBaseService.list_all(db, user_id=current_user.id, skip=skip, limit=limit)


@router.get(
    "/{kb_id}",
    response_model=KnowledgeBaseResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Knowledge Base by ID",
)
async def get_knowledge_base(
    kb_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> KnowledgeBaseResponse:
    """Retrieve details of a specific knowledge base if owned by the authenticated user."""
    return await KnowledgeBaseService.get_by_id(db, kb_id, user_id=current_user.id)


@router.delete(
    "/{kb_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Knowledge Base",
)
async def delete_knowledge_base(
    kb_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a knowledge base if owned by the authenticated user, cascading all documents and chunks."""
    await KnowledgeBaseService.delete(db, kb_id, user_id=current_user.id)
