# Implementation Plan: Frontend Knowledge Base & Interactive Chat UI

**Branch**: `003-frontend-rag-ui` | **Date**: 2026-11-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/003-frontend-rag-ui/spec.md`

---

## Summary

Esta funcionalidade implementa a aplicação Single Page Application (SPA) do Atlas AI. Construída em Vue.js 3 com TypeScript, Tailwind CSS, Pinia e Vite, a interface fornece gerenciamento visual de bases de conhecimento, upload de documentos (PDF, TXT, MD) com monitoramento do processamento vetorial em tempo real, e uma experiência de chat interativa com balões estilizados, histórico multi-turn e gavetas expansíveis para auditoria de fontes e scores de similaridade RAG.

---

## Technical Context

**Language/Version**: TypeScript 5+ (Strict Mode) / ECMAScript 2022+.

**Primary Dependencies**:
- Framework: `Vue.js 3.5+` (Composition API com `<script setup lang="ts">`).
- Build Tool: `Vite 5+`.
- State Management: `Pinia 2+`.
- Routing: `Vue Router 4+`.
- Styling: `Tailwind CSS 3+`, `@tailwindcss/typography`.
- Icons: `lucide-vue-next`.
- HTTP Client: `axios`.
- Markdown: `marked`.

**Storage**: Armazenamento reativo em memória via Pinia; sem persistência local sensível (Single Source of Truth no backend).

**Testing**: `vitest` / `@vue/test-utils` para componentes; validação visual e E2E.

**Target Platform**: Web Browsers Modernos (Chrome, Firefox, Safari, Edge) em Desktop e Mobile.

**Project Type**: Single Page Application (Frontend desacoplado no Monorepo em `/frontend`).

**Performance Goals**:
- Carregamento inicial da página $< 1.2$ segundos.
- Resposta visual instantânea a interações do usuário $< 100$ ms.

**Constraints**:
- Comunicação estritamente restrita a chamadas REST para `/api/v1` via Axios.
- Tipagem TypeScript espelhando 100% dos contratos OpenAPI gerados pelo backend.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio da Constitution | Status | Avaliação Técnica & Conformidade |
| :--- | :---: | :--- |
| **I. Monorepo & Separação** | ✅ PASS | Todo o código e dependências pertencem estritamente a `/frontend`. Nenhuma importação de arquivos do backend. |
| **II. Código Limpo & Tipado** | ✅ PASS | TypeScript em modo estrito, interfaces explícitas e componentes Vue 3 autoexplicativos. |
| **III. Contratos Estritos** | ✅ PASS | Tipos TypeScript espelham exatamente os contratos OpenAPI das features 001 e 002. |
| **IV. Segurança & Gestão de Segredos** | ✅ PASS | Sem credenciais no frontend; URL da API injetada via `VITE_API_BASE_URL`. |
| **V. RAG Responsável & Citações** | ✅ PASS | Interface exibe badges de similaridade e pills clicáveis com o trecho exato de cada fonte. |
| **VI. Simplicidade (KISS / YAGNI)** | ✅ PASS | Arquitetura limpa de componentes Vue, Tailwind utilitário e Pinia sem complexidade desnecessária. |
| **VII. Pirâmide de Testes** | ✅ PASS | Componentes testáveis isoladamente e tipos verificados pelo compilador `vue-tsc`. |
| **VIII. Tratamento de Erros** | ✅ PASS | Interceptor de erro Axios mapeando `{ detail, code }` para notificações amigáveis na UI. |
| **IX. Documentação & ADRs** | ✅ PASS | `data-model.md`, `research.md`, `contracts/` e `quickstart.md` detalham a arquitetura. |
| **X. Spec Kit Flow** | ✅ PASS | Fluxo rigoroso: `spec.md` $\rightarrow$ `plan.md` $\rightarrow$ `tasks.md` $\rightarrow$ implementação. |
| **XI. Version Control Hygiene** | ✅ PASS | Commits atômicos sob autorização explícita do usuário. |

---

## Project Structure

### Documentation (this feature)

```text
specs/003-frontend-rag-ui/
├── spec.md              # Requisitos funcionais e critérios de aceitação
├── plan.md              # Este plano de implementação técnica
├── research.md          # Fase 0: Decisões técnicas e bibliotecas
├── data-model.md        # Fase 1: Arquitetura de componentes e interfaces
├── quickstart.md        # Fase 1: Guia prático de execução local
├── contracts/           # Fase 1: Contratos TypeScript da API
│   └── frontend-contracts.ts
└── checklists/          # Checklists de qualidade
    └── requirements.md
```

### Source Code (frontend application layout)

```text
frontend/
├── index.html                   # HTML base da SPA
├── package.json                 # Dependências e scripts npm
├── tsconfig.json                # Configuração estrita do TypeScript
├── vite.config.ts               # Configuração do Vite com aliases e proxies
├── tailwind.config.js           # Configuração de temas e cores do Tailwind
├── postcss.config.js            # Processador PostCSS para Tailwind
├── src/
│   ├── main.ts                  # Inicializador da aplicação Vue, Pinia e Router
│   ├── App.vue                  # Componente raiz com Header e RouterView
│   ├── assets/
│   │   └── main.css             # Diretivas do Tailwind CSS
│   ├── types/
│   │   └── index.ts             # Tipos e contratos TypeScript
│   ├── services/
│   │   ├── api.ts               # Instância Axios e interceptors
│   │   ├── knowledgeBaseService.ts # Métodos HTTP para bases e documentos
│   │   └── chatService.ts       # Métodos HTTP para sessões e mensagens
│   ├── stores/
│   │   ├── knowledgeBaseStore.ts # Loja Pinia para bases e documentos
│   │   └── chatStore.ts         # Loja Pinia para sessões e mensagens
│   ├── router/
│   │   └── index.ts             # Definição de rotas do Vue Router
│   ├── components/
│   │   ├── Navbar.vue           # Barra de navegação superior
│   │   ├── KnowledgeBaseCard.vue# Cartão de base com contagem e ações
│   │   ├── CreateKBModal.vue    # Modal de criação de base
│   │   ├── FileDropzone.vue     # Área de upload com drag-and-drop
│   │   ├── DocumentTable.vue    # Tabela de documentos e badges de status
│   │   ├── ChatSidebar.vue      # Menu lateral com lista de sessões
│   │   ├── MessageBubble.vue    # Balão de mensagem (markdown + citações)
│   │   ├── CitationModal.vue    # Popover/modal com trecho original da fonte
│   │   └── ChatInputBar.vue     # Campo de texto e botão de envio com loading
│   └── views/
│       ├── DashboardView.vue    # Tela inicial com grade de bases
│       └── KnowledgeBaseDetailView.vue # Tela detalhada com abas Documentos e Chat
└── Dockerfile                   # Container de produção (Nginx para arquivos estáticos)
```

---

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| :--- | :--- | :--- |
| *Nenhuma violação identificada* | — | O design segue rigorosamente os 11 princípios da Constitution, usando a stack oficial Vue 3 + Tailwind. |
