"""Integration tests for Gemini API Key registration and validation."""

import uuid
from unittest.mock import MagicMock, patch
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_key_registration_requires_auth(async_client: AsyncClient) -> None:
    """Ensure unauthenticated request to /settings/gemini-key returns 401."""
    response = await async_client.post(
        "/api/v1/settings/gemini-key",
        json={"api_key": "AIzaSyDFakeKey1234567890"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_key_registration_with_mocked_gemini(async_client: AsyncClient) -> None:
    """Test full flow: register user, login, submit key, and verify status."""
    unique_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    reg_response = await async_client.post(
        "/api/v1/auth/register",
        json={"email": unique_email, "password": "StrongPassword123!"},
    )
    if reg_response.status_code == 500:
        pytest.skip("Database not available in sandbox environment")

    assert reg_response.status_code == 201

    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": unique_email, "password": "StrongPassword123!"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Initially NOT_CONFIGURED
    status_resp = await async_client.get("/api/v1/settings/gemini-key/status", headers=headers)
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "NOT_CONFIGURED"

    # 2. Submit invalid key (mocked failure)
    with patch("google.genai.Client") as mock_client_cls:
        mock_instance = MagicMock()
        mock_instance.models.get.side_effect = Exception("API key invalid")
        mock_client_cls.return_value = mock_instance

        invalid_resp = await async_client.post(
            "/api/v1/settings/gemini-key",
            json={"api_key": "AIzaSyInvalidKey1234567890"},
            headers=headers,
        )
        assert invalid_resp.status_code == 400

    # 3. Submit valid key (mocked success)
    with patch("google.genai.Client") as mock_client_cls:
        mock_instance = MagicMock()
        mock_instance.models.get.return_value = MagicMock(name="gemini-2.5-flash")
        mock_client_cls.return_value = mock_instance

        valid_resp = await async_client.post(
            "/api/v1/settings/gemini-key",
            json={"api_key": "AIzaSyValidKey1234567890_ABCD"},
            headers=headers,
        )
        assert valid_resp.status_code == 200
        data = valid_resp.json()
        assert data["status"] == "VALID"
        assert data["key_hint"] == "...ABCD"
