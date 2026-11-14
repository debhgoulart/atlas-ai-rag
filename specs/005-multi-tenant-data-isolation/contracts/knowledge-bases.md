# API Contract: Knowledge Bases (Multi-Tenant Scoped)

**Base Path**: `/api/v1/knowledge-bases`
**Authentication**: Bearer JWT (`Authorization: Bearer <token>`) required on all endpoints.

## Endpoints

### 1. Create Knowledge Base
- **POST** `/api/v1/knowledge-bases`
- **Security**: `BearerAuth` (extracts `current_user`)
- **Request Body**:
  ```json
  {
    "name": "BTS",
    "description": "Base de conhecimento da BTS"
  }
  ```
- **Responses**:
  - `201 Created`:
    ```json
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "name": "BTS",
      "description": "Base de conhecimento da BTS",
      "document_count": 0,
      "created_at": "2026-11-14T03:00:00Z",
      "updated_at": "2026-11-14T03:00:00Z"
    }
    ```
  - `400 Bad Request`:
    ```json
    {
      "detail": "Já existe uma base de conhecimento com este nome para este usuário.",
      "code": "DUPLICATE_ENTITY"
    }
    ```
  - `401 Unauthorized`: Token missing or invalid.

### 2. List Knowledge Bases
- **GET** `/api/v1/knowledge-bases?skip=0&limit=20`
- **Security**: `BearerAuth` (extracts `current_user`)
- **Query Params**:
  - `skip`: int (default: 0)
  - `limit`: int (default: 20)
- **Responses**:
  - `200 OK`: Returns an array of `KnowledgeBaseResponse` belonging **only** to `current_user`.
  - `401 Unauthorized`: Token missing or invalid.

### 3. Get Knowledge Base by ID
- **GET** `/api/v1/knowledge-bases/{kb_id}`
- **Security**: `BearerAuth` (extracts `current_user`)
- **Responses**:
  - `200 OK`: `KnowledgeBaseResponse`
  - `404 Not Found`: If `kb_id` does not exist OR belongs to another user (anti-enumeration).
  - `401 Unauthorized`: Token missing or invalid.

### 4. Delete Knowledge Base
- **DELETE** `/api/v1/knowledge-bases/{kb_id}`
- **Security**: `BearerAuth` (extracts `current_user`)
- **Responses**:
  - `204 No Content`: Successfully deleted knowledge base and cascade children.
  - `404 Not Found`: If `kb_id` does not exist OR belongs to another user.
  - `401 Unauthorized`: Token missing or invalid.
