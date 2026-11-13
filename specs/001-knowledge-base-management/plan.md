# Implementation Plan: Knowledge Base Management & Document Ingestion

**Branch**: `001-knowledge-base-management` | **Date**: 2026-11-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-knowledge-base-management/spec.md`

---

## Summary

Esta funcionalidade estabelece o núcleo de dados e o pipeline de ingestão do Atlas AI. Ela permite aos usuários criar e gerenciar bases de conhecimento isoladas, fazer upload de documentos (PDF, Markdown e TXT), extrair texto limpo, particionar o conteúdo em chunks preservando contexto (chunk size 500, overlap 100), gerar embeddings de 768 dimensões utilizando o modelo `text-embedding-004` da Google Gemini API, e persistir tudo no PostgreSQL com a extensão `pgvector`. Além disso, expõe um endpoint para testes de busca vetorial por similaridade de cosseno com ranqueamento e metadados de atribuição.

---

## Technical Context

**Language/Version**: Python 3.11+ / 3.14 (Backend assíncrono).

**Primary Dependencies**: 
- Framework: `FastAPI` (com `uvicorn`).
- Validação: `Pydantic v2`.
- Banco de Dados / ORM: `SQLAlchemy 2.0` (async) com driver `asyncpg`.
- Migrações: `Alembic`.
- Banco Vetorial: `pgvector-python`.
- Manipulação de PDF: `pypdf`.
- IA / Embeddings: `google-genai` (Google Gemini API SDK).

**Storage**: PostgreSQL 16+ com extensão `pgvector`.

**Testing**: `pytest`, `pytest-asyncio`, `httpx` (para testes de integração com `TestClient`).

**Target Platform**: Linux / Docker Container.

**Project Type**: Web Service (REST API backend desacoplado no monorepo).

**Performance Goals**:
- Extração, chunking e vetorização de documento típico de 10 páginas em < 10 segundos.
- Busca vetorial por similaridade em < 200 ms para bases com até 1.000 chunks.
- Validação síncrona de uploads inválidos em < 200 ms.

**Constraints**:
- Limite máximo de arquivo: 10 MB por documento.
- Dimensão do vetor: 768 dimensões (`text-embedding-004`).
- Métrica de distância vetorial: Similaridade de Cosseno (`vector_cosine_ops`).

**Scale/Scope**: Módulo central do Backend; suporta bases arbitrárias, milhares de chunks e múltiplos formatos textuais.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio da Constitution | Status | Avaliação Técnica & Conformidade |
| :--- | :---: | :--- |
| **I. Monorepo & Separação** | ✅ PASS | Todo o código e dependências pertencem estritamente a `backend/`. Nenhuma importação ou código cruzado com o frontend. |
| **II. Código Limpo & Didático** | ✅ PASS | Pydantic v2 e type hints em 100% dos métodos. Módulos de chunking e cálculo de similaridade comentados didaticamente. |
| **III. Contratos de API Estritos** | ✅ PASS | Contrato OpenAPI documentado em `contracts/api-spec.yaml`. Schemas Pydantic mapeiam entradas, saídas e erros. |
| **IV. Segurança & Gestão de Segredos** | ✅ PASS | `GEMINI_API_KEY` e credenciais de banco injetadas via `.env`. Uploads sanitizados contra path traversal e extensões maliciosas. |
| **V. RAG Responsável & Citações** | ✅ PASS | Busca vetorial retorna metadados completos de citação (documento, chunk index, score de similaridade). |
| **VI. Simplicidade (KISS / YAGNI)** | ✅ PASS | Chunking e vetorização implementados de forma nativa e direta sem abstrações desnecessárias do LangChain. |
| **VII. Pirâmide de Testes** | ✅ PASS | Testes unitários para chunker/parser e testes de integração com FastAPI `TestClient` e banco de dados. |
| **VIII. Tratamento de Erros** | ✅ PASS | Respostas de erro estruturadas com `{ detail, code }`. Falhas de API de IA tratadas sem quebrar o servidor. |
| **IX. Documentação & ADRs** | ✅ PASS | `data-model.md`, `research.md`, `contracts/` e `quickstart.md` detalham a arquitetura. |
| **X. Spec Kit Flow** | ✅ PASS | Fluxo rigoroso: `spec.md` $\rightarrow$ `plan.md` $\rightarrow$ `tasks.md` $\rightarrow$ implementação. |
| **XI. Version Control Hygiene** | ✅ PASS | Sem commits automáticos. Modificações limitadas ao escopo da feature. |

---

## Project Structure

### Documentation (this feature)

```text
specs/001-knowledge-base-management/
├── spec.md              # Requisitos de negócio e critérios de aceitação
├── plan.md              # Este plano de implementação técnica
├── research.md          # Fase 0: Decisões técnicas e pesquisa de bibliotecas
├── data-model.md        # Fase 1: Modelos de dados, ERD e índices pgvector
├── quickstart.md        # Fase 1: Guia prático de execução e exemplos cURL
├── contracts/           # Fase 1: Especificação OpenAPI dos contratos REST
│   └── api-spec.yaml
└── checklists/          # Checklists de qualidade
    └── requirements.md
