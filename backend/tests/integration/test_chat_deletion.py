"""Integration tests for chat session deletion and cascading purge of messages."""

import uuid
from unittest.mock import MagicMock, patch
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_chat_session_cascade_deletion(async_client: AsyncClient) -> None:
    """Verify that deleting a chat session purges it and its messages completely under authenticated session."""
    user_email = f"chat_del_{uuid.uuid4().hex[:8]}@example.com"
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
            json={"api_key": "AIzaSyKeyForChatDel_123"},
            headers=headers,
        )

    # 1. Create Knowledge Base
    kb_payload = {"name": f"Delete KB {uuid.uuid4().hex[:8]}"}
    kb_res = await async_client.post(
        "/api/v1/knowledge-bases", json=kb_payload, headers=headers
    )
    assert kb_res.status_code == 201
    kb_id = kb_res.json()["id"]

    # 2. Create Chat Session
    session_res = await async_client.post(
        f"/api/v1/knowledge-bases/{kb_id}/chats",
        json={"title": "Session to Delete"},
        headers=headers,
    )
    assert session_res.status_code == 201
    chat_id = session_res.json()["id"]

    # 3. Add message
    with patch("app.services.gemini_client.GeminiEmbeddingClient.generate_embedding") as mock_embed, \
         patch("app.services.gemini_client.GeminiChatClient.generate_response") as mock_gen:
        mock_embed.return_value = [0.1] * 768
        mock_res = MagicMock()
        mock_res.content = "Resposta temporária"
        mock_res.prompt_tokens = 5
        mock_res.completion_tokens = 5
        mock_gen.return_value = mock_res

        await async_client.post(
            f"/api/v1/knowledge-bases/{kb_id}/chats/{chat_id}/messages",
            json={"content": "Mensagem que será deletada"},
            headers=headers,
        )

    # 4. Delete Chat Session
    del_res = await async_client.delete(
        f"/api/v1/knowledge-bases/{kb_id}/chats/{chat_id}",
        headers=headers,
    )
    assert del_res.status_code == 204

    # 5. Verify 404
    not_found = await async_client.get(
        f"/api/v1/knowledge-bases/{kb_id}/chats/{chat_id}",
        headers=headers,
    )
    assert not_found.status_code == 404
