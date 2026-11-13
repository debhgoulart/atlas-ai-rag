export type ApiKeyStatus = "NOT_CONFIGURED" | "VALID" | "INVALID";

export interface GeminiKeyStatusResponse {
  status: ApiKeyStatus;
  key_hint: string | null;
  last_validated_at: string | null;
  updated_at: string | null;
}

export interface GeminiKeyCreatePayload {
  api_key: string;
}
