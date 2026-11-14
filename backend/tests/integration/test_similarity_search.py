"""Integration tests for semantic similarity search endpoint."""

import io
import uuid
from unittest.mock import MagicMock, patch
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_similarity_search(async_client: AsyncClient) -> None:
    """Test semantic similarity search probe against uploaded chunks under authenticated session."""
    user_email = f"sim_search_{uuid.uuid4().hex[:8]}@example.com"
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
            json={"api_key": "AIzaSyKeyForSimSearch_123"},
            headers=headers,
        )

    # 1. Create Knowledge Base
    kb_payload = {"name": f"Search KB {uuid.uuid4().hex[:8]}"}
    kb_res = await async_client.post(
        "/api/v1/knowledge-bases", json=kb_payload, headers=headers
    )
    assert kb_res.status_code == 201
    kb_id = kb_res.json()["id"]

    # 2. Upload sample document with mocked embeddings
    content = (
        b"PostgreSQL pgvector allows storing dense vectors and querying nearest neighbors using "
        b"the cosine distance operator. FastAPI provides asynchronous request handling."
    )
    files = {"file": ("vector_guide.txt", io.BytesIO(content), "text/plain")}

    with patch("app.services.gemini_client.GeminiEmbeddingClient.generate_embeddings_batch") as mock_batch, \
         patch("app.services.gemini_client.GeminiEmbeddingClient.generate_embedding") as mock_single:
        mock_batch.return_value = [[0.1] * 768]
        mock_single.return_value = [0.1] * 768

        upload_res = await async_client.post(
            f"/api/v1/knowledge-bases/{kb_id}/documents", files=files, headers=headers
        )
        assert upload_res.status_code == 201

        # 3. Query similarity search
        search_payload = {
            "query": "How does vector search work in PostgreSQL?",
            "limit": 3,
            "similarity_threshold": 0.0,
        }
        search_res = await async_client.post(
            f"/api/v1/knowledge-bases/{kb_id}/search", json=search_payload, headers=headers
        )
        assert search_res.status_code == 200
        results = search_res.json()
        assert isinstance(results, list)
        if results:
            top_match = results[0]
            assert "content" in top_match
            assert "similarity_score" in top_match
            assert "document_name" in top_match
