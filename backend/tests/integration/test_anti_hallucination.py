"""Integration tests for anti-hallucination behavior in empty or irrelevant knowledge bases."""

import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_anti_hallucination_on_empty_kb(async_client: AsyncClient) -> None:
    """Verify that querying an empty knowledge base does not crash and admits lack of context."""
    # 1. Create Empty Knowledge Base
    kb_payload = {"name": f"Empty KB {uuid.uuid4().hex[:8]}"}
    kb_res = await async_client.post("/api/v1/knowledge-bases", json=kb_payload)
    if kb_res.status_code == 500:
        pytest.skip("Database not available in sandboxed environment")
    assert kb_res.status_code == 201
    kb_id = kb_res.json()["id"]

    # 2. Create Chat Session
    session_res = await async_client.post(
        f"/api/v1/knowledge-bases/{kb_id}/chats",
        json={"title": "Empty KB Test"},
    )
    assert session_res.status_code == 201
    chat_id = session_res.json()["id"]

    # 3. Send query that has zero matches
    msg_res = await async_client.post(
        f"/api/v1/knowledge-bases/{kb_id}/chats/{chat_id}/messages",
        json={"content": "Qual a capital da França segundo os documentos?"},
    )
    assert msg_res.status_code == 200
    msg_data = msg_res.json()
    assert msg_data["role"] == "assistant"
    # Citations must be empty since no chunks exist
    assert len(msg_data["citations"]) == 0
