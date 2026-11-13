import { apiClient } from "@/services/api";
import type { GeminiKeyStatusResponse } from "@/types";

export const geminiCredentialService = {
  async getStatus(): Promise<GeminiKeyStatusResponse> {
    const response = await apiClient.get<GeminiKeyStatusResponse>("/settings/gemini-key/status");
    return response.data;
  },

  async saveKey(apiKey: string): Promise<GeminiKeyStatusResponse> {
    const response = await apiClient.post<GeminiKeyStatusResponse>("/settings/gemini-key", {
      api_key: apiKey,
    });
    return response.data;
  },

  async deleteKey(): Promise<GeminiKeyStatusResponse> {
    const response = await apiClient.delete<GeminiKeyStatusResponse>("/settings/gemini-key");
    return response.data;
  },
};
