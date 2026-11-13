"""API endpoints for Document ingestion, lifecycle management, and semantic search."""

import uuid
from typing import List
from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_user_gemini_api_key
from app.db.session import get_db
from app.schemas.document import DocumentResponse
from app.schemas.search import SimilaritySearchRequest, SimilaritySearchResult
from app.services.ingestion_service import IngestionService

router = APIRouter(prefix="/knowledge-bases/{kb_id}", tags=["Documents & RAG"])

_ingestion_service = IngestionService()


@router.post(
    "/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and ingest a document",
)
async def upload_document(
    kb_id: uuid.UUID,
    file: UploadFile = File(..., description="PDF, TXT, or Markdown document (max 10 MB)"),
    user_api_key: str = Depends(get_user_gemini_api_key),
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    """Upload a document, extract text, generate chunked embeddings, and index into pgvector."""
    file_bytes = await file.read()
    filename = file.filename or "uploaded_file"
    content_type = file.content_type or "application/octet-stream"

    return await _ingestion_service.ingest_document(
        db=db,
        kb_id=kb_id,
        filename=filename,
        content_type=content_type,
        file_bytes=file_bytes,
        api_key=user_api_key,
    )


@router.get(
    "/documents",
    response_model=List[DocumentResponse],
    status_code=status.HTTP_200_OK,
    summary="List all documents in a Knowledge Base",
)
async def list_documents(
    kb_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> List[DocumentResponse]:
    """Retrieve all documents belonging to the specified knowledge base."""
    return await _ingestion_service.list_documents(db, kb_id)


@router.get(
    "/documents/{doc_id}",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get document details and processing status",
)
async def get_document(
    kb_id: uuid.UUID,
    doc_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    """Retrieve details and chunk counts of a specific document."""
    return await _ingestion_service.get_document(db, kb_id, doc_id)


@router.delete(
    "/documents/{doc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete document and its vector chunks",
)
async def delete_document(
    kb_id: uuid.UUID,
    doc_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a document and cascade purge all its associated vector embeddings."""
    await _ingestion_service.delete_document(db, kb_id, doc_id)


@router.post(
    "/search",
    response_model=List[SimilaritySearchResult],
    status_code=status.HTTP_200_OK,
    summary="Probe semantic similarity search on knowledge base",
)
async def search_knowledge_base(
    kb_id: uuid.UUID,
    payload: SimilaritySearchRequest,
    user_api_key: str = Depends(get_user_gemini_api_key),
    db: AsyncSession = Depends(get_db),
) -> List[SimilaritySearchResult]:
    """Perform cosine similarity vector retrieval against document chunks in the knowledge base."""
    return await _ingestion_service.search_similar_chunks(
        db=db,
        kb_id=kb_id,
        query=payload.query,
        limit=payload.limit,
        similarity_threshold=payload.similarity_threshold,
        api_key=user_api_key,
    )
