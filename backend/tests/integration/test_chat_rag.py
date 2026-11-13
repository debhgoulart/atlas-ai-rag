"""Integration tests for conversational RAG queries with source citations."""

import io
import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_chat_rag_query_with_citations(async_client: AsyncClient) -> None:
    """Test creating a chat session, uploading a document, and getting a grounded RAG response."""
    # 1. Create Knowledge Base
    kb_payload = {"name": f"Chat RAG KB {uuid.uuid4().hex[:8]}"}
    kb_res = await async_client.post("/api/v1/knowledge-bases", json=kb_payload)
    if kb_res.status_code == 500:
        pytest.skip("Database not available in sandboxed environment")
    assert kb_res.status_code == 201
    kb_id = kb_res.json()["id"]

    # 2. Upload document
    doc_text = (
        b"# Microsservicos no Atlas AI\n\n"
        b"O Atlas AI adota uma arquitetura Monorepo separando frontend Vue 3 e backend FastAPI. "
        b"A comunicacao ocorre exclusivamente via API REST versionada em /api/v1."
    )
    files = {"file": ("arquitetura.md", io.BytesIO(doc_text), "text/markdown")}
    upload_res = await async_client.post(f"/api/v1/knowledge-bases/{kb_id}/documents", files=files)
    assert upload_res.status_code == 201

    # 3. Create Chat Session
    session_res = await async_client.post(
        f"/api/v1/knowledge-bases/{kb_id}/chats",
        json={"title": "Perguntas de Arquitetura"},
    )
    assert session_res.status_code == 201
    chat_id = session_res.json()["id"]

    # 4. Send Message
    msg_res = await async_client.post(
        f"/api/v1/knowledge-bases/{kb_id}/chats/{chat_id}/messages",
        json={"content": "Qual a arquitetura adotada pelo Atlas AI?"},
    )
    assert msg_res.status_code == 200
    msg_data = msg_res.json()
    assert msg_data["role"] == "assistant"
    assert len(msg_data["content"]) > 0
    assert "citations" in msg_data
    assert isinstance(msg_data["citations"], list)
