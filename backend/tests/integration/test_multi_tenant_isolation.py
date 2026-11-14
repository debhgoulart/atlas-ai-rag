"""Integration tests ensuring multi-tenant data isolation across all resources.

Verifies that User A and User B operate in completely independent silos:
- Folders / Knowledge Bases (creation, listing, IDOR access, homonymous folder names)
- Documents and file uploads
- Chat sessions and message histories
- Vector similarity searches and RAG retrieval
"""

import uuid
from typing import Dict, Tuple
from unittest.mock import MagicMock, patch
import pytest
from httpx import AsyncClient


async def register_and_login_user(
    async_client: AsyncClient, prefix: str
) -> Tuple[str, Dict[str, str]]:
    """Register and authenticate a new isolated user account, returning email and headers."""
    email = f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"
    password = "PasswordUser123!"

    reg_resp = await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    if reg_resp.status_code == 500:
        pytest.skip("Database connection not active in current test environment")

    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return email, headers


# -------------------------------------------------------------------------
# Phase 3: User Story 1 - Isolated Knowledge Base Ownership
# -------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_folder_isolation_and_homonymous_creation(async_client: AsyncClient) -> None:
    """User A creates folder 'BTS'. User B cannot see it, but can create their own 'BTS'."""
    _, headers_a = await register_and_login_user(async_client, "user_a")
    _, headers_b = await register_and_login_user(async_client, "user_b")

    folder_name = "BTS"

    # 1. User A creates folder "BTS"
    create_a = await async_client.post(
        "/api/v1/knowledge-bases",
        json={"name": folder_name, "description": "User A BTS folder"},
        headers=headers_a,
    )
    assert create_a.status_code == 201
    kb_a_id = create_a.json()["id"]

    # 2. User B lists folders -> User A's folder must NOT appear
    list_b = await async_client.get("/api/v1/knowledge-bases", headers=headers_b)
    assert list_b.status_code == 200
    kb_b_ids = [kb["id"] for kb in list_b.json()]
    assert kb_a_id not in kb_b_ids

    # 3. User B creates their own folder also named "BTS" -> MUST succeed
    create_b = await async_client.post(
        "/api/v1/knowledge-bases",
        json={"name": folder_name, "description": "User B BTS folder"},
        headers=headers_b,
    )
    assert create_b.status_code == 201
    kb_b_id = create_b.json()["id"]
    assert kb_a_id != kb_b_id

    # 4. User B cannot create duplicate "BTS" within their own account
    dup_b = await async_client.post(
        "/api/v1/knowledge-bases",
        json={"name": folder_name, "description": "Duplicate BTS"},
        headers=headers_b,
    )
    assert dup_b.status_code == 400
    assert dup_b.json()["code"] == "DUPLICATE_ENTITY"

    # 5. User B attempts direct access (IDOR) to User A's folder by ID -> 404
    idor_get = await async_client.get(
        f"/api/v1/knowledge-bases/{kb_a_id}",
        headers=headers_b,
    )
    assert idor_get.status_code == 404

    # 6. User B attempts to delete User A's folder -> 404
    idor_del = await async_client.delete(
        f"/api/v1/knowledge-bases/{kb_a_id}",
        headers=headers_b,
    )
    assert idor_del.status_code == 404


@pytest.mark.asyncio
async def test_unauthenticated_folder_operations_blocked(async_client: AsyncClient) -> None:
    """Anonymous requests to knowledge base endpoints must be rejected with 401."""
    resp_list = await async_client.get("/api/v1/knowledge-bases")
    assert resp_list.status_code == 401

    resp_create = await async_client.post(
        "/api/v1/knowledge-bases",
        json={"name": "Anon Folder"},
    )
    assert resp_create.status_code == 401

    fake_id = str(uuid.uuid4())
    resp_get = await async_client.get(f"/api/v1/knowledge-bases/{fake_id}")
    assert resp_get.status_code == 401


# -------------------------------------------------------------------------
# Phase 4: User Story 2 - Isolated Document Management & Uploads
# -------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_document_isolation_and_idor(async_client: AsyncClient) -> None:
    """User B cannot list, retrieve, or delete User A's documents."""
    _, headers_a = await register_and_login_user(async_client, "user_a")
    _, headers_b = await register_and_login_user(async_client, "user_b")

    # Set mock Gemini keys for both users so document upload works
    with patch("google.genai.Client") as mock_client:
        mock_instance = MagicMock()
        mock_instance.models.get.return_value = MagicMock()
        mock_client.return_value = mock_instance

        await async_client.post(
            "/api/v1/settings/gemini-key",
            json={"api_key": "AIzaSyKeyA_1234567890"},
            headers=headers_a,
        )
        await async_client.post(
            "/api/v1/settings/gemini-key",
            json={"api_key": "AIzaSyKeyB_1234567890"},
            headers=headers_b,
        )

    # User A creates a folder
    kb_a = await async_client.post(
        "/api/v1/knowledge-bases",
        json={"name": "Confidential Project"},
        headers=headers_a,
    )
    kb_a_id = kb_a.json()["id"]

    # Mock embeddings to avoid external Gemini API call
    with patch("app.services.gemini_client.GeminiEmbeddingClient.generate_embedding") as mock_embed:
        mock_embed.return_value = [0.1] * 768

        # User A uploads a document
        upload_resp = await async_client.post(
            f"/api/v1/knowledge-bases/{kb_a_id}/documents",
            files={"file": ("secret.txt", b"Secret Project Data for User A", "text/plain")},
            headers=headers_a,
        )
        assert upload_resp.status_code == 201
        doc_a_id = upload_resp.json()["id"]

    # User B attempts to list documents in User A's folder -> 404
    list_docs_b = await async_client.get(
        f"/api/v1/knowledge-bases/{kb_a_id}/documents",
        headers=headers_b,
    )
    assert list_docs_b.status_code == 404

    # User B attempts to get details of User A's document -> 404
    get_doc_b = await async_client.get(
        f"/api/v1/knowledge-bases/{kb_a_id}/documents/{doc_a_id}",
        headers=headers_b,
    )
    assert get_doc_b.status_code == 404

    # User B attempts to delete User A's document -> 404
    del_doc_b = await async_client.delete(
        f"/api/v1/knowledge-bases/{kb_a_id}/documents/{doc_a_id}",
        headers=headers_b,
    )
    assert del_doc_b.status_code == 404


