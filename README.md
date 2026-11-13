# Atlas AI — Full Stack RAG & Knowledge Base Chatbot

O **Atlas AI** é uma aplicação web Full Stack moderna de gerenciamento de bases de conhecimento e chatbot inteligente, desenvolvida para demonstrar competências avançadas em Engenharia de Software, Engenharia de IA, Retrieval-Augmented Generation (RAG) e arquitetura de sistemas distribuídos.

---

## 🎯 Objetivos do Projeto

- **Criação e Gestão de Bases de Conhecimento**: Organização de coleções temáticas de documentos por domínios.
- **Pipeline de Ingestão e Vetorização**: Upload de documentos (PDF, Markdown, TXT), extração de texto, chunking semântico com overlap e geração de embeddings com o Google Gemini (`text-embedding-004`).
- **Armazenamento Vetorial Escalável**: Indexação e busca por similaridade de cosseno utilizando PostgreSQL com a extensão `pgvector`.
- **Chatbot Contextualizado e Confiável**: Síntese de respostas via LLM (Google Gemini) estritamente fundamentadas no contexto dos documentos ingeridos, com guardrails contra alucinações.
- **Transparência e Citação de Fontes**: Apresentação de metadados dos chunks de origem (documento, página, trecho e pontuação de relevância) para cada resposta gerada.
- **Governança com Spec Kit**: Desenvolvimento guiado por especificações formais, planos arquiteturais e tarefas atômicas independentes.

---

## 🏗️ Arquitetura Monorepo

O projeto adota uma arquitetura **Monorepo** com separação estrita de responsabilidades:

```text
atlas-ai-rag/
├── backend/             # Aplicação Python / FastAPI (REST API v1)
│   ├── alembic/         # Migrações versionadas do banco relacional + pgvector
│   ├── app/             # Camadas: models, schemas, services, api/v1
│   └── tests/           # Suíte de testes unitários e testes integrados
├── frontend/            # Aplicação SPA Vue 3 + TypeScript + Vite + Tailwind CSS
│   └── src/             # Componentes, views, stores (Pinia), services (Axios)
├── specs/               # Especificações funcionais gerenciadas pelo Spec Kit
├── docs/                # Documentação técnica e ADRs (Architectural Decision Records)
├── tests/               # Testes integrados e benchmarks
├── .specify/            # Configurações e memória da Constitution do Spec Kit
└── docker-compose.yml   # Orquestração de containers local (PostgreSQL + pgvector)
```

---

## 🛠️ Tecnologias Utilizadas

### Frontend
- **Framework**: Vue.js 3 (Composition API com `<script setup>`)
- **Linguagem**: TypeScript (Strict Mode)
- **Build Tool**: Vite
- **Gerenciamento de Estado**: Pinia
- **Roteamento**: Vue Router
- **Estilização**: Tailwind CSS
- **Ícones**: Lucide Vue Next
- **Cliente HTTP**: Axios

### Backend
- **Linguagem**: Python 3.11+
- **Framework Web**: FastAPI (endpoints assíncronos)
- **Validação de Schemas**: Pydantic v2
- **Banco de Dados & ORM**: PostgreSQL + SQLAlchemy 2.0 (async via `asyncpg`)
- **Migrações**: Alembic
- **Banco Vetorial**: Extensão `pgvector`

### Inteligência Artificial & RAG
- **LLM**: Google Gemini API (`gemini-2.5-flash` / `gemini-1.5-flash`)
- **Embeddings**: Google Gemini `text-embedding-004` (vetores densos de 768 dimensões)
- **Técnica RAG**: Chunking semântico com preservação de parágrafos, similaridade de cosseno via pgvector (`<=>`), injeção dinâmica de contexto com restrições anti-alucinação.

---

## 🚀 Como Executar Localmente

