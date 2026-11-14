# 🌌 Atlas AI — Full Stack RAG & Knowledge Base Engine

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![pgvector](https://img.shields.io/badge/pgvector-Vector_Search-4169E1?style=for-the-badge&logo=databricks&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js_3-TypeScript-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

<p align="center">
  <b>Motor completo de Recuperação Aumentada por Geração (RAG) de nível de produção.</b><br>
  Desenvolvido com arquitetura assíncrona desacoplada, indexação vetorial nativa em PostgreSQL via <code>pgvector</code>, guardrails estritos contra alucinações e interface reativa moderna.
</p>

[Visão Geral](#-visão-geral) • [Demonstração Visual](#-demonstração-visual) • [Decisões Arquiteturais](#-decisões-arquiteturais--estudo-de-caso) • [Arquitetura](#-arquitetura-do-sistema) • [Como Executar](#-como-executar-localmente) • [Roadmap](#-roadmap-e-evoluções-futuras)

</div>

---

## 🎯 Visão Geral

O **Atlas AI** é uma solução *Full Stack* voltada para a gestão de bases de conhecimento e conversação contextualizada via **Retrieval-Augmented Generation (RAG)**. O projeto foi projetado para demonstrar competências sólidas em **Engenharia de Software**, **Engenharia de IA** e **Arquitetura de Sistemas Distribuídos**, superando a fragilidade de tutoriais genéricos e scripts em notebooks ao adotar padrões corporativos reais:

- **Bases de Conhecimento Multidomínio**: Criação, isolamento e gestão de coleções documentais independentes.
- **Pipeline de Ingestão e Chunking Semântico**: Processamento de arquivos heterogêneos (`.pdf`, `.md`, `.txt`), segmentação recursiva preservando limites conceituais e geração de embeddings densos via Google Gemini (`text-embedding-004`).
- **Recuperação Vetorial em Banco de Produção**: Consultas de similaridade por cosseno (`<=>`) executadas diretamente no PostgreSQL através da extensão `pgvector`, com suporte a índices HNSW de alta performance.
- **Guardrails Anti-Alucinação Estritos**: Prompt de sistema projetado para tolerância zero a invenções e mitigação de *prompt injection*, garantindo respostas factuais com atribuição explícita de fontes.
- **Transparência e Métricas em Tempo Real**: Exibição detalhada para o usuário final de scores de similaridade, trechos documentais consultados, tempo de latência e consumo de tokens.
- **Segurança de Credenciais (BYOK - Bring Your Own Key)**: Criptografia simétrica em repouso com Fernet (AES-128-CBC + HMAC) para armazenamento isolado de chaves por usuário.

---

## 🧠 Decisões Arquiteturais & Estudo de Caso

O projeto foi construído sob uma governança formal orientada a **ADRs (Architectural Decision Records)**. Abaixo destacam-se os principais pilares técnicos:

### 1. Por que PostgreSQL + `pgvector` em vez de bancos vetoriais isolados?
Bancos puramente vetoriais em nuvem (como Pinecone ou Qdrant) resolvem a busca por similaridade, mas adicionam complexidade acentuada em aplicações reais:
- **Transações ACID e Consistência Relacional**: No Atlas AI, a deleção de uma base ou documento remove imediatamente seus metadados, arquivos e chunks vetoriais em uma única transação relacional (`ON DELETE CASCADE`), sem risco de dados órfãos.
- **Filtros Híbridos Simples**: Permite combinar cláusulas relacionais padrão (`WHERE kb_id = ... AND user_id = ...`) com ordenação vetorial (`ORDER BY embedding <=> query_embedding`) em uma única query SQL otimizada.
- **Simplicidade Operacional (Princípio KISS)**: Uma única infraestrutura de banco de dados para dados relacionais e vetoriais, viabilizando deploy local simplificado com `docker compose` ou em produção via PostgreSQL gerenciado.

*(Mais detalhes em: [ADR 0001: Estratégia de pgvector e Chunking](docs/adr/0001-pgvector-and-chunking-strategy.md))*

---

### 2. Chunking Recursivo Nativo vs. Frameworks Pesados
Em vez de importar bibliotecas inchadas que adicionam centenas de dependências indiretas, implementamos um fatiador recursivo nativo (`RecursiveTextChunker`):
- Segmenta textos respeitando uma hierarquia natural: **parágrafos (`\n\n`) $\to$ quebras de linha (`\n`) $\to$ sentenças (`. `) $\to$ palavras (` `)**.
- Adota **tamanho de 500 caracteres com overlap de 100 caracteres**, garantindo continuidade semântica e evitando que conceitos essenciais sejam cortados bruscamente na fronteira entre blocos.

---

### 3. Guardrails Anti-Alucinação e Delimitação Estrita (`<context>`)
A síntese de respostas em RAG corporativo exige precisão cirúrgica:
- **Isolamento XML**: Os chunks recuperados da base são injetados em um bloco delimitado por `<context> ... </context>`. O prompt de sistema instrui o modelo a interpretar esse conteúdo exclusivamente como dados factuais passivos, imunizando o assistente contra ataques de *prompt injection* contidos nos próprios documentos.
- **Tolerância Zero a Alucinações**: Caso o contexto recuperado não contenha evidências explícitas e inequívocas para responder à pergunta, o assistente é instruído a emitir compulsoriamente a resposta segura: *"Desculpe, não encontrei informações sobre este tema nos documentos da base de conhecimento."*

*(Mais detalhes em: [ADR 0002: Prompt Engineering e Anti-Alucinação](docs/adr/0002-prompt-engineering-and-anti-hallucination.md))*

---

### 🔬 Estudo de Caso Prático: Os Desafios do Naive RAG vs. Advanced RAG

Durante a bateria de validações com dados reais (upload simultâneo do *Deck de Cultura do iFood* com 39 páginas e um *Currículo Profissional* de 1 página), executamos a seguinte consulta comparativa:

> **Usuário:** *"O meu currículo está de acordo com o deck de cultura do ifood?"*
> 
> **Resultado da Aplicação:** O sistema retornou o aviso padrão anti-alucinação: *"Desculpe, não encontrei informações sobre este tema nos documentos da base de conhecimento."*

#### Diagnóstico Técnico da Causa Raiz:
1. **Gargalo do Top-K Fixo ($K=5$) e Disparidade de Volume**: O deck possui 39 páginas (gerando dezenas de chunks), enquanto o currículo possui apenas 1 página (gerando 2 chunks). Como a consulta enfatizou termos como "cultura" e "ifood", os 5 resultados com maior similaridade de cosseno foram todos pertencentes ao deck de cultura.
2. **Ausência do Currículo no Contexto do LLM**: Nenhum chunk do currículo esteve presente entre os 5 trechos enviados ao Gemini.
3. **Comportamento Confiável do Guardrail**: Em vez de fabricar uma análise ou alucinar sobre um currículo ausente, o modelo identificou a insuficiência de dados e ativou corretamente o guardrail de segurança.

#### 💡 Soluções e Evoluções Mapeadas (Roadmap v1.1):
- **Decomposição de Query (*Query Decomposition*)**: Pré-processamento via LLM para desmembrar perguntas comparativas em duas sub-consultas vetoriais separadas (uma para o currículo e outra para os pilares de cultura).
- **Recuperação Balanceada / MMR (*Maximal Marginal Relevance*)**: Forçar diversidade documental para garantir representatividade de múltiplos arquivos no contexto final.
- **Reranking com Cross-Encoder**: Elevar o corte inicial para $K=15$ e reordenar semanticamente antes da montagem do prompt.

---

### 4. Segurança e Isolamento de Chaves (BYOK)
- **Criptografia Simétrica Fernet**: As chaves de API dos usuários são criptografadas em repouso no banco de dados com chave mestra de alta entropia.
- **Desacoplamento de Custos**: Nenhum custo de LLM é centralizado no servidor; cada usuário opera com suas próprias cotas seguras do Google AI Studio.

*(Mais detalhes em: [ADR 0003: Criptografia de Credenciais e Isolamento](docs/adr/0003-user-credentials-encryption-and-isolation.md))*

---

## 🏗️ Arquitetura do Sistema

O Atlas AI segue o padrão **Monorepo** com separação explícita de responsabilidades em camadas desacopladas:

```text
atlas-ai-rag/
├── backend/                  # API REST Assíncrona (FastAPI + Python 3.11+)
│   ├── alembic/              # Migrações versionadas do banco relacional + pgvector
│   ├── app/
│   │   ├── api/v1/           # Rotas REST organizadas por domínio (auth, kb, chat, docs)
│   │   ├── core/             # Configurações, segurança JWT, Fernet e exceções
│   │   ├── db/               # Sessão assíncrona do SQLAlchemy 2.0 (asyncpg)
│   │   ├── models/           # Entidades relacionais e vetoriais do banco
│   │   ├── schemas/          # Contratos de dados Pydantic v2
│   │   └── services/         # Regras de negócio, Ingestão, Chunker e Cliente Gemini
│   └── tests/                # Suíte de testes unitários e de integração
├── frontend/                 # Single Page Application (Vue 3 + Vite + Tailwind CSS)
│   └── src/
│       ├── components/       # Componentes reativos reutilizáveis
│       ├── stores/           # Gerenciamento de estado global com Pinia
│       ├── views/            # Telas da aplicação (Dashboard, Base Detail, Chat RAG)
│       └── services/         # Integração HTTP com a API via Axios
├── docs/                     # Documentação viva, assets visuais e ADRs
├── specs/                    # Especificações funcionais guiadas pelo Spec Kit
└── docker-compose.yml        # Orquestrador local do banco PostgreSQL com pgvector
```

---

## 🛠️ Tecnologias e Ferramentas

| Camada | Tecnologia | Propósito / Benefício |
|---|---|---|
| **Backend** | Python 3.11+ / FastAPI | Alto throughput com I/O assíncrono nativo e documentação OpenAPI automática |
| **Banco Relacional & Vetorial** | PostgreSQL 16 + `pgvector` | Armazenamento híbrido ACID para dados relacionais e busca por similaridade de cosseno |
| **ORM & Migrações** | SQLAlchemy 2.0 / Alembic | Modelagem assíncrona com `asyncpg` e versionamento determinístico de esquemas |
| **Embeddings & LLM** | Google Gemini API | `text-embedding-004` (768 dimensões) e `gemini-2.5-flash` para geração rápida e de baixo custo |
| **Frontend** | Vue.js 3 + TypeScript | Interface reativa orientada a componentes com Composition API e tipagem estrita |
| **Estilização & UI** | Tailwind CSS + Lucide Icons | Design moderno, responsivo e focado em experiência do desenvolvedor |
| **Gerenciamento de Estado** | Pinia | Reatividade global centralizada com suporte a TypeScript |
| **Ambiente & Deploy** | Docker Compose | Reproducibilidade garantida para desenvolvimento e integração contínua |

---

## 🚀 Como Executar Localmente

### Pré-requisitos
- **Docker & Docker Compose** (para subir o PostgreSQL com `pgvector`)
- **Python 3.11+** e `pip`
- **Node.js 20+** e `npm`
- **Chave de API do Google Gemini**: Obtenha gratuitamente no [Google AI Studio](https://aistudio.google.com/).

---

### ⚡ Opção 1: Inicialização Rápida Automatizada (Recomendado)

O projeto conta com um script de automação (`start.sh`) que configura e sobe o ecossistema completo:

```bash
# 1. Clonar o repositório
git clone https://github.com/debhgoulart/atlas-ai-rag.git
cd atlas-ai-rag

# 2. Executar o inicializador interativo
./start.sh
```

**O que o `./start.sh` orquestra automaticamente:**
1. Guia o usuário caso ainda não possua a chave do Google Gemini configurada.
2. Inicia o container Docker do PostgreSQL com `pgvector`.
3. Aplica automaticamente as migrações do Alembic.
4. Oferece opção de sanitização do banco para inicialização limpa (*zero-state*).
5. Inicia o Backend FastAPI (`http://localhost:8000/docs`) e o Frontend Vue 3 (`http://localhost:5173`).
6. Trata o encerramento gracioso dos processos ao pressionar `Ctrl + C`.

---

### 🛠️ Opção 2: Execução Manual Passo a Passo

<details>
<summary><b>Clique para expandir as instruções manuais detalhadas</b></summary>

#### Passo 1: Configurar Variáveis de Ambiente
```bash
cp .env.example .env
```
Edite o arquivo `.env` inserindo sua chave `GEMINI_API_KEY` e gerando chaves secretas para `SECRET_KEY` e `CREDENTIALS_ENCRYPTION_KEY`.

#### Passo 2: Subir o Banco de Dados Vetorial
```bash
docker compose up -d db
```

#### Passo 3: Configurar e Rodar o Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate       # No Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- **Documentação Swagger**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

#### Passo 4: Configurar e Rodar o Frontend
Em outro terminal:
```bash
cd frontend
npm install
npm run dev
```
- **Aplicação Web**: [http://localhost:5173](http://localhost:5173)

</details>

---

## 🧪 Suíte de Testes Automatizados

O projeto conta com testes automatizados cobrindo tanto regras puras quanto fluxos integrados de ponta a ponta:

```bash
cd backend
source .venv/bin/activate
pytest tests/ -v
```

- **Testes Unitários**: Validação dos parsers de arquivo (PDF, Markdown, TXT) e algoritmo do `RecursiveTextChunker`.
- **Testes de Integração**: Endpoints de bases de conhecimento, upload de arquivos, busca vetorial e conversação RAG com verificação de histórico e guardrails anti-alucinação.

---

## 🗺️ Roadmap e Evoluções Futuras

- [ ] **Advanced RAG — Query Decomposition**: Decompor perguntas comparativas e complexas em múltiplos sub-vetores de busca.
- [ ] **Hybrid Search (BM25 + Dense Embeddings)**: Combinar busca por palavras-chave com busca semântica para queries técnicas com termos específicos.
- [ ] **Re-ranking com Cross-Encoder**: Refinar a lista dos top chunks recuperados antes do envio ao modelo gerador.
- [ ] **Avaliação Contínua com RAG Triad**: Integrar métricas de *Context Relevance*, *Groundedness* e *Answer Relevance* via Ragas/TruLens.
- [ ] **Suporte a Novas Fontes**: Ingestão direta de áudio via Whisper, planilhas CSV/XLSX e integração com Google Drive.

---

## 👩‍💻 Autora

<div align="center">

**Deborah de Oliveira Goulart**  
*Graduanda em Ciência da Computação • Desenvolvedora Backend & Engenharia de IA*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/deborahgoulart)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/debhgoulart)
[![Portfólio](https://img.shields.io/badge/Portfólio-Web-8A2BE2?style=for-the-badge&logo=vercel&logoColor=white)](https://deborah-goulart-portifolio.vercel.app/)
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:debh.goulart@gmail.com)

</div>

---

## 📄 Licença

Este projeto está sob a licença [MIT](LICENSE). Sinta-se livre para estudar, sugerir melhorias ou utilizá-lo como referência técnica!
