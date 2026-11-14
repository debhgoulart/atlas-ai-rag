# Implementation Plan: Multi-Tenant Data Isolation & Access Control

**Branch**: `005-multi-tenant-data-isolation` | **Date**: 2026-11-14 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/005-multi-tenant-data-isolation/spec.md`

## Summary

Enforce strict multi-tenant data isolation across the entire Atlas AI RAG platform. The bug where a folder created by User A (e.g., "BTS") was visible to User B occurred because `knowledge_bases`, `documents`, `document_chunks`, and `chat_sessions` lacked `user_id` ownership, while endpoints did not require or enforce user scoping. 

This implementation adds `user_id` foreign keys and indexes to all private resources, replaces the global folder name uniqueness constraint with a compound `(user_id, name)` constraint, injects authenticated user dependencies (`get_current_user`) into all resource routes, enforces user filtering on `pgvector` similarity queries, purges orphaned development records, and implements Pinia store cleanup on logout.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x / Vue 3 (frontend)

**Primary Dependencies**: FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, Alembic, Pinia, Axios, pgvector

**Storage**: PostgreSQL with `pgvector` extension

**Testing**: pytest, pytest-asyncio, httpx AsyncClient

**Target Platform**: Linux container (Render/Railway), Web SPA (Vercel)

**Project Type**: Fullstack Web Application (separated `/backend` and `/frontend` over REST `/api/v1`)

**Performance Goals**: Sub-50ms CRUD query response; sub-150ms pgvector similarity search with scoped user indexes

**Constraints**: Strict server-enforced authorization; zero cross-tenant leakage; IDOR attempts masked via HTTP 404; fail-closed execution on unauthenticated requests

**Scale/Scope**: Multi-user tenancy; full isolation of folders, documents, chunks, chats, and embeddings

## Constitution Check

*GATE: Evaluated against Atlas AI Constitution v1.1.0.*

- **Principle I: Monorepo Architecture & Strict Separation of Concerns**: **PASS**. Backend and frontend communicate exclusively over HTTP REST (`/api/v1`) with independent dependency manifests.
- **Principle II: Clean Code, Strict Typing & Educational Value**: **PASS**. Pydantic v2 models validate all payloads; TypeScript strict interfaces mirror contracts.
- **Principle III: Strict API Contracts & Living Schemas**: **PASS**. Explicit OpenAPI contracts documented in `/contracts/`.
- **Principle IV: Multi-Tenant Data Isolation & Server-Enforced Security (NON-NEGOTIABLE)**: **PASS**. Direct enforcement of all 10 non-negotiable multi-tenant rules. Server-derived `user_id` from Bearer token; indexed foreign keys on all private resources; scoped SQL and `pgvector` queries; IDOR defense returning 404; client-side Pinia store purge on logout.
- **Principle V: Responsible AI Engineering & Grounded RAG**: **PASS**. RAG prompt grounding strictly confined to user-owned passages.
- **Principle VI: Architectural Simplicity (KISS/YAGNI)**: **PASS**. Direct SQLAlchemy query scoping and FastAPI dependency injection without unnecessary middleware layers or external RLS engines.
- **Principle VII: Pragmatic Testing Pyramid & Testability**: **PASS**. Dedicated multi-tenant test suite (`test_multi_tenant_isolation.py`) testing User A vs. User B isolation across all operations.
- **Multi-Tenancy & Data Isolation Quality Gate**: **PASS**. Automated test suite validates zero cross-user visibility or mutation leakage.

## Project Structure

### Documentation (this feature)

```text
specs/005-multi-tenant-data-isolation/
├── plan.md              # Implementation plan
├── research.md          # Architectural research & decisions (Phase 0)
├── data-model.md        # Relational data model & migration plan (Phase 1)
├── quickstart.md        # Validation & test execution guide (Phase 1)
├── contracts/           # API interface contracts (Phase 1)
│   ├── knowledge-bases.md
│   ├── documents.md
│   └── chats.md
├── checklists/
│   └── requirements.md  # Specification quality checklist
└── spec.md              # Feature specification
```

### Source Code Impact

```text
backend/
├── alembic/
│   └── versions/
│       └── 0006_multi_tenant_isolation.py       # Migration adding user_id & compound uniqueness
├── app/
│   ├── models/
│   │   ├── knowledge_base.py                     # Add user_id FK & compound unique constraint
│   │   ├── document.py                           # Add user_id FK & index
│   │   ├── document_chunk.py                     # Add user_id FK & compound index (user_id, kb_id)
│   │   └── chat_session.py                       # Add user_id FK & index
│   ├── services/
│   │   ├── knowledge_base_service.py             # Scope create, list, get, delete by user_id
│   │   ├── ingestion_service.py                  # Scope document CRUD & pgvector search by user_id
│   │   └── rag_chat_service.py                   # Scope chat session & message turns by user_id
│   └── api/
│       └── v1/
│           ├── knowledge_bases.py                # Add Depends(get_current_user) to all routes
│           ├── documents.py                      # Add Depends(get_current_user) & pass user_id
│           └── chat.py                           # Add Depends(get_current_user) to session endpoints
└── tests/
    └── integration/
        ├── test_multi_tenant_isolation.py        # Comprehensive User A vs User B isolation tests
        └── test_knowledge_bases.py               # Update existing tests to use authenticated user

frontend/
├── src/
│   └── stores/
│       ├── authStore.ts                          # Trigger store resets on logout
│       ├── knowledgeBaseStore.ts                 # Add reset() action
│       ├── chatStore.ts                          # Add reset() action
│       └── geminiCredentialStore.ts              # Add reset() action
```

**Structure Decision**: Web application layout modifying backend SQLAlchemy models, Alembic migrations, services, FastAPI routers, and frontend Pinia stores.

## Complexity Tracking

> No constitution violations detected. Standard FastAPI dependencies and SQLAlchemy scoped filtering utilized.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| None | N/A | N/A |
