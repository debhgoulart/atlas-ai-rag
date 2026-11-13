# Feature Specification: Gerenciamento Individual e Seguro de Gemini API Keys

**Feature Branch**: `004-user-gemini-api-keys`
**Created**: 2026-11-13
**Status**: Draft
**Input**: Requisitos para gestão descentralizada, criptografada e individual de Gemini API Keys por usuário no Atlas AI.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cadastro e Validação Segura de API Key Individual (Priority: P1) 🎯 MVP

As an authenticated user, I want to input my personal Google Gemini API Key and have it validated with Google's API before storage, so that Atlas AI can securely execute AI operations on my behalf without relying on a shared server-side key.

**Why this priority**: Without the ability to submit, validate, encrypt, and persist a user's individual Gemini API Key, no individual AI operations (embeddings, chat generation) can be performed. This is the cornerstone of per-user AI billing and isolation.

**Independent Test**:
Can be fully tested by authenticating a user, submitting a valid Gemini API Key via the API/modal, confirming that the backend validates it against Google Gemini, encrypts it with AES-256 (Fernet/AES-GCM), stores it in the database with status `VALID`, and returns a masked key hint (e.g., `"...3aF1"`) without ever exposing the raw secret.

**Acceptance Scenarios**:
1. **Given** an authenticated user without a configured key (`NOT_CONFIGURED`), **When** they submit a valid Gemini API Key, **Then** the backend validates the key against Google Gemini, encrypts it using `CREDENTIALS_ENCRYPTION_KEY`, persists it in `user_gemini_credentials`, and returns status `VALID` with a masked `key_hint`.
2. **Given** an authenticated user, **When** they submit a syntactically invalid or deactivated Gemini API Key, **Then** the backend rejects the request with HTTP 400 (`INVALID_GEMINI_KEY`), without storing or logging the key.
3. **Given** a stored credential in the database, **When** inspected directly in PostgreSQL, **Then** the raw API key is never visible in plaintext and is stored as an encrypted binary/ciphertext payload.

---

### User Story 2 - Consulta de Status e Gerenciamento da Chave (Priority: P1)

As an authenticated user, I want to view my current key status (`NOT_CONFIGURED`, `VALID`, `INVALID`), replace an existing key with a new one, or delete my key with confirmation, so that I have full autonomy over my credentials.

**Why this priority**: Users need visibility into their credential health and must be capable of rotating or revoking credentials at any time to preserve security.

**Independent Test**:
Can be tested by querying `GET /api/v1/settings/gemini-key/status` to receive status and `key_hint`, updating the key via `POST /api/v1/settings/gemini-key`, and removing it via `DELETE /api/v1/settings/gemini-key`, verifying status transitions from `VALID` to `NOT_CONFIGURED`.

**Acceptance Scenarios**:
1. **Given** a user with a valid key, **When** querying the status endpoint, **Then** the response returns `{ "status": "VALID", "key_hint": "...XXXX", "updated_at": "..." }` without revealing the full key.
2. **Given** a user with an active key, **When** they replace it with another valid key, **Then** the old ciphertext is overwritten with the new encrypted key and the status remains `VALID`.
3. **Given** a user requesting key removal with confirmation, **When** the deletion endpoint is invoked, **Then** the stored credential record is deleted or reset to `NOT_CONFIGURED`.
4. **Given** User A and User B, **When** User A queries or updates their key, **Then** they cannot access or modify User B's key under any circumstance (strict authorization isolation).

---

### User Story 3 - Execução do Pipeline RAG com Chave do Usuário & Tratamento de Erros (Priority: P1)

As an authenticated user with a valid key, I want document ingestion (embeddings) and chat queries (synthesis) to automatically use my decrypted personal Gemini API Key, and to be notified gracefully if my key becomes invalid or unconfigured.

**Why this priority**: Ensures that the core value of Atlas AI (RAG embeddings and conversational chat) functions seamlessly with individual keys, fulfilling the multi-tenant architectural goal.

**Independent Test**:
Can be tested by sending a chat question or uploading a document as a user with a valid key, verifying that the GenAI client receives the decrypted user key; and then testing as a user with `NOT_CONFIGURED` or `INVALID` key, verifying that the system blocks the operation with an explicit error and prompts key configuration.

