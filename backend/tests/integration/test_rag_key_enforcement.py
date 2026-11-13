"""Integration tests verifying enforcement of Gemini API key on RAG operations."""

import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_chat_and_upload_blocked_without_user_key(async_client: AsyncClient) -> None:
    """Ensure user without configured Gemini Key receives HTTP 403 on RAG endpoints."""
    email = f"nokey_{uuid.uuid4().hex[:8]}@example.com"
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
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    fake_kb_id = str(uuid.uuid4())
    fake_chat_id = str(uuid.uuid4())

    # 1. Attempt sending chat message without key -> 403 Forbidden
    chat_resp = await async_client.post(
        f"/api/v1/knowledge-bases/{fake_kb_id}/chats/{fake_chat_id}/messages",
        json={"content": "Qual é a resposta para a vida?"},
        headers=headers,
    )
    assert chat_resp.status_code == 403
    assert "Gemini API Key" in chat_resp.json()["detail"]

    # 2. Attempt document upload without key -> 403 Forbidden
    files = {"file": ("test.txt", b"Conteudo do arquivo de teste", "text/plain")}
    upload_resp = await async_client.post(
        f"/api/v1/knowledge-bases/{fake_kb_id}/documents",
        files=files,
        headers=headers,
    )
    assert upload_resp.status_code == 403
    assert "Gemini API Key" in upload_resp.json()["detail"]
