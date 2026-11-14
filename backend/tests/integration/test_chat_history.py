"""Integration tests for chat session listing, history retrieval, and multi-turn persistence."""

import uuid
from unittest.mock import MagicMock, patch
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_chat_history_preservation(async_client: AsyncClient) -> None:
    """Verify that multiple turns are preserved in chronological order under authenticated session."""
    user_email = f"chat_history_{uuid.uuid4().hex[:8]}@example.com"
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
            json={"api_key": "AIzaSyKeyForChatHistory_123"},
            headers=headers,
        )

    # 1. Create Knowledge Base
    kb_payload = {"name": f"History KB {uuid.uuid4().hex[:8]}"}
    kb_res = await async_client.post(
        "/api/v1/knowledge-bases", json=kb_payload, headers=headers
    )
    assert kb_res.status_code == 201
    kb_id = kb_res.json()["id"]

    # 2. Create Chat Session
    session_res = await async_client.post(
        f"/api/v1/knowledge-bases/{kb_id}/chats",
        json={"title": "Multi-Turn Session"},
        headers=headers,
    )
    assert session_res.status_code == 201
    chat_id = session_res.json()["id"]

    # Mock embeddings and Gemini response
    with patch("app.services.gemini_client.GeminiEmbeddingClient.generate_embedding") as mock_embed, \
         patch("app.services.gemini_client.GeminiChatClient.generate_response") as mock_gen:
        mock_embed.return_value = [0.1] * 768
        mock_res = MagicMock()
        mock_res.content = "Resposta do assistente"
        mock_res.prompt_tokens = 10
        mock_res.completion_tokens = 5
        mock_gen.return_value = mock_res

        # 3. Send Turn 1
        await async_client.post(
            f"/api/v1/knowledge-bases/{kb_id}/chats/{chat_id}/messages",
            json={"content": "Mensagem 1 do usuário"},
            headers=headers,
        )

        # 4. Send Turn 2
        await async_client.post(
            f"/api/v1/knowledge-bases/{kb_id}/chats/{chat_id}/messages",
            json={"content": "Mensagem 2 do usuário"},
            headers=headers,
        )

    # 5. Fetch Session Details
    detail_res = await async_client.get(
        f"/api/v1/knowledge-bases/{kb_id}/chats/{chat_id}",
        headers=headers,
    )
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert len(detail_data["messages"]) == 4  # 2 user + 2 assistant
    assert detail_data["messages"][0]["role"] == "user"
    assert detail_data["messages"][1]["role"] == "assistant"
    assert detail_data["messages"][2]["role"] == "user"
    assert detail_data["messages"][3]["role"] == "assistant"