**Acceptance Scenarios**:
1. **Given** a user with a `VALID` key, **When** they upload a document or ask a question in chat, **Then** the backend decrypts their key in memory, initializes the Gemini client, successfully completes embedding/generation, and never exposes the key in logs or HTTP responses.
2. **Given** a user with `NOT_CONFIGURED` status, **When** attempting to upload a document or send a chat message, **Then** the backend returns HTTP 403 with error code `MISSING_USER_GEMINI_KEY`, and the frontend displays a modal to input the key.
3. **Given** a user whose key was revoked or expired on Google's side, **When** an AI operation is attempted, **Then** the backend captures the 401/403 GenAI error, updates the database status to `INVALID`, and returns `INVALID_USER_GEMINI_KEY` prompting the user to update their key.

---

### User Story 4 - Interface de Usuário e Experiência de Configuração (Priority: P2)

As a web application user, I want the UI to automatically verify my key status upon login, present a clear status indicator in the navbar, offer an intuitive modal to input/toggle visibility of the key, and disable AI actions when no key is set.

**Why this priority**: Essential for usability, preventing broken user journeys and providing transparent feedback on credential status.

**Independent Test**:
Can be tested in the browser by logging in, observing the key status badge in the navbar, opening the modal, pasting a key with visibility toggle, saving, observing the status change to green, and observing warning states when the key is absent.

**Acceptance Scenarios**:
1. **Given** a user logs in, **When** the dashboard loads, **Then** the frontend checks `/api/v1/settings/gemini-key/status` and updates the navbar badge (green for `VALID`, amber for `NOT_CONFIGURED`, red for `INVALID`).
2. **Given** the status is `NOT_CONFIGURED`, **When** the user accesses a knowledge base or chat, **Then** a warning banner or modal prompts them to configure their Gemini API Key, disabling generation buttons.
3. **Given** the modal is open, **When** the user clicks the eye icon, **Then** the input type toggles between `password` and `text`.
4. **Given** a successful key validation, **When** the modal closes, **Then** the UI reflects `VALID` state and enables all AI interactions.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer autenticação de usuário (registro, login e identificação via token JWT Bearer) para associar credenciais exclusivamente ao usuário autenticado.
- **FR-002**: O sistema NUNCA DEVE armazenar Gemini API Keys em texto puro no banco de dados. Todas as chaves DEVEM ser criptografadas com algoritmo simétrico autenticado (Fernet ou AES-256-GCM) antes da persistência.
- **FR-003**: A chave mestra de criptografia DEVE ser carregada exclusivamente da variável de ambiente `CREDENTIALS_ENCRYPTION_KEY` no backend. A `SECRET_KEY` de autenticação NÃO DEVE ser reutilizada para criptografia de dados.
- **FR-004**: O backend DEVE validar a chave diretamente junto à API do Google Gemini antes de persistir qualquer nova chave.
- **FR-005**: O sistema DEVE manter o ciclo de vida da credencial através do status `NOT_CONFIGURED`, `VALID` e `INVALID`.
- **FR-006**: O endpoint de consulta de status NUNCA DEVE retornar a chave completa, retornando apenas status, data de atualização e máscara com os últimos 4 dígitos (`key_hint`).
- **FR-007**: As chaves NUNCA DEVEM ser registradas em logs, traces, mensagens de erro ou respostas HTTP.
- **FR-008**: O pipeline de RAG (geração de embeddings e geração de respostas no chat) DEVE recuperar e descriptografar a chave do usuário autenticado para instanciar os clientes do Google Gemini.
- **FR-009**: Se o usuário não possuir chave ou a chave for inválida, as operações de IA DEVEM ser bloqueadas com código de erro específico (`MISSING_USER_GEMINI_KEY` / `INVALID_USER_GEMINI_KEY`).
- **FR-010**: A interface frontend DEVE permitir cadastrar, visualizar status, alternar visibilidade, substituir e remover a chave mediante confirmação.

---

### Non-Functional & Security Requirements

- **NFR-001**: Isolamento rigoroso de tenants: um usuário só pode acessar ou alterar sua própria credencial.
- **NFR-002**: Chaves de criptografia e API keys não trafegam no frontend salvo no momento do envio inicial pelo usuário via POST HTTPS.
- **NFR-003**: Zero dependência de chave global do sistema no ambiente de produção para chamadas de usuários.

---

## Key Entities

- **User**: Representa o usuário do sistema (`id`, `email`, `hashed_password`, `created_at`, `updated_at`).
- **UserGeminiCredential**: Representa a credencial criptografada do usuário (`id`, `user_id`, `encrypted_api_key`, `key_hint`, `status`, `last_validated_at`, `created_at`, `updated_at`).