# -------------------------------------------------------------------------
# Phase 5: User Story 3 - Isolated Chat Sessions and History
# -------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_chat_session_isolation(async_client: AsyncClient) -> None:
    """User B cannot list, access, post to, or delete User A's chat sessions."""
    _, headers_a = await register_and_login_user(async_client, "user_a")
    _, headers_b = await register_and_login_user(async_client, "user_b")

    kb_a = await async_client.post(
        "/api/v1/knowledge-bases",
        json={"name": "Chat KB A"},
        headers=headers_a,
    )
    kb_a_id = kb_a.json()["id"]

    # User A creates a chat session
    chat_a = await async_client.post(
        f"/api/v1/knowledge-bases/{kb_a_id}/chats",
        json={"title": "Private Conversation"},
        headers=headers_a,
    )
    assert chat_a.status_code == 201
    chat_a_id = chat_a.json()["id"]

    # User B tries to list chat sessions in User A's KB -> 404
    list_chats_b = await async_client.get(
        f"/api/v1/knowledge-bases/{kb_a_id}/chats",
        headers=headers_b,
    )
    assert list_chats_b.status_code == 404

    # User B tries to get details of User A's chat session -> 404
    get_chat_b = await async_client.get(
        f"/api/v1/knowledge-bases/{kb_a_id}/chats/{chat_a_id}",
        headers=headers_b,
    )
    assert get_chat_b.status_code == 404

    # User B tries to delete User A's chat session -> 404
    del_chat_b = await async_client.delete(
        f"/api/v1/knowledge-bases/{kb_a_id}/chats/{chat_a_id}",
        headers=headers_b,
    )
    assert del_chat_b.status_code == 404


# -------------------------------------------------------------------------
# Phase 6: User Story 4 - Vector Similarity Search & RAG Isolation
# -------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_vector_search_cross_tenant_isolation(async_client: AsyncClient) -> None:
    """User B's vector searches and RAG queries cannot match User A's embeddings."""
    _, headers_a = await register_and_login_user(async_client, "user_a")
    _, headers_b = await register_and_login_user(async_client, "user_b")

    # Set mock keys
    with patch("google.genai.Client") as mock_client:
        mock_instance = MagicMock()
        mock_instance.models.get.return_value = MagicMock()
        mock_client.return_value = mock_instance

        await async_client.post(
            "/api/v1/settings/gemini-key",
            json={"api_key": "AIzaSyKeyA_9999999999"},
            headers=headers_a,
        )
        await async_client.post(
            "/api/v1/settings/gemini-key",
            json={"api_key": "AIzaSyKeyB_9999999999"},
            headers=headers_b,
        )

    # User A creates KB and uploads document with unique phrase
    kb_a = await async_client.post(
        "/api/v1/knowledge-bases",
        json={"name": "Project Nova A"},
        headers=headers_a,
    )
    kb_a_id = kb_a.json()["id"]

    # User B creates their own KB
    kb_b = await async_client.post(
        "/api/v1/knowledge-bases",
        json={"name": "Project Nova B"},
        headers=headers_b,
    )
    kb_b_id = kb_b.json()["id"]

    with patch("app.services.gemini_client.GeminiEmbeddingClient.generate_embedding") as mock_embed:
        # Mock identical embeddings so semantic distance is 0.0 (exact match)
        mock_embed.return_value = [0.2] * 768

        await async_client.post(
            f"/api/v1/knowledge-bases/{kb_a_id}/documents",
            files={"file": ("nova.txt", b"Project Nova Secret Code 98765", "text/plain")},
            headers=headers_a,
        )

        # User B queries their own KB for the secret code
        search_b = await async_client.post(
            f"/api/v1/knowledge-bases/{kb_b_id}/search",
            json={"query": "Project Nova Secret Code 98765", "limit": 5},
            headers=headers_b,
        )
        assert search_b.status_code == 200
        results_b = search_b.json()
        # Must return 0 results because User A's chunk must never leak into User B's search
        assert len(results_b) == 0

        # User B attempts to query User A's KB directly -> 404
        search_a_by_b = await async_client.post(
            f"/api/v1/knowledge-bases/{kb_a_id}/search",
            json={"query": "Project Nova Secret Code 98765", "limit": 5},
            headers=headers_b,
        )
        assert search_a_by_b.status_code == 404
