"""Integration tests verifying user's decrypted key is passed to Gemini RAG execution."""

import uuid
from unittest.mock import MagicMock, patch
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_rag_chat_uses_user_decrypted_key(async_client: AsyncClient) -> None:
    """Ensure user's key is decrypted in memory and passed to Gemini client for synthesis."""
    email = f"validuser_{uuid.uuid4().hex[:8]}@example.com"
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!"},
    )
    if reg.status_code == 500:
        pytest.skip("Database not available in sandbox environment")

    login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    user_raw_key = "AIzaSyUserSpecificKey_XYZ987654321"

    # Save user key (mocking Google validation)
    with patch("google.genai.Client") as mock_client:
        mock_instance = MagicMock()
        mock_instance.models.get.return_value = MagicMock()
        mock_client.return_value = mock_instance

        key_resp = await async_client.post(
            "/api/v1/settings/gemini-key",
            json={"api_key": user_raw_key},
            headers=headers,
        )
        assert key_resp.status_code == 200

    # Create KB and chat session
    kb_resp = await async_client.post(
        "/api/v1/knowledge-bases",
        json={"name": f"KB_{uuid.uuid4().hex[:8]}"},
        headers=headers,
    )
    kb_id = kb_resp.json()["id"]

    chat_resp = await async_client.post(
        f"/api/v1/knowledge-bases/{kb_id}/chats",
        headers=headers,
    )
    chat_id = chat_resp.json()["id"]

    # Send message and verify Gemini client receives the user's decrypted key
    with patch("app.services.rag_chat_service.GeminiChatClient") as mock_chat_client_cls, \
         patch("app.services.ingestion_service.GeminiEmbeddingClient") as mock_embed_cls:
        
        mock_chat_inst = MagicMock()
        mock_chat_inst.generate_response = MagicMock()
        async def fake_generate(*args, **kwargs):
            from app.services.gemini_client import ChatGenerationResult
            return ChatGenerationResult(content="Resposta gerada com a chave do usuário", prompt_tokens=10, completion_tokens=5)
        mock_chat_inst.generate_response.side_effect = fake_generate
        mock_chat_client_cls.return_value = mock_chat_inst

        mock_embed_inst = MagicMock()
        async def fake_embed(*args, **kwargs):
            return [0.0] * 768
        mock_embed_inst.generate_embedding.side_effect = fake_embed
        mock_embed_cls.return_value = mock_embed_inst

        msg_resp = await async_client.post(
            f"/api/v1/knowledge-bases/{kb_id}/chats/{chat_id}/messages",
            json={"content": "Como funciona o Atlas AI?"},
            headers=headers,
        )
        assert msg_resp.status_code == 200
        # Assert GeminiChatClient was initialized with the user's decrypted key
        mock_chat_client_cls.assert_called_with(api_key=user_raw_key)
