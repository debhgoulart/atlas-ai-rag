import { defineStore } from "pinia";
import { ref } from "vue";
import type { KnowledgeBase, KnowledgeBaseCreatePayload, DocumentItem } from "@/types";
import { knowledgeBaseService } from "@/services/knowledgeBaseService";

export const useKnowledgeBaseStore = defineStore("knowledgeBase", () => {
  const knowledgeBases = ref<KnowledgeBase[]>([]);
  const currentKnowledgeBase = ref<KnowledgeBase | null>(null);
  const documents = ref<DocumentItem[]>([]);
  const isLoading = ref<boolean>(false);
  const isUploading = ref<boolean>(false);
  const errorMessage = ref<string | null>(null);

  async function fetchKnowledgeBases() {
    isLoading.value = true;
    errorMessage.value = null;
    try {
      knowledgeBases.value = await knowledgeBaseService.listAll();
    } catch (err: any) {
      errorMessage.value = err.detail || "Erro ao carregar bases de conhecimento.";
    } finally {
      isLoading.value = false;
    }
  }

  async function selectKnowledgeBase(id: string) {
    isLoading.value = true;
    errorMessage.value = null;
    try {
      currentKnowledgeBase.value = await knowledgeBaseService.getById(id);
      await fetchDocuments(id);
    } catch (err: any) {
      errorMessage.value = err.detail || "Erro ao selecionar base de conhecimento.";
    } finally {
      isLoading.value = false;
    }
  }

  async function createKnowledgeBase(payload: KnowledgeBaseCreatePayload) {
    isLoading.value = true;
    errorMessage.value = null;
    try {
      const created = await knowledgeBaseService.create(payload);
      knowledgeBases.value.unshift(created);
      return created;
    } catch (err: any) {
      errorMessage.value = err.detail || "Erro ao criar base de conhecimento.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function deleteKnowledgeBase(id: string) {
    isLoading.value = true;
    errorMessage.value = null;
    try {
      await knowledgeBaseService.delete(id);
      knowledgeBases.value = knowledgeBases.value.filter((kb) => kb.id !== id);
      if (currentKnowledgeBase.value?.id === id) {
        currentKnowledgeBase.value = null;
        documents.value = [];
      }
    } catch (err: any) {
      errorMessage.value = err.detail || "Erro ao excluir base de conhecimento.";
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchDocuments(kbId: string) {
    try {
      documents.value = await knowledgeBaseService.listDocuments(kbId);
    } catch (err: any) {
      errorMessage.value = err.detail || "Erro ao carregar documentos.";
    }
  }

  async function uploadDocument(kbId: string, file: File) {
    isUploading.value = true;
    errorMessage.value = null;
    try {
      const doc = await knowledgeBaseService.uploadDocument(kbId, file);
      documents.value.unshift(doc);
      if (currentKnowledgeBase.value) {
        currentKnowledgeBase.value.document_count += 1;
      }
      return doc;
    } catch (err: any) {
      errorMessage.value = err.detail || "Falha no upload do documento.";
      throw err;
    } finally {
      isUploading.value = false;
    }
  }

  async function deleteDocument(kbId: string, docId: string) {
    try {
      await knowledgeBaseService.deleteDocument(kbId, docId);
      documents.value = documents.value.filter((d) => d.id !== docId);
      if (currentKnowledgeBase.value && currentKnowledgeBase.value.document_count > 0) {
        currentKnowledgeBase.value.document_count -= 1;
      }
    } catch (err: any) {
      errorMessage.value = err.detail || "Erro ao excluir documento.";
      throw err;
    }
  }

  return {
    knowledgeBases,
    currentKnowledgeBase,
    documents,
    isLoading,
    isUploading,
    errorMessage,
    fetchKnowledgeBases,
    selectKnowledgeBase,
    createKnowledgeBase,
    deleteKnowledgeBase,
    fetchDocuments,
    uploadDocument,
    deleteDocument,
  };
});
