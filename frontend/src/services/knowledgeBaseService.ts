import { apiClient } from "./api";
import type {
  KnowledgeBase,
  KnowledgeBaseCreatePayload,
  DocumentItem,
} from "@/types";

export const knowledgeBaseService = {
  async listAll(skip = 0, limit = 50): Promise<KnowledgeBase[]> {
    const response = await apiClient.get<KnowledgeBase[]>("/knowledge-bases", {
      params: { skip, limit },
    });
    return response.data;
  },

  async getById(id: string): Promise<KnowledgeBase> {
    const response = await apiClient.get<KnowledgeBase>(`/knowledge-bases/${id}`);
    return response.data;
  },

  async create(payload: KnowledgeBaseCreatePayload): Promise<KnowledgeBase> {
    const response = await apiClient.post<KnowledgeBase>("/knowledge-bases", payload);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/knowledge-bases/${id}`);
  },

  async listDocuments(kbId: string): Promise<DocumentItem[]> {
    const response = await apiClient.get<DocumentItem[]>(`/knowledge-bases/${kbId}/documents`);
    return response.data;
  },

  async uploadDocument(kbId: string, file: File): Promise<DocumentItem> {
    const formData = new FormData();
    formData.append("file", file);
    const response = await apiClient.post<DocumentItem>(
      `/knowledge-bases/${kbId}/documents`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    return response.data;
  },

  async deleteDocument(kbId: string, docId: string): Promise<void> {
    await apiClient.delete(`/knowledge-bases/${kbId}/documents/${docId}`);
  },
};
