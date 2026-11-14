# API Contract: Chat Sessions & Conversational RAG (Multi-Tenant Scoped)

**Base Path**: `/api/v1/knowledge-bases/{kb_id}/chats`
**Authentication**: Bearer JWT (`Authorization: Bearer <token>`) required on all endpoints.

## Endpoints

### 1. Create Chat Session
- **POST** `/api/v1/knowledge-bases/{kb_id}/chats`
- **Security**: `BearerAuth` (extracts `current_user`)
- **Request Body**:
  ```json
  {
    "title": "Discussão de Requisitos"
  }
  ```
- **Responses**:
  - `201 Created`: `ChatSessionResponse` (with `user_id` set to `current_user.id`)
  - `404 Not Found`: If `kb_id` belongs to another user.
  - `401 Unauthorized`: Token missing or invalid.

### 2. List Chat Sessions
- **GET** `/api/v1/knowledge-bases/{kb_id}/chats`
- **Security**: `BearerAuth` (extracts `current_user`)
- **Responses**:
  - `200 OK`: Array of `ChatSessionResponse` belonging strictly to `current_user` in `kb_id`.
  - `404 Not Found`: If `kb_id` belongs to another user.

### 3. Get Chat Session Details & History
- **GET** `/api/v1/knowledge-bases/{kb_id}/chats/{chat_id}`
- **Security**: `BearerAuth` (extracts `current_user`)
- **Responses**:
  - `200 OK`: `ChatSessionDetailResponse` (with full message history)
  - `404 Not Found`: If `chat_id` belongs to another user.

### 4. Delete Chat Session
- **DELETE** `/api/v1/knowledge-bases/{kb_id}/chats/{chat_id}`
- **Security**: `BearerAuth` (extracts `current_user`)
- **Responses**:
  - `204 No Content`: Chat session and messages deleted.
  - `404 Not Found`: If `chat_id` belongs to another user.

### 5. Send Message (RAG Turn)
- **POST** `/api/v1/knowledge-bases/{kb_id}/chats/{chat_id}/messages`
- **Security**: `BearerAuth` (extracts `current_user` and user's registered Gemini API key)
- **Request Body**:
  ```json
  {
    "content": "Quais são os pontos principais do documento?"
  }
  ```
- **Responses**:
  - `200 OK`: `ChatMessageResponse` (containing grounded assistant response and citations from `current_user`'s documents).
  - `404 Not Found`: If `chat_id` or `kb_id` does not belong to `current_user`.
