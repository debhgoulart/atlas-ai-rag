# Quickstart: Frontend Knowledge Base & Chat UI

**Feature**: `003-frontend-rag-ui`  
**Date**: 2026-11-13  
**Status**: Completed  

---

## 1. Pré-requisitos
1. **Node.js 20+ / npm 10+**.
2. Backend do Atlas AI rodando em `http://localhost:8000`.

---

## 2. Passo a Passo de Execução Local

### 2.1 Acessar a pasta do frontend e instalar dependências
```bash
cd frontend
npm install
```

### 2.2 Configurar Variáveis de Ambiente
O frontend utiliza a variável `VITE_API_BASE_URL` para apontar para a API:
```bash
echo "VITE_API_BASE_URL=http://localhost:8000/api/v1" > .env
```

### 2.3 Iniciar o Servidor de Desenvolvimento Vite
```bash
npm run dev
```
O servidor iniciará em: [http://localhost:5173](http://localhost:5173).

---

## 3. Roteiro de Teste Visual do Usuário

1. **Dashboard de Bases**:
   - Acesse `http://localhost:5173`.
   - Clique em **"Nova Base de Conhecimento"** e insira nome e descrição.
   - Veja o cartão criado aparecer na grade.
2. **Upload de Documento**:
   - Clique no cartão da base para abrir os detalhes.
   - Na aba **"Documentos"**, arraste um arquivo PDF, TXT ou Markdown para a área pontilhada.
   - Acompanhe a transição do badge para **Concluído** com o número de chunks gerados.
3. **Conversar com o Chatbot**:
   - Mude para a aba **"Chat Inteligente"**.
   - Digite uma pergunta sobre o documento enviado e pressione Enter.
   - Observe a resposta fundamentada e clique nos **pills de fontes** para inspecionar os trechos originais e a relevância.