### Pré-requisitos
Certifique-se de ter instalados em seu ambiente:
- **Docker & Docker Compose** (para o PostgreSQL com `pgvector`)
- **Python 3.11+** e gerenciador `pip`
- **Node.js 20+** e `npm`
- **Chave de API do Google Gemini**: Obtenha gratuitamente no [Google AI Studio](https://aistudio.google.com/).

---

### ⚡ Opção 1: Inicialização Rápida Interativa (Recomendado)

O projeto possui um script orquestrador interativo que automatiza todo o processo a partir do zero:

```bash
# 1. Clonar o repositório
git clone git@github.com:debhgoulart/atlas-ai-rag.git
cd atlas-ai-rag

# 2. Executar o script inicializador
./start.sh
```

**O que o script `./start.sh` faz automaticamente:**
1. Apresenta instruções claras de como gerar sua chave gratuita no Google AI Studio.
2. Permite colar a chave diretamente no terminal para gravar no `.env`.
3. Sobe o container Docker do PostgreSQL com a extensão `pgvector`.
4. Aplica todas as migrações do banco com o Alembic.
5. Oferece a opção de sanitizar o banco para iniciar em estado 100% zerado.
6. Inicia o Backend FastAPI (`http://localhost:8000/docs`) e o Frontend Vue 3 (`http://localhost:5173`).
7. Encerra todos os serviços de forma graciosa ao pressionar `Ctrl + C`.

---

### 🛠️ Opção 2: Execução Manual Passo a Passo

Caso prefira iniciar cada serviço individualmente:

#### Passo 1: Configurar Variáveis de Ambiente

```bash
cp .env.example .env
```
Abra o `.env` e configure sua `GEMINI_API_KEY`.

---

### Passo 2: Iniciar o Banco de Dados com pgvector

Suba o container do PostgreSQL 16 com a extensão `pgvector` pré-instalada:

```bash
docker compose up -d db
```

Para verificar se o container está saudável:
```bash
docker compose ps
```

---

### Passo 3: Configurar e Iniciar o Backend

1. Acesse o diretório do backend e crie o ambiente virtual:
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   # No Windows (PowerShell): .venv\Scripts\Activate.ps1
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Execute as migrações do banco de dados (criação da extensão `pgvector` e de todas as tabelas):
   ```bash
   alembic upgrade head
   ```

4. Inicie o servidor da API FastAPI:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

- **Swagger / OpenAPI interativo**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

### Passo 4: Configurar e Iniciar o Frontend

Em um novo terminal, a partir da raiz do projeto:

1. Acesse o diretório do frontend:
   ```bash
   cd frontend
   ```

2. Instale os pacotes npm:
   ```bash
   npm install
   ```

3. Inicie o servidor de desenvolvimento do Vite:
   ```bash
   npm run dev
   ```

4. Abra seu navegador em:
   ```text
   http://localhost:5173
   ```

---

## 🧪 Como Executar a Suíte de Testes

O projeto conta com suíte de testes unitários e de integração automatizada:

```bash
cd backend
source .venv/bin/activate
pytest tests/ -v
```

- **Testes Unitários**: Validação dos parsers de documentos (PDF, MD, TXT) e algoritmo de chunking recursivo com overlap.
- **Testes de Integração**: Testes de ponta a ponta dos endpoints de Base de Conhecimento, Ingestão de Documentos, Busca Vetorial e Chat RAG com preservação de histórico e guardrails anti-alucinação.

---

## 🧹 Como Limpar / Zerar a Base de Dados (Zero-State)

Para reiniciar o banco em estado completamente limpo (sem documentos ou conversas de teste), preservando as migrações e a extensão `pgvector`:

```bash
cd backend
source .venv/bin/activate
python -m app.scripts.reset_db
```

---

## 💡 Fluxo de Uso Recomendado

1. **Criar uma Base de Conhecimento**:
   - No Dashboard do Atlas AI, clique em **"Nova Base de Conhecimento"**.
   - Defina um nome temático (ex: *Documentação Técnica*, *Manuais Internos*).

2. **Ingestão de Arquivos**:
   - Abra a base criada e arraste arquivos nos formatos `.pdf`, `.md` ou `.txt`.
   - O pipeline automático realiza a extração do texto bruto, divide em chunks semânticos e armazena os embeddings vetoriais de 768 dimensões.

3. **Interação com o Chat RAG**:
   - Clique na aba **"Chat RAG"** da base.
   - Envie perguntas sobre o conteúdo dos documentos.
   - O modelo fornecerá respostas sintetizadas e você poderá clicar no botão **"Ver Fontes"** para inspecionar os trechos exatos utilizados e seus respectivos graus de relevância.

---

## 📑 Decisões Arquiteturais (ADRs)

Para compreender as motivações técnicas das escolhas adotadas neste projeto, consulte:
- [ADR 0001: Estratégia de pgvector e Chunking](docs/adr/0001-pgvector-and-chunking-strategy.md)
- [ADR 0002: Engenharia de Prompt e Anti-Alucinação](docs/adr/0002-prompt-engineering-and-anti-hallucination.md)
- [Constitution do Projeto](.specify/memory/constitution.md)

---

## 📄 Licença

Distribuído sob a licença MIT. Consulte `LICENSE` para mais detalhes.
