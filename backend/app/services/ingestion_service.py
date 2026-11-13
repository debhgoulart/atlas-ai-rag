"""Service orchestrating document ingestion, chunking, embeddings, and vector similarity search."""

import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import EntityNotFoundException
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.knowledge_base import KnowledgeBase
from app.schemas.document import DocumentResponse, DocumentStatusEnum
from app.schemas.search import SimilaritySearchResult
from app.services.document_parser import DocumentParser
from app.services.gemini_client import GeminiEmbeddingClient
from app.services.text_chunker import RecursiveTextChunker


class IngestionService:
    """Orchestrates end-to-end ingestion and vector search pipelines."""

    def __init__(
        self,
        embedding_client: Optional[GeminiEmbeddingClient] = None,
        chunker: Optional[RecursiveTextChunker] = None,
    ) -> None:
        self.embedding_client = embedding_client or GeminiEmbeddingClient()
        self.chunker = chunker or RecursiveTextChunker(
            chunk_size=settings.DEFAULT_CHUNK_SIZE,
            chunk_overlap=settings.DEFAULT_CHUNK_OVERLAP,
        )

    async def ingest_document(
        self,
        db: AsyncSession,
        kb_id: uuid.UUID,
        filename: str,
        content_type: str,
        file_bytes: bytes,
        api_key: Optional[str] = None,
    ) -> DocumentResponse:
        """Validate, extract, chunk, embed, and persist an uploaded document."""
        # 1. Verify Knowledge Base exists
        kb_stmt = select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
        kb_res = await db.execute(kb_stmt)
        if not kb_res.scalar_one_or_none():
            raise EntityNotFoundException("KnowledgeBase", kb_id)

        # 2. Validate file metadata
        file_size = len(file_bytes)
        extension = DocumentParser.validate_file(
            filename=filename,
            content_type=content_type,
            file_size=file_size,
            max_bytes=settings.max_upload_size_bytes,
        )

        # 3. Create initial document record with 'processing' state
        doc = Document(
            knowledge_base_id=kb_id,
            filename=filename,
            content_type=content_type,
            file_size_bytes=file_size,
            status=DocumentStatusEnum.PROCESSING.value,
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)

        try:
            # 4. Extract text content
            text, metadata = DocumentParser.extract_text(file_bytes, extension)

            # 5. Split text into chunks
            text_chunks = self.chunker.split_text(text)
            if not text_chunks:
                raise ValueError("No valid text chunks could be produced from document content.")

            # 6. Generate dense vector embeddings via Gemini API
            chunk_texts = [c.content for c in text_chunks]
            embedder = GeminiEmbeddingClient(api_key=api_key) if api_key else self.embedding_client
            embeddings = await embedder.generate_embeddings_batch(
                chunk_texts, task_type="RETRIEVAL_DOCUMENT"
            )

            # 7. Persist DocumentChunk instances
            for tc, emb in zip(text_chunks, embeddings):
                chunk_obj = DocumentChunk(
                    document_id=doc.id,
                    knowledge_base_id=kb_id,
                    chunk_index=tc.index,
                    content=tc.content,
                    embedding=emb,
                    chunk_metadata={
                        **metadata,
                        "char_start": tc.char_start,
                        "char_end": tc.char_end,
                    },
                )
                db.add(chunk_obj)

            # 8. Mark document as completed
            doc.status = DocumentStatusEnum.COMPLETED.value
            doc.chunk_count = len(text_chunks)
            await db.commit()
            await db.refresh(doc)

            return DocumentResponse.model_validate(doc)

        except Exception as exc:
            # Mark document as failed with reason
            doc.status = DocumentStatusEnum.FAILED.value
            doc.error_message = str(exc)
            await db.commit()
            await db.refresh(doc)
            raise

    async def list_documents(self, db: AsyncSession, kb_id: uuid.UUID) -> List[DocumentResponse]:
        """List all documents for a given knowledge base."""
        # Verify knowledge base exists
        kb_stmt = select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
        kb_res = await db.execute(kb_stmt)
        if not kb_res.scalar_one_or_none():
            raise EntityNotFoundException("KnowledgeBase", kb_id)

        stmt = select(Document).where(Document.knowledge_base_id == kb_id).order_by(Document.created_at.desc())
        result = await db.execute(stmt)
        docs = result.scalars().all()
        return [DocumentResponse.model_validate(d) for d in docs]

    async def get_document(self, db: AsyncSession, kb_id: uuid.UUID, doc_id: uuid.UUID) -> DocumentResponse:
        """Fetch details of a single document."""
        stmt = select(Document).where(
            Document.id == doc_id, Document.knowledge_base_id == kb_id
        )
        result = await db.execute(stmt)
        doc = result.scalar_one_or_none()
        if not doc:
            raise EntityNotFoundException("Document", doc_id)
        return DocumentResponse.model_validate(doc)

    async def delete_document(self, db: AsyncSession, kb_id: uuid.UUID, doc_id: uuid.UUID) -> None:
        """Delete document and cascade remove all its vector chunks."""
        stmt = select(Document).where(
            Document.id == doc_id, Document.knowledge_base_id == kb_id
        )
        result = await db.execute(stmt)
        doc = result.scalar_one_or_none()
        if not doc:
            raise EntityNotFoundException("Document", doc_id)

        await db.delete(doc)
        await db.commit()

    async def search_similar_chunks(
        self,
        db: AsyncSession,
        kb_id: uuid.UUID,
        query: str,
        limit: int = 5,
        similarity_threshold: float = 0.0,
        api_key: Optional[str] = None,
    ) -> List[SimilaritySearchResult]:
        """Perform cosine similarity search against pgvector chunks."""
        # 1. Verify knowledge base exists
        kb_stmt = select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
        kb_res = await db.execute(kb_stmt)
        if not kb_res.scalar_one_or_none():
            raise EntityNotFoundException("KnowledgeBase", kb_id)

        # 2. Generate embedding for search query (RETRIEVAL_QUERY task type)
        embedder = GeminiEmbeddingClient(api_key=api_key) if api_key else self.embedding_client
        query_embedding = await embedder.generate_embedding(
            query, task_type="RETRIEVAL_QUERY"
        )

        # 3. Query pgvector using cosine distance operator `<=>`
        # Cosine distance = 1 - cosine_similarity. Similarity = 1 - distance.
        distance_col = DocumentChunk.embedding.cosine_distance(query_embedding).label("distance")

        stmt = (
            select(
                DocumentChunk,
                Document.filename.label("document_name"),
                distance_col,
            )
            .join(Document, Document.id == DocumentChunk.document_id)
            .where(DocumentChunk.knowledge_base_id == kb_id)
            .order_by(distance_col)
            .limit(limit)
        )

        result = await db.execute(stmt)
        rows = result.all()

        search_results: List[SimilaritySearchResult] = []
        for chunk, doc_name, distance in rows:
            similarity = round(1.0 - float(distance), 4)
            if similarity >= similarity_threshold:
                search_results.append(
                    SimilaritySearchResult(
                        chunk_id=chunk.id,
                        document_id=chunk.document_id,
                        document_name=doc_name,
                        chunk_index=chunk.chunk_index,
                        content=chunk.content,
                        similarity_score=similarity,
                    )
                )

        return search_results
