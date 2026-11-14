# Quickstart & Multi-Tenant Validation Guide

**Feature**: `005-multi-tenant-data-isolation`
**Target Audience**: Developers, QA Engineers, Security Reviewers

## Prerequisites

- PostgreSQL with `pgvector` running (via Docker Compose or local instance).
- Python virtual environment (`.venv`) with dependencies installed (`pip install -r backend/requirements.txt`).
- Node.js dependencies installed (`npm install` inside `/frontend`).

---

## 1. Automated Test Execution

Execute the full suite of multi-tenant isolation integration tests:

```bash
cd backend
pytest tests/integration/test_multi_tenant_isolation.py -v
```

### Expected Results
- `test_folder_isolation`: User A creates folder "BTS"; User B lists folders; User B receives an empty list.
- `test_same_name_folder_allowed`: User A creates "BTS" and User B creates "BTS"; both succeed with distinct IDs.
- `test_direct_folder_access_idor_blocked`: User B requests `/api/v1/knowledge-bases/{user_a_kb_id}`; returns 404.
- `test_document_isolation`: User A uploads document; User B cannot list or get document; returns 404.
- `test_chat_session_isolation`: User A starts chat; User B cannot list, fetch, or post to that session; returns 404.
- `test_vector_similarity_cross_user_leak_prevented`: User A uploads doc with unique keyword; User B queries RAG with that keyword; User B gets 0 chunks and 0 citations from User A.
- `test_unauthenticated_requests_blocked`: All endpoints return 401 when called without Bearer token.

---

## 2. Manual End-to-End Verification (Browser / Two Sessions)

1. Open two browser windows (e.g., normal window for User A, incognito window for User B).
2. Register and log in as `usera@example.com` in Window 1.
3. Register and log in as `userb@example.com` in Window 2.
4. **Create Folder**:
   - In Window 1, create a knowledge base named `BTS`.
   - In Window 2, refresh or view the dashboard. Confirm `BTS` is **not** visible.
   - In Window 2, create a knowledge base also named `BTS`. Confirm it is created successfully without conflict.
5. **Upload & Chat**:
   - In Window 1, upload a document inside `BTS`.
   - In Window 2, inspect `BTS`. Confirm 0 documents are present.
6. **Logout & Session Hygiene**:
   - In Window 1, click Logout. Confirm store state resets and redirect to Login occurs with zero residual data.
