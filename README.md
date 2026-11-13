# Atlas AI — Full Stack RAG & Knowledge Base Chatbot

O **Atlas AI** é uma aplicação web Full Stack moderna de gerenciamento de bases de conhecimento e chatbot inteligente, desenvolvida para demonstrar competências avançadas em Engenharia de Software, Engenharia de IA, Retrieval-Augmented Generation (RAG) e arquitetura de sistemas distribuídos.

---

## 🎯 Objetivos do Projeto

- **Criação e Gestão de Bases de Conhecimento**: Organização de coleções temáticas de documentos por domínios.
- **Pipeline de Ingestão e Vetorização**: Upload de documentos (PDF, Markdown, TXT), extração de texto, chunking semântico e geração de embeddings com o Google Gemini (`text-embedding-004`).
- **Armazenamento Vetorial Escalável**: Indexação e busca por similaridade de cosseno utilizando PostgreSQL com a extensão `pgvector`.
- **Chatbot Contextualizado e Confiável**: Síntese de respostas via LLM (Google Gemini) estritamente fundamentadas no contexto dos documentos ingeridos.
- **Transparência e Citação de Fontes**: Apresentação de metadados dos chunks de origem (documento, página, trecho e pontuação de relevância) para cada resposta gerada.
- **Governança com Spec Kit**: Desenvolvimento orientado a especificações, planos arquiteturais e tarefas atômicas independentes.

---

## 🏗️ Arquitetura Monorepo

O projeto adota uma arquitetura **Monorepo** com separação estrita de responsabilidades:

```text
atlas-ai-rag/
├── backend/             # Aplicação Python / FastAPI (REST API v1)
├── frontend/            # Aplicação Vue.js 3 + TypeScript + Vite + Tailwind CSS
├── specs/               # Especificações funcionais gerenciadas pelo Spec Kit
├── docs/                # Documentação técnica e ADRs (Architectural Decision Records)
├── tests/               # Testes integrados e benchmarks de avaliação RAG
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
- **Linguagem**: Python 3
- **Framework Web**: FastAPI (endpoints assíncronos)
- **Validação de Schemas**: Pydantic v2
- **Banco de Dados & ORM**: PostgreSQL + SQLAlchemy 2.0 (async)
- **Migrações**: Alembic
- **Banco Vetorial**: Extensão `pgvector`

### Inteligência Artificial & RAG
- **LLM**: Google Gemini API (Gemini 2.5 Flash / Pro)
- **Embeddings**: Google Gemini `text-embedding-004` (768 dimensões)
- **Técnica RAG**: Chunking com overlap, busca vetorial por similaridade de cosseno, contextualização estrita anti-alucinação.

---

## 📜 Governança e Constitution

O projeto é regido pela [Constitution do Atlas AI](.specify/memory/constitution.md) (v1.0.0), que estabelece 11 princípios não negociáveis para qualidade de código, segurança, transparência de IA e desenvolvimento incremental.

---

## 🚀 Como Executar Localmente

### Pré-requisitos
- Docker & Docker Compose
- Python 3.11+ com suporte a ambiente virtual (`.venv`)
- Node.js 20+ e npm

*(Instruções detalhadas de execução e deploy serão expandidas conforme as etapas forem implementadas).*
