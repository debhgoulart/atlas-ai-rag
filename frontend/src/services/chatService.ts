import { apiClient } from "./api";
import type {
  ChatSession,
  ChatSessionDetail,
  ChatMessage,
  SendMessageRequest,
} from "@/types";

export const chatService = {
  async listSessions(kbId: string): Promise<ChatSession[]> {
    const response = await apiClient.get<ChatSession[]>(`/knowledge-bases/${kbId}/chats`);
    return response.data;
  },

  async getSessionDetails(kbId: string, sessionId: string): Promise<ChatSessionDetail> {
    const response = await apiClient.get<ChatSessionDetail>(
      `/knowledge-bases/${kbId}/chats/${sessionId}`
    );
    return response.data;
  },

  async createSession(kbId: string, title?: string): Promise<ChatSession> {
    const response = await apiClient.post<ChatSession>(`/knowledge-bases/${kbId}/chats`, {
      title: title || "Nova Conversa",
    });
    return response.data;
  },

  async deleteSession(kbId: string, sessionId: string): Promise<void> {
    await apiClient.delete(`/knowledge-bases/${kbId}/chats/${sessionId}`);
  },

  async sendMessage(
    kbId: string,
    sessionId: string,
    payload: SendMessageRequest
  ): Promise<ChatMessage> {
    const response = await apiClient.post<ChatMessage>(
      `/knowledge-bases/${kbId}/chats/${sessionId}/messages`,
      payload
    );
    return response.data;
  },
};
