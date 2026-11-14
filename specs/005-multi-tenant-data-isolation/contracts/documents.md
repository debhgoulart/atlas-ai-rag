# API Contract: Documents & Semantic Search (Multi-Tenant Scoped)

**Base Path**: `/api/v1/knowledge-bases/{kb_id}`
**Authentication**: Bearer JWT (`Authorization: Bearer <token>`) required on all endpoints.

## Endpoints

### 1. Upload and Ingest Document
- **POST** `/api/v1/knowledge-bases/{kb_id}/documents`
- **Security**: `BearerAuth` (extracts `current_user` and retrieves registered user Gemini key)
- **Content-Type**: `multipart/form-data`
- **Form Data**:
  - `file`: binary file (PDF, TXT, MD, max 10MB)
- **Responses**:
  - `201 Created`: `DocumentResponse`
  - `400 Bad Request`: `MISSING_USER_GEMINI_KEY` or `INVALID_FILE_TYPE` or `FILE_TOO_LARGE`
  - `404 Not Found`: If `kb_id` does not exist or belongs to another user.
  - `401 Unauthorized`: Token missing or invalid.

### 2. List Documents in Knowledge Base
- **GET** `/api/v1/knowledge-bases/{kb_id}/documents`
- **Security**: `BearerAuth` (extracts `current_user`)
- **Responses**:
  - `200 OK`: Array of `DocumentResponse` (only documents owned by `current_user` in that `kb_id`).
  - `404 Not Found`: If `kb_id` belongs to another user.
  - `401 Unauthorized`: Token missing or invalid.

### 3. Get Document Details
- **GET** `/api/v1/knowledge-bases/{kb_id}/documents/{doc_id}`
- **Security**: `BearerAuth` (extracts `current_user`)
- **Responses**:
  - `200 OK`: `DocumentResponse`
  - `404 Not Found`: If `doc_id` does not exist or belongs to another user.

### 4. Delete Document
- **DELETE** `/api/v1/knowledge-bases/{kb_id}/documents/{doc_id}`
- **Security**: `BearerAuth` (extracts `current_user`)
- **Responses**:
  - `204 No Content`: Document and vector chunks deleted.
  - `404 Not Found`: If `doc_id` does not exist or belongs to another user.

### 5. Semantic Similarity Search (Direct)
- **POST** `/api/v1/knowledge-bases/{kb_id}/search`
- **Security**: `BearerAuth` (extracts `current_user`)
- **Request Body**:
  ```json
  {
    "query": "Qual a arquitetura do projeto?",
    "limit": 5,
    "similarity_threshold": 0.5
  }
  ```
- **Responses**:
  - `200 OK`: Array of `SimilaritySearchResult` strictly constrained to `current_user.id` and `kb_id`.
  - `404 Not Found`: If `kb_id` belongs to another user.
