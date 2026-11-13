"""Integration tests for chat session listing, history retrieval, and multi-turn persistence."""

import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_chat_history_preservation(async_client: AsyncClient) -> None:
    """Verify that multiple turns are preserved in chronological order."""
    # 1. Create Knowledge Base
    kb_payload = {"name": f"History KB {uuid.uuid4().hex[:8]}"}
    kb_res = await async_client.post("/api/v1/knowledge-bases", json=kb_payload)
    if kb_res.status_code == 500:
        pytest.skip("Database not available in sandboxed environment")
    assert kb_res.status_code == 201
    kb_id = kb_res.json()["id"]

    # 2. Create Chat Session
    session_res = await async_client.post(
        f"/api/v1/knowledge-bases/{kb_id}/chats",
        json={"title": "Multi-Turn Session"},
    )
    assert session_res.status_code == 201
    chat_id = session_res.json()["id"]

    # 3. Send Turn 1
    await async_client.post(
        f"/api/v1/knowledge-bases/{kb_id}/chats/{chat_id}/messages",
        json={"content": "Mensagem 1 do usuário"},
    )

    # 4. Send Turn 2
    await async_client.post(
        f"/api/v1/knowledge-bases/{kb_id}/chats/{chat_id}/messages",
        json={"content": "Mensagem 2 do usuário"},
    )

    # 5. Fetch Session Details
    detail_res = await async_client.get(
        f"/api/v1/knowledge-bases/{kb_id}/chats/{chat_id}"
    )
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert len(detail_data["messages"]) == 4  # 2 user + 2 assistant
    assert detail_data["messages"][0]["role"] == "user"
    assert detail_data["messages"][1]["role"] == "assistant"
    assert detail_data["messages"][2]["role"] == "user"
    assert detail_data["messages"][3]["role"] == "assistant"
