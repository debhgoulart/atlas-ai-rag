---
description: "Task list for Multi-Tenant Data Isolation implementation"
---

# Tasks: Multi-Tenant Data Isolation & Access Control

**Input**: Design documents from `/specs/005-multi-tenant-data-isolation/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`
**Tests**: Included as mandatory verification for multi-user isolation scenarios (User A vs. User B).
**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Database migration and foundational schema preparation

- [X] T001 Create Alembic migration script in `backend/alembic/versions/0006_multi_tenant_isolation.py` revising `0005_users_and_credentials` to purge orphan legacy data (`DELETE FROM knowledge_bases WHERE user_id IS NULL`), add indexed column `user_id` (`UUID`, `ForeignKey("users.id", ondelete="CASCADE")`, `nullable=False`) to `knowledge_bases`, `documents`, `document_chunks`, and `chat_sessions`, drop global unique index `ix_knowledge_bases_name`, and create compound unique constraint `uq_knowledge_bases_user_id_name` on `(user_id, name)`.
- [X] T002 [P] Update SQLAlchemy model `KnowledgeBase` in `backend/app/models/knowledge_base.py` to add `user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)`, relationship to `User`, and `__table_args__ = (UniqueConstraint("user_id", "name", name="uq_knowledge_bases_user_id_name"),)`.
- [X] T003 [P] Update SQLAlchemy model `Document` in `backend/app/models/document.py` to add `user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)` and relationship to `User`.
- [X] T004 [P] Update SQLAlchemy model `DocumentChunk` in `backend/app/models/document_chunk.py` to add `user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)` and compound index `Index("ix_document_chunks_user_kb", "user_id", "knowledge_base_id")`.
- [X] T005 [P] Update SQLAlchemy model `ChatSession` in `backend/app/models/chat_session.py` to add `user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)` and relationship to `User`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Multi-user test harness and shared authentication fixtures

**⚠️ CRITICAL**: Foundational test scaffolding and fixtures must be established before user story implementations.

- [X] T006 Create test harness and multi-user fixtures in `backend/tests/integration/test_multi_tenant_isolation.py` setting up authenticated API clients for two distinct accounts (`User A` and `User B`).

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Isolated Knowledge Base Ownership (Priority: P1) 🎯 MVP

**Goal**: Guarantee that folders/knowledge bases are strictly owned by the creating user; User A's folder (e.g. "BTS") is invisible to User B, while User B can create their own folder named "BTS" without naming collisions.

**Independent Test**: Register User A and User B. User A creates folder "BTS". User B lists folders and receives 0 folders. User B creates folder "BTS" and succeeds with distinct ID. User B attempts to access or delete User A's folder ID and receives HTTP 404.

### Tests for User Story 1
- [X] T007 [US1] Implement isolation tests for folder creation, listing, IDOR access, and duplicate names across users in `backend/tests/integration/test_multi_tenant_isolation.py`.
- [X] T008 [P] [US1] Update existing test suite in `backend/tests/integration/test_knowledge_bases.py` to pass authenticated Bearer tokens in headers.

### Implementation for User Story 1
- [X] T009 [US1] Refactor `KnowledgeBaseService` in `backend/app/services/knowledge_base_service.py` to require `user_id: uuid.UUID` on `create`, `list_all`, `get_by_id`, and `delete`, enforcing `KnowledgeBase.user_id == user_id` on all queries and checking name duplication scoped strictly to `user_id`.
- [X] T010 [US1] Update API router endpoints in `backend/app/api/v1/knowledge_bases.py` to inject `current_user: User = Depends(get_current_user)` on `POST /`, `GET /`, `GET /{kb_id}`, and `DELETE /{kb_id}`, passing `current_user.id` to `KnowledgeBaseService`.

**Checkpoint**: At this point, User Story 1 is fully functional and testable as the core multi-tenant MVP.

---

## Phase 4: User Story 2 - Isolated Document Management & Uploads (Priority: P1)

**Goal**: Guarantee that document uploads and listings are strictly partitioned by tenant; User B cannot view, download, or delete documents uploaded by User A.