```

### Source Code (backend application layout)

```text
backend/
├── app/
│   ├── main.py                    # Inicialização do FastAPI, CORS e inclusão de rotas
│   ├── core/
│   │   ├── config.py              # Pydantic BaseSettings (GEMINI_API_KEY, DATABASE_URL)
│   │   └── exceptions.py          # Exceções customizadas e handlers de erro HTTP
│   ├── db/
│   │   ├── session.py             # Engine assíncrona SQLAlchemy e get_db session dependency
│   │   └── base.py                # Base declarativa SQLAlchemy
│   ├── models/
│   │   ├── __init__.py            # Exportação de todas as models para o Alembic
│   │   ├── knowledge_base.py      # Model KnowledgeBase
│   │   ├── document.py            # Model Document
│   │   └── document_chunk.py      # Model DocumentChunk (com Vector(768) do pgvector)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── knowledge_base.py      # Schemas Pydantic (Create, Response, Update)
│   │   ├── document.py            # Schemas Pydantic (Response, Status)
│   │   └── search.py              # Schemas Pydantic (SearchRequest, SearchResult)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── gemini_client.py       # Integração com Gemini text-embedding-004
│   │   ├── document_parser.py     # Extração de texto de PDF (pypdf), TXT e MD
│   │   ├── text_chunker.py        # Algoritmo de chunking recursivo com overlap
│   │   └── ingestion_service.py   # Orquestração do pipeline de ingestão e vetorização
│   └── api/
│       └── v1/
│           ├── __init__.py
│           ├── router.py          # APIRouter agregador de v1
│           ├── knowledge_bases.py # Endpoints de CRUD de bases de conhecimento
│           └── documents.py       # Endpoints de upload e busca semântica
├── alembic/
│   ├── env.py                     # Configuração de migração com pgvector
│   └── versions/                  # Arquivos de migração versionados
├── alembic.ini                    # Configuração do Alembic
├── tests/
│   ├── conftest.py                # Fixtures de teste e banco em memória/mock
│   ├── unit/
│   │   ├── test_chunker.py        # Testes unitários do particionador de texto
│   │   └── test_parser.py         # Testes unitários da extração de documentos
│   └── integration/
│       ├── test_knowledge_bases.py# Testes das rotas REST de bases de conhecimento
│       └── test_ingestion.py      # Testes de upload e busca vetorial
├── requirements.txt               # Dependências pinadas do backend
└── Dockerfile                     # Container Docker para o backend
```

**Structure Decision**: A estrutura modular clássica do FastAPI (`app/api`, `app/core`, `app/db`, `app/models`, `app/schemas`, `app/services`) foi adotada para garantir desacoplamento total, facilidade de injeção de dependências e testabilidade de cada componente isoladamente.

---

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| :--- | :--- | :--- |
| *Nenhuma violação identificada* | — | O design segue rigorosamente os 11 princípios da Constitution, priorizando simplicidade nativa sem sobrecarga de frameworks externos. |
