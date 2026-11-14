# Technical Research & Architecture Decisions: Multi-Tenant Data Isolation

**Feature**: `005-multi-tenant-data-isolation`
**Date**: 2026-11-14
**Status**: Completed

## 1. Context & Architectural Root Cause Analysis

### Identified Vulnerabilities in Existing Codebase
1. **Unscoped Endpoints**:
   - `GET /api/v1/knowledge-bases`, `POST /api/v1/knowledge-bases`, `GET /api/v1/knowledge-bases/{kb_id}`, and `DELETE /api/v1/knowledge-bases/{kb_id}` did not require authentication or accept a `user_id`. Every caller received all knowledge bases across the entire database.
   - `GET /api/v1/knowledge-bases/{kb_id}/documents`, `POST .../documents`, and `DELETE ...` validated existence of `kb_id`, but never verified who owned `kb_id`.
   - `POST /api/v1/knowledge-bases/{kb_id}/chats`, `GET .../chats`, and `GET .../chats/{chat_id}` accepted any `kb_id` and `chat_id` without checking ownership.
2. **Missing Relational Ownership (`user_id`)**:
   - The SQLAlchemy models `KnowledgeBase`, `Document`, `DocumentChunk`, and `ChatSession` had zero references to `User.id`.
   - The table `knowledge_bases` had a global unique constraint on `name` (`unique=True`), preventing two distinct users from creating folders with identical names (e.g., "BTS").
3. **Unfiltered pgvector Cosine Similarity Search**:
   - `IngestionService.search_similar_chunks` queried `DocumentChunk` strictly filtering by `DocumentChunk.knowledge_base_id == kb_id`. Any user who sent a chat message or search request to any `kb_id` received semantic chunk matches from whatever documents were in that folder.
4. **Client-Side State Persistence**:
   - `authStore.logout()` removed the local token string from `localStorage` but did not reset Pinia stores (`knowledgeBaseStore`, `chatStore`, `geminiCredentialStore`). In single-page transitions without hard reload, stale data remained in memory.

---

## 2. Research Decisions

### Decision 1: Server-Derived Identity Extraction
- **Decision**: All endpoints handling private resources MUST inject `current_user: User = Depends(get_current_user)`. The authenticated user's ID (`current_user.id`) will be passed into the service layer.
- **Rationale**: Complies with Constitution Principle IV. Identity is extracted from cryptographically verified Bearer JWT tokens in the `Authorization` header. Client payloads cannot supply or override `user_id`.
- **Alternatives Considered**:
  - *Client passing `user_id` in headers or query params*: Rejected because clients can tamper with parameters (Insecure Direct Object Reference).
  - *PostgreSQL Row-Level Security (RLS) with session variables*: Considered, but adds overhead with async SQLAlchemy connection pools (`pgbouncer`/connection pooling often resets session state). Application-layer enforcement in FastAPI/SQLAlchemy provides explicit, debuggable, and type-safe query boundaries.

### Decision 2: Multi-Tenant Foreign Keys & Defense-in-Depth Schema
- **Decision**: Add `user_id` as an indexed foreign key (`UUID`, `ForeignKey("users.id", ondelete="CASCADE")`) to:
  1. `knowledge_bases`
  2. `documents`
  3. `document_chunks`
  4. `chat_sessions`
- **Rationale**: While `documents` and `document_chunks` are children of `knowledge_bases`, having `user_id` directly on every entity allows direct indexed filtering (`WHERE user_id = :uid`) on vector searches, document lookups, and session management without mandatory multi-table joins.
- **Alternatives Considered**:
  - *Only putting `user_id` on `knowledge_bases`*: Rejected because vector similarity queries on `document_chunks` would require joining `knowledge_bases` on every nearest-neighbor calculation, increasing query latency on high-dimensional vectors (768 dimensions).

### Decision 3: Compound Uniqueness for Folder Names
- **Decision**: Drop the global unique index `ix_knowledge_bases_name`. Replace it with a compound unique constraint: `UniqueConstraint('user_id', 'name', name='uq_knowledge_bases_user_id_name')`.
- **Rationale**: User A and User B must both be allowed to create a folder named "BTS" independently. Uniqueness must be enforced strictly per-user, preventing collisions between different users while still preventing accidental duplicate folders within a single user's workspace.
- **Alternatives Considered**:
  - *Removing name uniqueness entirely*: Rejected because having duplicate folder names under the same account causes confusion in UI navigation.

### Decision 4: pgvector Scoping & Filter Optimization
- **Decision**: Modify `search_similar_chunks` to accept `user_id: uuid.UUID` and add `.where(DocumentChunk.user_id == user_id, DocumentChunk.knowledge_base_id == kb_id)`.
- **Rationale**: Guarantees that vector distance calculations (`<=>`) never return passages belonging to another user. Even if a user crafts an adversarial prompt or queries another folder ID, the vector query returns zero results.
- **Alternatives Considered**:
  - *Filtering after vector retrieval in Python*: Rejected because it is insecure (pagination/limit truncation) and leaks vector computation cycles.

### Decision 5: Legacy Orphan Data Strategy
- **Decision**: In migration `0006_multi_tenant_isolation.py`, identify records in `knowledge_bases`, `documents`, `document_chunks`, and `chat_sessions` where `user_id IS NULL`. Purge these unassociated development/test records safely.
- **Rationale**: Mandated by the project requirement: "Corrija eventuais registros antigos que não estejam associados corretamente aos seus proprietários, sem atribuir dados a usuários por suposição." In development environments, attributing orphan data to arbitrary accounts violates privacy principles.
- **Alternatives Considered**:
  - *Assigning all orphan data to the first registered user*: Rejected as it violates privacy and violates explicit user instructions.

### Decision 6: IDOR Defense & Error Response Semantics
- **Decision**: When an authenticated user attempts to access a resource (folder, document, chat session) that exists in the database but belongs to another user, return HTTP 404 (EntityNotFoundException) rather than HTTP 403.
- **Rationale**: Returning HTTP 404 prevents resource enumeration attacks. An attacker cannot discover whether an ID exists in another account because unauthorized IDs appear nonexistent.
- **Alternatives Considered**:
  - *Returning HTTP 403*: Reveals that the ID exists and belongs to someone else.

### Decision 7: Frontend Store Reset & Session Hygiene
- **Decision**: Implement a `.reset()` action on `useKnowledgeBaseStore`, `useChatStore`, and `useGeminiCredentialStore`. Call all reset methods inside `useAuthStore.logout()`.
- **Rationale**: Eliminates transient visual memory leakage in single-page applications when switching accounts.
- **Alternatives Considered**:
  - *Hard window reload `window.location.reload()`*: Functional, but jarring UX. Explicit Pinia store resets provide clean and instant state clearance without disrupting SPA navigation.
