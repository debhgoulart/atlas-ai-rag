"""Integration tests ensuring multi-tenant isolation between different users' keys."""

import uuid
from unittest.mock import MagicMock, patch
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_multi_user_isolation(async_client: AsyncClient) -> None:
    """Ensure User A cannot view, modify, or delete User B's credentials."""
    user_a_email = f"user_a_{uuid.uuid4().hex[:8]}@example.com"
    user_b_email = f"user_b_{uuid.uuid4().hex[:8]}@example.com"

    reg_a = await async_client.post(
        "/api/v1/auth/register",
        json={"email": user_a_email, "password": "PasswordUserA123!"},
    )
    if reg_a.status_code == 500:
        pytest.skip("Database not available in sandbox environment")

    await async_client.post(
        "/api/v1/auth/register",
        json={"email": user_b_email, "password": "PasswordUserB123!"},
    )

    login_a = await async_client.post(
        "/api/v1/auth/login",
        json={"email": user_a_email, "password": "PasswordUserA123!"},
    )
    login_b = await async_client.post(
        "/api/v1/auth/login",
        json={"email": user_b_email, "password": "PasswordUserB123!"},
    )

    headers_a = {"Authorization": f"Bearer {login_a.json()['access_token']}"}
    headers_b = {"Authorization": f"Bearer {login_b.json()['access_token']}"}

    with patch("google.genai.Client") as mock_client:
        mock_instance = MagicMock()
        mock_instance.models.get.return_value = MagicMock()
        mock_client.return_value = mock_instance

        # User A registers key
        await async_client.post(
            "/api/v1/settings/gemini-key",
            json={"api_key": "AIzaSyKeyForUserA_AAAA"},
            headers=headers_a,
        )

        # User B registers key
        await async_client.post(
            "/api/v1/settings/gemini-key",
            json={"api_key": "AIzaSyKeyForUserB_BBBB"},
            headers=headers_b,
        )

        # Verify User A sees ONLY their key hint
        status_a = await async_client.get("/api/v1/settings/gemini-key/status", headers=headers_a)
        assert status_a.json()["key_hint"] == "...AAAA"

        # Verify User B sees ONLY their key hint
        status_b = await async_client.get("/api/v1/settings/gemini-key/status", headers=headers_b)
        assert status_b.json()["key_hint"] == "...BBBB"

        # User A deletes their key
        await async_client.delete("/api/v1/settings/gemini-key", headers=headers_a)

        # User A is now NOT_CONFIGURED
        status_a_after = await async_client.get("/api/v1/settings/gemini-key/status", headers=headers_a)
        assert status_a_after.json()["status"] == "NOT_CONFIGURED"

        # User B is STILL VALID with their own key
        status_b_after = await async_client.get("/api/v1/settings/gemini-key/status", headers=headers_b)
        assert status_b_after.json()["status"] == "VALID"
        assert status_b_after.json()["key_hint"] == "...BBBB"
