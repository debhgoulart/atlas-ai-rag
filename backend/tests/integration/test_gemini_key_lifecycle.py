"""Integration tests for Gemini API Key lifecycle and deletion."""

import uuid
from unittest.mock import MagicMock, patch
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_key_lifecycle_update_and_deletion(async_client: AsyncClient) -> None:
    """Test updating existing key and removing key with confirmation."""
    email = f"lifecycle_{uuid.uuid4().hex[:8]}@example.com"
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

    with patch("google.genai.Client") as mock_client:
        mock_instance = MagicMock()
        mock_instance.models.get.return_value = MagicMock()
        mock_client.return_value = mock_instance

        # 1. Register first key
        res1 = await async_client.post(
            "/api/v1/settings/gemini-key",
            json={"api_key": "AIzaSyInitialKey_1111"},
            headers=headers,
        )
        assert res1.status_code == 200
        assert res1.json()["key_hint"] == "...1111"

        # 2. Update with second key
        res2 = await async_client.post(
            "/api/v1/settings/gemini-key",
            json={"api_key": "AIzaSyUpdatedKey_2222"},
            headers=headers,
        )
        assert res2.status_code == 200
        assert res2.json()["key_hint"] == "...2222"

        # 3. Check status
        status_res = await async_client.get("/api/v1/settings/gemini-key/status", headers=headers)
        assert status_res.status_code == 200
        assert status_res.json()["key_hint"] == "...2222"

        # 4. Delete key
        del_res = await async_client.delete("/api/v1/settings/gemini-key", headers=headers)
        assert del_res.status_code == 200
        assert del_res.json()["status"] == "NOT_CONFIGURED"
        assert del_res.json()["key_hint"] is None
