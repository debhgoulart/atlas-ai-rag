---
description: "Task list for feature 004-user-gemini-api-keys implementation"
---

# Tasks: Gerenciamento Individual e Seguro de Gemini API Keys

**Input**: Design documents from `specs/004-user-gemini-api-keys/` (`spec.md`, `plan.md`, `data-model.md`, `contracts/credentials-api.yaml`, `research.md`)

**Prerequisites**: Constitution v1.0.0, Python 3.11+ / 3.14, Node.js 20+, PostgreSQL com pgvector

**Organization**: Tasks are grouped into sequential Setup, Foundational, User Stories (P1/P2), and Polish phases to enable independent implementation and testability.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no direct dependencies)
- **[Story]**: User story mapping (`US1`, `US2`, `US3`, `US4`)
- Exact file paths are provided for each task

---

## Phase 1: Setup (Dependencies, Environment & Architecture Records)

**Purpose**: Instalar bibliotecas de segurança e configurar variáveis de ambiente isoladas.

- [x] T001 Adicionar dependências de segurança (`cryptography>=43.0.0`, `passlib[bcrypt]>=1.7.4`, `pyjwt>=2.9.0`) em `backend/requirements.txt`
- [x] T002 [P] Atualizar `backend/app/core/config.py` com novas variáveis de ambiente (`CREDENTIALS_ENCRYPTION_KEY`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`)
- [x] T003 [P] Atualizar templates de ambiente `.env.example` e `backend/.env.example` com placeholders não sensíveis e documentar variáveis do Render vs Vercel
- [x] T004 [P] Criar registro de decisão arquitetural em `docs/adr/0003-user-credentials-encryption-and-isolation.md` detalhando criptografia simétrica e isolamento multi-tenant

**Checkpoint**: Dependências e variáveis de ambiente configuradas.

---

## Phase 2: Foundational (Database Models, Migrations & Core Auth Foundation)

**Purpose**: Infraestrutura de autenticação e persistência que bloqueia a implementação das user stories.

**⚠️ CRITICAL**: Nenhuma user story de API keys pode ser implementada antes da conclusão desta fundação.

- [x] T005 [P] Implementar serviço de criptografia simétrica `EncryptionService` (Fernet / AES-256 com suporte a versionamento de chave) em `backend/app/core/security/encryption.py`
- [x] T006 [P] Implementar utilitários de autenticação (hashing de senha via bcrypt e geração/validação de tokens JWT) em `backend/app/core/security/auth.py`
- [x] T007 [P] Criar modelo SQLAlchemy `User` (`users`: `id`, `email`, `hashed_password`, `is_active`, `created_at`, `updated_at`) em `backend/app/models/user.py`
- [x] T008 [P] Criar modelo SQLAlchemy `UserGeminiCredential` (`user_gemini_credentials`: `id`, `user_id` FK unique cascade, `encrypted_api_key`, `key_hint`, `status`, `last_validated_at`, `created_at`, `updated_at`) em `backend/app/models/user_gemini_credential.py`
- [x] T009 Exportar novos modelos em `backend/app/models/__init__.py` e criar migração Alembic em `backend/alembic/versions/0005_users_and_credentials.py`
- [x] T010 [P] Criar schemas Pydantic de autenticação (`UserRegisterRequest`, `UserLoginRequest`, `TokenResponse`, `UserResponse`) em `backend/app/schemas/auth.py`
- [x] T011 Implementar dependência FastAPI `get_current_user` para extração e validação do token JWT Bearer em `backend/app/api/deps.py`
- [x] T012 Implementar rotas de autenticação (`POST /register`, `POST /login`, `GET /me`) em `backend/app/api/v1/auth.py` e registrar no roteador principal em `backend/app/api/v1/router.py`
- [x] T013 [P] Definir tipos TypeScript de autenticação (`User`, `LoginCredentials`, `RegisterData`, `AuthTokens`) em `frontend/src/types/auth.ts` e exportar em `frontend/src/types/index.ts`
- [x] T014 [P] Implementar serviço de autenticação `authService.ts` em `frontend/src/services/authService.ts`
- [x] T015 [P] Implementar loja Pinia `authStore.ts` com gerenciamento de estado de login, persistência de token e logout em `frontend/src/stores/authStore.ts`
- [x] T016 Configurar interceptor no cliente Axios em `frontend/src/services/api.ts` para anexar o cabeçalho `Authorization: Bearer <token>` dinamicamente

**Checkpoint**: Fundação pronta - autenticação de usuário e tabelas do banco operacionais.

---

## Phase 3: User Story 1 - Cadastro e Validação Segura de API Key Individual (Priority: P1) 🎯 MVP

**Goal**: Permitir que o usuário autenticado envie sua Gemini API Key, valide-a sem custo junto ao Google Gemini, criptografe-a e salve-a no PostgreSQL com status `VALID`, rejeitando chaves inválidas.

**Independent Test**: Submeter uma chave válida via endpoint autenticado, verificar retorno de status `VALID` com `key_hint` mascarado (ex: `"...3aF1"`), verificar que no banco de dados a chave está criptografada e não em texto claro, e submeter uma chave inválida verificando HTTP 400 sem persistência.

### Tests for User Story 1 ⚠️
- [x] T017 [P] [US1] Teste unitário para `EncryptionService` (cifragem, decifragem, integridade e tratamento de chave incorreta) em `backend/tests/unit/test_encryption.py`
- [x] T018 [P] [US1] Teste unitário para validação da chave Gemini junto ao Google (mock de resposta válida e inválida via `genai.Client`) em `backend/tests/unit/test_gemini_validator.py`
- [x] T019 [P] [US1] Teste de integração para cadastro de chave válida e rejeição de chave inválida em `backend/tests/integration/test_gemini_key_registration.py`

### Implementation for User Story 1
- [x] T020 [P] [US1] Criar schemas Pydantic para credenciais Gemini (`GeminiKeyCreateRequest`, `GeminiKeyStatusResponse`, enum `ApiKeyStatus`) em `backend/app/schemas/gemini_credential.py`
- [x] T021 [US1] Implementar serviço `GeminiCredentialService` com método `save_and_validate_key(user_id, api_key)` validando via `client.models.get` e criptografando em `backend/app/services/gemini_credential_service.py`
- [x] T022 [US1] Implementar endpoint `POST /api/v1/settings/gemini-key` em `backend/app/api/v1/gemini_credentials.py` e registrar em `backend/app/api/v1/router.py`

**Checkpoint**: User Story 1 (MVP) concluída - chaves individuais cadastradas, validadas e criptografadas no banco.

---

## Phase 4: User Story 2 - Consulta de Status, Substituição e Remoção com Isolamento (Priority: P1)

**Goal**: Permitir ao usuário autenticado consultar o status de sua chave (com máscara), substituí-la por uma nova ou removê-la com confirmação, garantindo isolamento total entre usuários.

**Independent Test**: Consultar status retornando `VALID` e `key_hint`, atualizar a chave para uma nova verificando atualização no banco, deletar a chave e confirmar retorno para `NOT_CONFIGURED`, além de testar tentativa de acesso cruzado entre usuários distintos (HTTP 401/403).

### Tests for User Story 2 ⚠️
- [x] T023 [P] [US2] Teste de integração para ciclo de vida de status, substituição e deleção de chave em `backend/tests/integration/test_gemini_key_lifecycle.py`
- [x] T024 [P] [US2] Teste de integração para isolamento estrito entre usuários (garantir que Usuário A nunca acessa ou modifica a chave do Usuário B) em `backend/tests/integration/test_gemini_key_isolation.py`

### Implementation for User Story 2
- [x] T025 [US2] Adicionar métodos `get_status(user_id)` e `delete_key(user_id)` no serviço `backend/app/services/gemini_credential_service.py`
- [x] T026 [US2] Implementar endpoints `GET /api/v1/settings/gemini-key/status` e `DELETE /api/v1/settings/gemini-key` em `backend/app/api/v1/gemini_credentials.py`

**Checkpoint**: User Story 2 concluída - gerenciamento completo do ciclo de vida e isolamento rigoroso entre contas.

---

## Phase 5: User Story 3 - Execução do Pipeline RAG com Chave do Usuário & Tratamento de Erros (Priority: P1)

**Goal**: Ingestão de documentos (embeddings) e respostas do chatbot (chat RAG) recuperam e utilizam a chave individual descriptografada do usuário autenticado em memória, bloqueando operações sem chave válida e sem registrar chaves em logs.

**Independent Test**: Fazer upload de documento e envio de mensagem de chat com usuário autenticado com chave válida, verificando execução bem-sucedida; repetir operação com usuário sem chave ou chave revogada, verificando retorno HTTP 403 (`MISSING_USER_GEMINI_KEY` / `INVALID_USER_GEMINI_KEY`) e atualização de status no banco para `INVALID`.

### Tests for User Story 3 ⚠️
- [x] T027 [P] [US3] Teste de integração do fluxo de chat RAG utilizando a chave descriptografada do usuário autenticado em `backend/tests/integration/test_rag_user_key.py`
- [x] T028 [P] [US3] Teste de integração verificando bloqueio de operações RAG para usuários sem chave ou com status `INVALID` em `backend/tests/integration/test_rag_key_enforcement.py`
- [x] T029 [P] [US3] Teste unitário do sanitizador de logs garantindo que strings de API Key nunca sejam gravadas em disco ou stdout em `backend/tests/unit/test_log_sanitizer.py`

### Implementation for User Story 3
- [x] T030 [US3] Implementar dependência FastAPI `get_user_gemini_api_key` em `backend/app/api/deps.py` que recupera e descriptografa a chave do usuário autenticado e lança `HTTPException(403)` se ausente/inválida
- [x] T031 [US3] Adaptar endpoint de upload de documentos em `backend/app/api/v1/documents.py` e serviço `backend/app/services/ingestion_service.py` para receber a chave do usuário na geração de embeddings
- [x] T032 [US3] Adaptar endpoint de chat em `backend/app/api/v1/chat.py` e serviço `backend/app/services/rag_chat_service.py` para receber a chave do usuário no retrieval de embeddings e na síntese da resposta
- [x] T033 [US3] Implementar captura de erro 401/403 do Google Gemini no chat e embeddings para marcar automaticamente a credencial como `INVALID` no banco
- [x] T034 [P] [US3] Implementar filtro customizado de logging em `backend/app/core/logging.py` para sanitizar e mascarar qualquer ocorrência acidental de tokens e API keys (`AIzaSy...`)

**Checkpoint**: User Story 3 concluída - pipeline RAG completamente desacoplado da chave global e operando por usuário.

---

## Phase 6: User Story 4 - Interface de Usuário & Experiência de Configuração (Priority: P2)

**Goal**: Interface web para verificação automática de status após login, indicador visual no Navbar, modal responsivo de cadastro/substituição/exclusão com toggle de visibilidade e bloqueio visual de ações de IA quando a chave estiver ausente.

**Independent Test**: Acessar a aplicação autenticado, visualizar badge indicativo no Navbar (amarelo para não configurado, verde para válido, vermelho para inválido), clicar no modal, cadastrar chave com opção de mostrar/ocultar senha, salvar, observar transição do badge e desbloqueio dos botões de chat/upload.

### Implementation for User Story 4
- [x] T035 [P] [US4] Criar tipos TypeScript para status de credenciais em `frontend/src/types/credential.ts` e exportar em `frontend/src/types/index.ts`
- [x] T036 [P] [US4] Implementar serviço HTTP `geminiCredentialService.ts` em `frontend/src/services/geminiCredentialService.ts`
- [x] T037 [US4] Implementar loja Pinia `geminiCredentialStore.ts` com ações para consultar status, salvar chave e remover chave em `frontend/src/stores/geminiCredentialStore.ts`
- [x] T038 [P] [US4] Criar modal de autenticação `AuthModal.vue` (login e cadastro com alternância de abas) em `frontend/src/components/AuthModal.vue`
- [x] T039 [P] [US4] Criar modal de gerenciamento de chave `GeminiKeyModal.vue` com campo de texto com botão de mostrar/ocultar senha, feedback de carregamento, badge de status e confirmação de exclusão em `frontend/src/components/GeminiKeyModal.vue`
- [x] T040 [US4] Atualizar barra de navegação `Navbar.vue` em `frontend/src/components/Navbar.vue` adicionando indicador visual de status da Gemini Key (pílula colorida clicável) e botão de login/perfil
- [x] T041 [US4] Atualizar `ChatInputBar.vue` e `FileDropzone.vue` para desabilitar envios e exibir aviso interativo que abre o `GeminiKeyModal` quando o status da chave for `NOT_CONFIGURED` ou `INVALID`
- [x] T042 [US4] Integrar verificação automática de status da chave no carregamento inicial da aplicação em `frontend/src/App.vue`

**Checkpoint**: User Story 4 concluída - experiência de usuário completa e fluida no frontend.

---

## Phase 7: Polish, Deploy & Cross-Cutting Concerns

**Purpose**: Scripts de suporte, rotação de chaves, verificação de segurança e documentação de deploy.

- [x] T043 [P] Criar script utilitário para gerar novas chaves mestras de criptografia em `backend/app/scripts/generate_encryption_key.py`
- [x] T044 [P] Criar script utilitário para rotação de chave mestra de criptografia (recriptografando dados existentes no PostgreSQL) em `backend/app/scripts/rotate_encryption_key.py`
- [x] T045 [P] Atualizar `README.md` com instruções detalhadas de configuração das variáveis no Render (`DATABASE_URL`, `SECRET_KEY`, `CREDENTIALS_ENCRYPTION_KEY`) e na Vercel (`VITE_API_URL`)
- [x] T046 Executar suíte completa de testes de integração e unitários do backend (`pytest backend/tests/`) garantindo zero regressões
- [x] T047 Executar checagem de tipos do frontend (`npm run build` com `vue-tsc`) garantindo tipagem estrita

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: Sem dependências - pode iniciar imediatamente.
- **Foundational (Phase 2)**: Depende da Phase 1 (dependências instaladas) - **BLOQUEIA** todas as user stories.
- **User Story 1 (Phase 3 - MVP)**: Depende da Phase 2 (tabelas e autenticação existentes).
- **User Story 2 (Phase 4)**: Depende da Phase 3 (estrutura de persistência e validação).
- **User Story 3 (Phase 5)**: Depende da Phase 3 e 4 (recuperação e injeção da chave descriptografada nos serviços RAG).
- **User Story 4 (Phase 6)**: Depende dos endpoints das Phases 2, 3 e 4.
- **Polish (Phase 7)**: Depende de todas as fases implementadas.

### Parallel Opportunities
- **Setup**: T002, T003 e T004 podem ser executadas em paralelo.
- **Foundational**:
  - T005 (`EncryptionService`) e T006 (`AuthUtils`) são independentes e rodam em paralelo.
  - T007 (`User` model) e T008 (`UserGeminiCredential` model) rodam em paralelo.
  - T013, T014 e T015 no frontend rodam em paralelo com o backend da Phase 2.
- **User Story 1**: T017, T018 e T019 (testes) rodam em paralelo antes da implementação T021/T022.
- **User Story 2**: T023 e T024 (testes) rodam em paralelo.
- **User Story 3**: T027, T028 e T029 (testes) rodam em paralelo.
- **User Story 4**: T035, T036, T038 e T039 no frontend rodam em paralelo.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Concluir Setup (Phase 1)
2. Concluir Foundational (Phase 2 - modelos, autenticação, migração)
3. Concluir User Story 1 (Phase 3 - validação, criptografia e cadastro da chave)
4. **VALIDAR**: Submeter chave real via Swagger UI / Postman e verificar cifra no PostgreSQL.

### Incremental Delivery
1. Setup + Foundational $\rightarrow$ Base multi-tenant pronta.
2. User Story 1 $\rightarrow$ Cadastro e validação de chaves funcionando (MVP).
3. User Story 2 $\rightarrow$ Consulta, substituição, exclusão e isolamento de tenants.
4. User Story 3 $\rightarrow$ Pipeline RAG conectado às chaves dos usuários.
5. User Story 4 $\rightarrow$ Interface gráfica completa no frontend com feedback visual.
6. Phase 7 $\rightarrow$ Rotação de chaves, documentação e deploy no Render/Vercel.