**Independent Test**: User A uploads a document to User A's folder. User B attempts to list documents in User A's folder, fetch document metadata by ID, or delete User A's document; all attempts are rejected with HTTP 404.

### Tests for User Story 2
- [X] T011 [US2] Implement document isolation and IDOR rejection tests in `backend/tests/integration/test_multi_tenant_isolation.py`.
- [X] T012 [P] [US2] Update existing tests in `backend/tests/integration/test_document_lifecycle.py` to authenticate as an owner user.

### Implementation for User Story 2
- [X] T013 [US2] Refactor `IngestionService` in `backend/app/services/ingestion_service.py` to require `user_id: uuid.UUID` on `ingest_document`, `list_documents`, `get_document`, and `delete_document`, validating that `KnowledgeBase.user_id == user_id` and setting `Document.user_id = user_id` and `DocumentChunk.user_id = user_id`.
- [X] T014 [US2] Update document API routes in `backend/app/api/v1/documents.py` to inject `current_user: User = Depends(get_current_user)` and pass `current_user.id` to `_ingestion_service` for document uploads, listing, retrieval, and deletion.

**Checkpoint**: At this point, User Stories 1 and 2 work independently with full document partition.

---

## Phase 5: User Story 3 - Isolated Conversational Chat Sessions and History (Priority: P1)

**Goal**: Guarantee that chat sessions and message history belong strictly to the creating user; User B cannot inspect, post to, or delete User A's conversations.

**Independent Test**: User A creates a chat session and posts messages. User B attempts to list sessions in User A's folder, fetch messages by session ID, post a turn, or delete the session; all attempts return HTTP 404.

### Tests for User Story 3
- [X] T015 [US3] Implement chat session isolation and IDOR rejection tests in `backend/tests/integration/test_multi_tenant_isolation.py`.
- [X] T016 [P] [US3] Update existing tests in `backend/tests/integration/test_chat_history.py` and `backend/tests/integration/test_chat_deletion.py` to authenticate before managing chat sessions.

### Implementation for User Story 3
- [X] T017 [US3] Refactor `RAGChatService` in `backend/app/services/rag_chat_service.py` to require `user_id: uuid.UUID` on `create_session`, `list_sessions`, `get_session_details`, and `delete_session`, verifying `ChatSession.user_id == user_id` and `KnowledgeBase.user_id == user_id`.
- [X] T018 [US3] Update chat endpoints in `backend/app/api/v1/chat.py` to inject `current_user: User = Depends(get_current_user)` on `POST /`, `GET /`, `GET /{chat_id}`, `DELETE /{chat_id}`, and pass `current_user.id` to `_chat_service`.

**Checkpoint**: At this point, User Stories 1, 2, and 3 are isolated and independently functional.

---

## Phase 6: User Story 4 - Multi-Tenant Vector Retrieval & RAG Isolation (Priority: P1)

**Goal**: Guarantee that semantic searches and RAG question answering draw context strictly from documents owned by the authenticated user, preventing cross-tenant vector data leakage.

**Independent Test**: User A uploads a document containing unique text "Secret Nova 98765". User B sends a RAG query or direct semantic search for "Secret Nova". The system returns 0 matching chunks and 0 citations from User A, stating no relevant information was found.

### Tests for User Story 4
- [X] T019 [US4] Implement cross-tenant vector leakage tests in `backend/tests/integration/test_multi_tenant_isolation.py` ensuring User B cannot retrieve User A's vector embeddings.
- [X] T020 [P] [US4] Update existing tests in `backend/tests/integration/test_similarity_search.py` and `backend/tests/integration/test_chat_rag.py` to authenticate the querying client.

