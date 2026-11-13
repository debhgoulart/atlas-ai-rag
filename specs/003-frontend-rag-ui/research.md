# Research & Technical Decisions: Frontend Knowledge Base & Interactive Chat UI

**Feature**: `003-frontend-rag-ui`  
**Date**: 2026-11-13  
**Status**: Completed  

---

## 1. Seleção e Comparativo de Tecnologias

### 1.1 Framework, Linguagem e Tooling
- **Decisão**: **Vue.js 3** com **Composition API** (`<script setup lang="ts">`), **TypeScript** (Strict Mode) e **Vite**.
- **Justificativa Didática**:
  - A Composition API com `<script setup>` proporciona código conciso, excelente inferência de tipos pelo compilador TypeScript e reatividade granular.
  - O Vite oferece servidor de desenvolvimento com *Hot Module Replacement* (HMR) instantâneo e empacotamento otimizado para produção via Rollup/esbuild.

---

### 1.2 Estilização e Ícones
- **Decisão**: **Tailwind CSS v3** integrado com a biblioteca de ícones **Lucide Vue Next**.
- **Justificativa Didática**:
  - O Tailwind CSS elimina a necessidade de folhas de estilo monolíticas e desacopladas, permitindo a construção rápida de componentes responsivos e acessíveis com um design limpo e profissional.
  - A biblioteca `lucide-vue-next` é leve, oferece suporte nativo a tree-shaking (apenas os ícones importados entram no bundle final) e fornece símbolos modernos para chat, upload, documentos e status.

---

### 1.3 Gerenciamento de Estado (State Management)
- **Decisão**: **Pinia** (gerenciador oficial de estado do ecossistema Vue 3).
- **Lojas Planejadas**:
  1. `useKnowledgeBaseStore`: Gerencia a lista de bases de conhecimento, a base atualmente selecionada, e a lista de documentos da base ativa.
  2. `useChatStore`: Gerencia as sessões de chat da base ativa, a sessão selecionada no momento, o envio de perguntas, o estado de digitação (*isThinking*) e o histórico de mensagens.
- **Vantagens**: Integração perfeita com TypeScript, sem boilerplate excessivo e compatibilidade total com a reatividade do Vue 3.

---

### 1.4 Cliente HTTP e Integração com o Backend
- **Decisão**: **Axios** com instância configurada em `src/services/api.ts`.
- **Configuração**:
  - `baseURL`: lida da variável de ambiente `import.meta.env.VITE_API_BASE_URL` (default: `http://localhost:8000/api/v1`).
  - Interceptors: Tratamento uniforme de erros HTTP 400, 404, 422 e 502, extraindo o envelope padronizado `{ detail, code }` implementado no backend.

---

### 1.5 Renderização de Mensagens e Formatação de Texto
- **Decisão**: Utilizar uma biblioteca leve de parsing de Markdown (como `marked`) combinada com sanitização básica para renderizar respostas da IA que contenham listas, cabeçalhos e blocos de código formatados com destaque sintático.
