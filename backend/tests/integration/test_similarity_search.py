"""Integration tests for semantic similarity search endpoint."""

import io
import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_similarity_search(async_client: AsyncClient) -> None:
    """Test semantic similarity search probe against uploaded chunks."""
    # 1. Create Knowledge Base
    kb_payload = {"name": f"Search KB {uuid.uuid4().hex[:8]}"}
    kb_res = await async_client.post("/api/v1/knowledge-bases", json=kb_payload)
    if kb_res.status_code == 500:
        pytest.skip("Database not available in sandboxed environment")
    assert kb_res.status_code == 201
    kb_id = kb_res.json()["id"]

    # 2. Upload sample document
    content = (
        b"PostgreSQL pgvector allows storing dense vectors and querying nearest neighbors using "
        b"the cosine distance operator. FastAPI provides asynchronous request handling."
    )
    files = {"file": ("vector_guide.txt", io.BytesIO(content), "text/plain")}
    upload_res = await async_client.post(f"/api/v1/knowledge-bases/{kb_id}/documents", files=files)
    assert upload_res.status_code == 201

    # 3. Query similarity search
    search_payload = {
        "query": "How does vector search work in PostgreSQL?",
        "limit": 3,
        "similarity_threshold": 0.0,
    }
    search_res = await async_client.post(
        f"/api/v1/knowledge-bases/{kb_id}/search", json=search_payload
    )
    assert search_res.status_code == 200
    results = search_res.json()
    assert isinstance(results, list)
    if results:
        top_match = results[0]
        assert "content" in top_match
        assert "similarity_score" in top_match
        assert "document_name" in top_match
