# Implementation Plan: Conversational RAG & Chatbot Engine

**Branch**: `002-conversational-rag-chat` | **Date**: 2026-11-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-conversational-rag-chat/spec.md`

---

## Summary

Esta funcionalidade adiciona a camada conversacional de IA ao Atlas AI. Ela permite criar sessões de chat persistentes vinculadas a uma base de conhecimento, recuperar os chunks mais relevantes utilizando busca vetorial no pgvector (Cosine Distance), alimentar o modelo Google Gemini (Gemini 2.5 Flash) com um prompt rigoroso delimitado por `<context>...</context>` anti-alucinação e anti-injection, e sintetizar respostas fundamentadas acompanhadas de metadados de citação das fontes.

---

## Technical Context

**Language/Version**: Python 3.11+ / 3.14 (Backend assíncrono).

**Primary Dependencies**:
- Framework: `FastAPI` (assíncrono).
- Validação: `Pydantic v2`.
- Banco de Dados / ORM: `SQLAlchemy 2.0` (async) com `asyncpg`.
- Migrações: `Alembic`.
- IA / LLM: `google-genai` (Gemini 2.5 Flash).
- Embeddings: `GeminiEmbeddingClient` (`text-embedding-004`).
- Banco Vetorial: `pgvector-python`.

**Storage**: PostgreSQL 16+ com tabelas `chat_sessions` e `chat_messages`.

**Testing**: `pytest`, `pytest-asyncio`, `httpx`.

**Target Platform**: Linux / Docker Container.

**Project Type**: Web Service (REST API backend desacoplado no monorepo).

**Performance Goals**:
- Latência total fim a fim $< 3.5$ segundos por turno conversacional.
- Recuperação vetorial preliminar em $< 200$ ms.

**Constraints**:
- Janela deslizante de contexto: últimas 6 mensagens ($K=6$).
- Prompt delimitado com `<context>...</context>`.
- Citação obrigatória de fontes no retorno JSON.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio da Constitution | Status | Avaliação Técnica & Conformidade |
| :--- | :---: | :--- |
| **I. Monorepo & Separação** | ✅ PASS | Todo o código contido estritamente em `backend/`. API REST pura `/api/v1/knowledge-bases/{kb_id}/chats`. |
| **II. Código Limpo & Didático** | ✅ PASS | Módulos `rag_chat_service.py` e `gemini_client.py` com tipagem rigorosa e comentários didáticos sobre o prompt. |
| **III. Contratos Estritos** | ✅ PASS | Contrato OpenAPI documentado em `contracts/chat-api.yaml`. Schemas Pydantic mapeiam entradas, saídas e erros. |
| **IV. Segurança & Gestão de Segredos** | ✅ PASS | API Key gerenciada via `.env`. Delimitação rígida de contexto mitigando *prompt injection*. |
| **V. RAG Responsável & Citações** | ✅ PASS | Retorno de fontes obrigatório (`citations`), anti-alucinação explícita no prompt de sistema e métricas de tokens. |
| **VI. Simplicidade (KISS / YAGNI)** | ✅ PASS | Orquestração nativa em Python usando o SDK oficial `google-genai` sem complexidade acidental. |
| **VII. Pirâmide de Testes** | ✅ PASS | Testes unitários de formatação de prompt e testes de integração de rotas e persistência. |
| **VIII. Tratamento de Erros** | ✅ PASS | Falhas do Gemini tratadas com erro padronizado `AI_SERVICE_ERROR` sem quebrar o servidor. |
| **IX. Documentação & ADRs** | ✅ PASS | `data-model.md`, `research.md`, `contracts/` e `quickstart.md` detalham a arquitetura. |
| **X. Spec Kit Flow** | ✅ PASS | Fluxo rigoroso: `spec.md` $\rightarrow$ `plan.md` $\rightarrow$ `tasks.md` $\rightarrow$ implementação. |
| **XI. Version Control Hygiene** | ✅ PASS | Modificações atômicas rastreadas e commits controlados pelo usuário. |

---

## Project Structure

### Documentation (this feature)

```text
specs/002-conversational-rag-chat/
├── spec.md              # Requisitos de negócio e critérios de aceitação
├── plan.md              # Este plano de implementação técnica
├── research.md          # Fase 0: Decisões técnicas e engenharia de prompt
├── data-model.md        # Fase 1: Modelos de dados e ERD
├── quickstart.md        # Fase 1: Guia prático de execução com exemplos cURL
├── contracts/           # Fase 1: Especificação OpenAPI dos contratos de chat
│   └── chat-api.yaml
└── checklists/          # Checklists de qualidade
    └── requirements.md
```

### Source Code (backend components affected)

```text
backend/
├── app/
│   ├── models/
│   │   ├── chat_session.py         # Model ChatSession
│   │   └── chat_message.py         # Model ChatMessage (role, content, citations, tokens)
│   ├── schemas/
│   │   └── chat.py                 # Schemas Pydantic (SessionCreate, MessageResponse, etc.)
│   ├── services/
│   │   ├── gemini_client.py        # Expansão para suportar geração de chat (gemini-2.5-flash)
│   │   └── rag_chat_service.py     # Orquestrador RAG (recuperação pgvector + prompt + resposta)
│   └── api/
│       └── v1/
│           ├── chat.py             # Endpoints REST de sessões e mensagens
│           └── router.py           # Inclusão do router de chat
├── alembic/
│   └── versions/
│       └── 0004_create_chat_tables.py # Migração Alembic para chat_sessions e chat_messages
└── tests/
    └── integration/
        └── test_chat.py            # Testes de integração para o fluxo de chat conversacional
```

---

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| :--- | :--- | :--- |
| *Nenhuma violação identificada* | — | O design segue rigorosamente os 11 princípios da Constitution, empregando o SDK oficial do Gemini diretamente. |
