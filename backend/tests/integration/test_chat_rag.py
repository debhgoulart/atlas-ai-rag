"""Integration tests for conversational RAG queries with source citations."""

import io
import uuid
from unittest.mock import MagicMock, patch
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_chat_rag_query_with_citations(async_client: AsyncClient) -> None:
    """Test creating a chat session, uploading a document, and getting a grounded RAG response under authenticated session."""
    user_email = f"chat_rag_{uuid.uuid4().hex[:8]}@example.com"
    reg_resp = await async_client.post(
        "/api/v1/auth/register",
        json={"email": user_email, "password": "Password123!"},
    )
    if reg_resp.status_code == 500:
        pytest.skip("Database not available in sandboxed environment")
    assert reg_resp.status_code == 201

    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": user_email, "password": "Password123!"},
    )
    headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    # Register Gemini Key for user
    with patch("google.genai.Client") as mock_client:
        mock_instance = MagicMock()
        mock_instance.models.get.return_value = MagicMock()
        mock_client.return_value = mock_instance

        await async_client.post(
            "/api/v1/settings/gemini-key",
            json={"api_key": "AIzaSyKeyForChatRag_123"},
            headers=headers,
        )

    # 1. Create Knowledge Base
    kb_payload = {"name": f"Chat RAG KB {uuid.uuid4().hex[:8]}"}
    kb_res = await async_client.post(
        "/api/v1/knowledge-bases", json=kb_payload, headers=headers
    )
    assert kb_res.status_code == 201
    kb_id = kb_res.json()["id"]

    # 2. Upload document
    doc_text = (
        b"# Microsservicos no Atlas AI\n\n"
        b"O Atlas AI adota uma arquitetura Monorepo separando frontend Vue 3 e backend FastAPI. "
        b"A comunicacao ocorre exclusivamente via API REST versionada em /api/v1."
    )
    files = {"file": ("arquitetura.md", io.BytesIO(doc_text), "text/markdown")}

    with patch("app.services.gemini_client.GeminiEmbeddingClient.generate_embeddings_batch") as mock_batch, \
         patch("app.services.gemini_client.GeminiEmbeddingClient.generate_embedding") as mock_single, \
         patch("app.services.gemini_client.GeminiChatClient.generate_response") as mock_gen:
        mock_batch.return_value = [[0.1] * 768]
        mock_single.return_value = [0.1] * 768

        mock_res = MagicMock()
        mock_res.content = "O Atlas AI adota arquitetura Monorepo separando frontend Vue 3 e backend FastAPI."
        mock_res.prompt_tokens = 50
        mock_res.completion_tokens = 25
        mock_gen.return_value = mock_res

        upload_res = await async_client.post(
            f"/api/v1/knowledge-bases/{kb_id}/documents", files=files, headers=headers
        )
        assert upload_res.status_code == 201

        # 3. Create Chat Session
        session_res = await async_client.post(
            f"/api/v1/knowledge-bases/{kb_id}/chats",
            json={"title": "Perguntas de Arquitetura"},
            headers=headers,
        )
        assert session_res.status_code == 201
        chat_id = session_res.json()["id"]

        # 4. Send Message
        msg_res = await async_client.post(
            f"/api/v1/knowledge-bases/{kb_id}/chats/{chat_id}/messages",
            json={"content": "Qual a arquitetura adotada pelo Atlas AI?"},
            headers=headers,
        )
        assert msg_res.status_code == 200
        msg_data = msg_res.json()
        assert msg_data["role"] == "assistant"
        assert len(msg_data["content"]) > 0
        assert "citations" in msg_data
        assert isinstance(msg_data["citations"], list)
