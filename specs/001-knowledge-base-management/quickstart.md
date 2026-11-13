# Quickstart: Knowledge Base Management & Document Ingestion

**Feature**: `001-knowledge-base-management`  
**Date**: 2026-11-13  
**Status**: Completed  

---

## 1. Pré-requisitos Locais

1. **Docker e Docker Compose** (para executar PostgreSQL com a extensão `pgvector`).
2. **Python 3.11+ / 3.14** com suporte a ambiente virtual (`.venv`).
3. Chave da API do Google Gemini (`GEMINI_API_KEY`).

---

## 2. Passo a Passo de Execução

### Passo 2.1 — Subir o Banco de Dados com pgvector
```bash
docker compose up -d db
```

### Passo 2.2 — Configurar Variáveis de Ambiente
Copie o arquivo de exemplo e insira sua chave do Gemini:
```bash
cp .env.example .env
# Edite .env e adicione sua GEMINI_API_KEY
```

### Passo 2.3 — Criar e Ativar o Ambiente Virtual do Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Passo 2.4 — Executar as Migrações do Banco
```bash
alembic upgrade head
```

### Passo 2.5 — Iniciar a API FastAPI
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Acesse a documentação interativa Swagger em: [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 3. Exemplos Práticos de Chamada (cURL)

### 3.1 Criar uma Base de Conhecimento
```bash
curl -X POST "http://localhost:8000/api/v1/knowledge-bases" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Manuais de Arquitetura",
    "description": "Documentos e guias técnicos de microsserviços."
  }'
```

### 3.2 Fazer Upload de um Documento (PDF / TXT / MD)
```bash
curl -X POST "http://localhost:8000/api/v1/knowledge-bases/<KB_ID>/documents" \
  -F "file=@/caminho/para/meu-documento.pdf"
```

### 3.3 Testar a Busca Semântica por Similaridade Vetorial
```bash
curl -X POST "http://localhost:8000/api/v1/knowledge-bases/<KB_ID>/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Como configurar o ambiente de desenvolvimento?",
    "limit": 3
  }'
```
Retornará os 3 trechos de texto mais semelhantes ranqueados pelo índice de cosseno do pgvector com seus metadados de origem.