### Implementation for User Story 4
- [X] T021 [US4] Update `IngestionService.search_similar_chunks` in `backend/app/services/ingestion_service.py` to accept `user_id: uuid.UUID` and add `.where(DocumentChunk.user_id == user_id, DocumentChunk.knowledge_base_id == kb_id)`.
- [X] T022 [US4] Update `RAGChatService.send_message` in `backend/app/services/rag_chat_service.py` to pass `user_id` into `search_similar_chunks` and verify `ChatSession.user_id == user_id`.
- [X] T023 [US4] Update `search_similar_chunks_endpoint` in `backend/app/api/v1/documents.py` to inject `current_user: User = Depends(get_current_user)` and forward `current_user.id`.

**Checkpoint**: Vector retrieval is 100% tenant-scoped; semantic searches cannot leak information across users.

---

## Phase 7: User Story 5 - Frontend Client Session Hygiene and Cache Purge (Priority: P2)

**Goal**: Guarantee that logging out or switching accounts on a shared browser completely resets all Pinia application stores, preventing transient display of previous user data.

**Independent Test**: Log in as User A, populate folders and chats. Call `logout()`. Verify `useKnowledgeBaseStore()`, `useChatStore()`, and `useGeminiCredentialStore()` states are empty arrays/null before User B logs in.

### Implementation for User Story 5
- [X] T024 [P] [US5] Add `reset()` action in `frontend/src/stores/knowledgeBaseStore.ts` to clear `knowledgeBases`, `currentKnowledgeBase`, `documents`, and error states.
- [X] T025 [P] [US5] Add `reset()` action in `frontend/src/stores/chatStore.ts` to clear `sessions`, `currentSession`, `messages`, and sending states.
- [X] T026 [P] [US5] Add `reset()` action in `frontend/src/stores/geminiCredentialStore.ts` to reset `hasKey`, `keyHint`, and validation states.
- [X] T027 [US5] Update `logout()` in `frontend/src/stores/authStore.ts` to invoke `reset()` on `useKnowledgeBaseStore()`, `useChatStore()`, and `useGeminiCredentialStore()`.

**Checkpoint**: Frontend store state is purged synchronously upon logout.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end verification and documentation compliance

- [X] T028 Run the complete integration test suite `pytest backend/tests/integration/` and verify 100% pass rate.
- [X] T029 Execute the validation scenarios documented in `specs/005-multi-tenant-data-isolation/quickstart.md`.
- [X] T030 [P] Update OpenAPI specifications and verify FastAPI documentation renders updated BearerAuth dependencies across `/api/v1/knowledge-bases`.

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: No dependencies - executes database migrations and model updates.
- **Foundational (Phase 2)**: Depends on Phase 1 - establishes the multi-user test harness.
- **User Story 1 (Phase 3)**: Depends on Phase 2 - delivers folder ownership (MVP).
- **User Story 2 (Phase 4)**: Depends on Phase 3 (needs folder ownership for document uploads).
- **User Story 3 (Phase 5)**: Depends on Phase 3 (needs folder ownership for chat sessions).
- **User Story 4 (Phase 6)**: Depends on Phase 4 and Phase 5 (needs documents and chats to scope vector queries).
- **User Story 5 (Phase 7)**: Frontend hygiene tasks can run in parallel with backend stories.
- **Polish (Phase 8)**: Depends on completion of all user stories.

### Parallel Opportunities
- Models in Phase 1 (`T002`, `T003`, `T004`, `T005`) can be updated in parallel.
- Existing test adaptations (`T008`, `T012`, `T016`, `T020`) can run in parallel with new story implementations.
- Frontend store resets (`T024`, `T025`, `T026`) can run in parallel with backend endpoints.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Complete Phase 1: Migration and models with `user_id`.
2. Complete Phase 2: Foundational test harness.
3. Complete Phase 3: Knowledge Base ownership and folder isolation.
4. **STOP and VALIDATE**: Confirm User A's folder "BTS" does not appear for User B, and User B can create their own "BTS".

### Incremental Delivery
1. Foundation + US1 → Folder isolation working (MVP).
2. Add US2 → Document upload and listing isolation.
3. Add US3 → Chat session and message history isolation.
4. Add US4 → Semantic search & pgvector chunk isolation.
5. Add US5 → Frontend cache cleanup on logout.
6. Phase 8 → Full test pass and validation.
