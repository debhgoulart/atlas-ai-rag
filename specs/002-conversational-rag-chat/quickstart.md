# Quickstart: Conversational RAG & Chatbot Engine

**Feature**: `002-conversational-rag-chat`  
**Date**: 2026-11-13  
**Status**: Completed  

---

## 1. Pré-requisitos
1. Backend rodando localmente (`http://localhost:8000`).
2. PostgreSQL com pgvector ativo via Docker.
3. Chave da API Gemini configurada (`GEMINI_API_KEY`).
4. Ao menos uma Base de Conhecimento com documentos processados.

---

## 2. Exemplos Práticos de Chamada (cURL)

### 2.1 Criar uma Sessão de Conversa
```bash
curl -X POST "http://localhost:8000/api/v1/knowledge-bases/<KB_ID>/chats" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Perguntas sobre Arquitetura"
  }'
```
Retorna o `id` da sessão de chat criada (`CHAT_ID`).

### 2.2 Enviar uma Pergunta e Receber Resposta RAG com Citações
```bash
curl -X POST "http://localhost:8000/api/v1/knowledge-bases/<KB_ID>/chats/<CHAT_ID>/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Como é calculado o índice de proximidade entre os vetores de texto?"
  }'
```
Retorna a resposta do assistente sintetizada pelo Gemini Flash, junto com o array `citations` contendo o documento de origem, trecho e pontuação de similaridade de cosseno.

### 2.3 Obter Histórico Completo do Diálogo
```bash
curl -X GET "http://localhost:8000/api/v1/knowledge-bases/<KB_ID>/chats/<CHAT_ID>"
```
Retorna todas as mensagens da sessão em ordem cronológica.
