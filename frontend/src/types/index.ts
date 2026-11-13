/**
 * Core TypeScript contracts for Atlas AI frontend.
 * Strictly mirrors backend schemas and OpenAPI contracts.
 */

export interface KnowledgeBase {
  id: string;
  name: string;
  description: string | null;
  document_count: number;
  created_at: string;
  updated_at: string;
}

export interface KnowledgeBaseCreatePayload {
  name: string;
  description?: string;
}

export type DocumentStatus = "pending" | "processing" | "completed" | "failed";

export interface DocumentItem {
  id: string;
  knowledge_base_id: string;
  filename: string;
  content_type: string;
  file_size_bytes: number;
  status: DocumentStatus;
  error_message: string | null;
  chunk_count: number;
  created_at: string;
  updated_at: string;
}

export interface CitationItem {
  chunk_id: string;
  document_id: string;
  document_name: string;
  chunk_index: number;
  similarity_score: number;
  content_snippet: string;
}

export interface ChatMessage {
  id: string;
  chat_session_id: string;
  role: "user" | "assistant";
  content: string;
  citations: CitationItem[];
  prompt_tokens?: number | null;
  completion_tokens?: number | null;
  latency_ms?: number | null;
  created_at: string;
}

export interface ChatSession {
  id: string;
  knowledge_base_id: string;
  title: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface ChatSessionDetail extends ChatSession {
  messages: ChatMessage[];
}

export interface ApiError {
  detail: string;
  code: string;
}
