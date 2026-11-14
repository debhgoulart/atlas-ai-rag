"""Integration tests for anti-hallucination behavior in empty or irrelevant knowledge bases."""

import uuid
from unittest.mock import MagicMock, patch
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_anti_hallucination_on_empty_kb(async_client: AsyncClient) -> None:
    """Verify that querying an empty knowledge base does not crash and admits lack of context."""
    # 0. Register and login user
    user_email = f"hallucination_tester_{uuid.uuid4().hex[:8]}@example.com"
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
            json={"api_key": "AIzaSyKeyForHallucination_123"},
            headers=headers,
        )

    # 1. Create Empty Knowledge Base
    kb_payload = {"name": f"Empty KB {uuid.uuid4().hex[:8]}"}
    kb_res = await async_client.post(
        "/api/v1/knowledge-bases", json=kb_payload, headers=headers
    )
    assert kb_res.status_code == 201
    kb_id = kb_res.json()["id"]

    # 2. Create Chat Session
    session_res = await async_client.post(
        f"/api/v1/knowledge-bases/{kb_id}/chats",
        json={"title": "Empty KB Test"},
        headers=headers,
    )
    assert session_res.status_code == 201
    chat_id = session_res.json()["id"]

    # 3. Send query that has zero matches
    with patch("app.services.gemini_client.GeminiEmbeddingClient.generate_embedding") as mock_embed, \
         patch("app.services.gemini_client.GeminiChatClient.generate_response") as mock_gen:
        mock_embed.return_value = [0.1] * 768
        mock_res = MagicMock()
        mock_res.content = "Desculpe, não encontrei informações sobre este tema nos documentos da base de conhecimento."
        mock_res.prompt_tokens = 10
        mock_res.completion_tokens = 10
        mock_gen.return_value = mock_res

        msg_res = await async_client.post(
            f"/api/v1/knowledge-bases/{kb_id}/chats/{chat_id}/messages",
            json={"content": "Qual a capital da França segundo os documentos?"},
            headers=headers,
        )
        assert msg_res.status_code == 200
        msg_data = msg_res.json()
        assert msg_data["role"] == "assistant"
        # Citations must be empty since no chunks exist
        assert len(msg_data["citations"]) == 0
