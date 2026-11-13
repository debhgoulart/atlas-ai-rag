# Research & Technical Decisions: Knowledge Base Management & Document Ingestion

**Feature**: `001-knowledge-base-management`  
**Date**: 2026-11-13  
**Status**: Completed  

---

## 1. Seleção e Comparativo de Tecnologias

### 1.1 Extração de Texto de Documentos (PDF, TXT, Markdown)
- **Desafio**: Extrair texto puro de documentos em múltiplos formatos preservando legibilidade, quebras semânticas e tratando codificações UTF-8 com robustez.
- **Opções Analisadas**:
  1. *PyPDF / pypdf*: Biblioteca Python moderna, pura (sem dependências em C complexas), leve, ativamente mantida, excelente suporte a extração de texto por página em PDFs.
  2. *pdfminer.six*: Muito detalhada para layout, porém mais lenta e com dependências mais pesadas.
  3. *Tesseract OCR*: Útil para imagens escaneadas, porém excessivo para o escopo v1 (assumimos PDFs com camada de texto).
- **Decisão**: Utilizar `pypdf` para documentos PDF e manipuladores nativos Python (com detecção segura de encoding UTF-8/fallback Latin-1) para arquivos `.txt` e `.md`.
- **Justificativa Didática**: Mantém o backend leve, de inicialização rápida e livre de binários externos de SO desnecessários no Docker.

---

### 1.2 Estratégia de Chunking (Segmentação de Texto)
- **Desafio**: Um documento longo não pode ser vetorizado como um único bloco, pois excede o limite contextual e dilui o sinal semântico. É necessário fatiar o texto em partes menores que preservem o contexto local.
- **Decisão**: Implementar um `RecursiveCharacterChunker` nativo com:
  - `chunk_size`: 500 caracteres (ou ~100-150 tokens).
  - `chunk_overlap`: 100 caracteres (garante continuidade de raciocínio entre blocos adjacentes).
  - Separadores hierárquicos: `["\n\n", "\n", ". ", " ", ""]`.
- **Por que implementação nativa em vez de LangChain?**
  - Em conformidade com o **Princípio VI da Constitution (KISS e uso consciente de frameworks)**, um chunker recursivo puro em Python possui menos de 60 linhas de código, é determinístico, facilmente testável via pytest unitário e não adiciona a sobrecarga de dezenas de dependências do ecossistema LangChain.

---

### 1.3 Modelo de Embeddings e Cliente Google Gemini
- **Desafio**: Transformar textos em vetores densos com alta capacidade semântica para recuperação (RAG).
- **Decisão**:
  - **Provedor**: Google Gemini API.
  - **SDK**: `google-genai` (SDK unificado e oficial mais recente da Google para a API Gemini).
  - **Modelo**: `text-embedding-004`.
  - **Dimensão**: 768 dimensões.
  - **Task Type**: `RETRIEVAL_DOCUMENT` para indexar chunks e `RETRIEVAL_QUERY` para a busca de similaridade do usuário.
- **Vantagens Técnicas**:
  - `text-embedding-004` é o modelo de embedding mais recente e balanceado da Google, projetado especificamente para tarefas de recuperação semântica e RAG.
  - Possui dimensão compacta (768) em comparação a modelos de 1536 ou 3072, resultando em menor consumo de memória no banco de dados e consultas mais velozes.

---

### 1.4 Banco de Dados Vetorial: PostgreSQL + pgvector
- **Desafio**: Persistência relacional de metadados integrada à busca vetorial por similaridade, sem a necessidade de operar um segundo serviço de banco (como Pinecone ou Qdrant).
- **Decisão**: Utilizar **PostgreSQL 16+** com a extensão **`pgvector`**.
- **Métrica de Distância**: **Similaridade de Cosseno** (operador `<=>` ou função `cosine_distance`).
- **Indexação Vetorial**:
  - Para coleções pequenas e médias (< 100k chunks), o scan vetorial exato (KNN sequencial) ou índice **HNSW** (`vector_cosine_ops`) oferece o melhor compromisso entre precisão e velocidade de busca.
  - Definiremos índice HNSW com parâmetros: `m = 16`, `ef_construction = 64`.
- **ORM & Integração**:
  - `SQLAlchemy 2.0` com suporte assíncrono via `asyncpg`.
  - Pacote `pgvector-python` para mapeamento transparente do tipo `Vector(768)` nas models SQLAlchemy.
  - Migrações via `Alembic` garantindo execução de `CREATE EXTENSION IF NOT EXISTS vector;`.

---

### 1.5 Arquitetura da API REST (FastAPI)
- **Estrutura de Routers**:
  - `/api/v1/knowledge-bases`: CRUD de bases de conhecimento.
  - `/api/v1/knowledge-bases/{kb_id}/documents`: Upload multipart, listagem e status de documentos.
  - `/api/v1/knowledge-bases/{kb_id}/search`: Sonda de busca semântica vetorial.
- **Validação e Tipagem**:
  - Schemas Pydantic v2 estritos para todas as entradas e saídas.
  - Status HTTP padronizados (201 Created, 200 OK, 204 No Content, 400 Bad Request, 404 Not Found, 422 Unprocessable Entity).
