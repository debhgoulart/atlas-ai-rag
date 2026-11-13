"""API endpoints for Chat Sessions, message sending, and conversational RAG history."""

import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.chat import (
    ChatMessageResponse,
    ChatSessionCreate,
    ChatSessionDetailResponse,
    ChatSessionResponse,
    SendMessageRequest,
)
from app.services.rag_chat_service import RAGChatService

router = APIRouter(prefix="/knowledge-bases/{kb_id}/chats", tags=["Conversational Chat & RAG"])

_chat_service = RAGChatService()


@router.post(
    "",
    response_model=ChatSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Chat Session",
)
async def create_chat_session(
    kb_id: uuid.UUID,
    payload: ChatSessionCreate = ChatSessionCreate(),
    db: AsyncSession = Depends(get_db),
) -> ChatSessionResponse:
    """Create a new conversational session linked to a Knowledge Base."""
    return await _chat_service.create_session(db, kb_id, payload.title)


@router.get(
    "",
    response_model=List[ChatSessionResponse],
    status_code=status.HTTP_200_OK,
    summary="List all Chat Sessions in a Knowledge Base",
)
async def list_chat_sessions(
    kb_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> List[ChatSessionResponse]:
    """Retrieve all chat sessions for the specified knowledge base, ordered by recent activity."""
    return await _chat_service.list_sessions(db, kb_id)


@router.get(
    "/{chat_id}",
    response_model=ChatSessionDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Chat Session details and full message history",
)
async def get_chat_session(
    kb_id: uuid.UUID,
    chat_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ChatSessionDetailResponse:
    """Retrieve chat session details along with chronological message history."""
    return await _chat_service.get_session_details(db, kb_id, chat_id)


@router.delete(
    "/{chat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Chat Session",
)
async def delete_chat_session(
    kb_id: uuid.UUID,
    chat_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a chat session and cascade delete all its messages."""
    await _chat_service.delete_session(db, kb_id, chat_id)


@router.post(
    "/{chat_id}/messages",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Send message and receive grounded RAG answer",
)
async def send_message(
    kb_id: uuid.UUID,
    chat_id: uuid.UUID,
    payload: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatMessageResponse:
    """Send user question, retrieve vector context from pgvector, and synthesize answer with source citations."""
    return await _chat_service.send_message(
        db=db,
        kb_id=kb_id,
        session_id=chat_id,
        user_content=payload.content,
    )
