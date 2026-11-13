import { defineStore } from "pinia";
import { ref } from "vue";
import type { ChatMessage, ChatSession, ChatSessionDetail } from "@/types";
import { chatService } from "@/services/chatService";

export const useChatStore = defineStore("chat", () => {
  const sessions = ref<ChatSession[]>([]);
  const currentSession = ref<ChatSessionDetail | null>(null);
  const isThinking = ref<boolean>(false);
  const isLoadingSessions = ref<boolean>(false);
  const errorMessage = ref<string | null>(null);

  async function fetchSessions(kbId: string) {
    isLoadingSessions.value = true;
    errorMessage.value = null;
    try {
      sessions.value = await chatService.listSessions(kbId);
      if (sessions.value.length > 0 && !currentSession.value) {
        await selectSession(kbId, sessions.value[0].id);
      }
    } catch (err: any) {
      errorMessage.value = err.detail || "Erro ao carregar sessões de conversa.";
    } finally {
      isLoadingSessions.value = false;
    }
  }

  async function selectSession(kbId: string, sessionId: string) {
    errorMessage.value = null;
    try {
      currentSession.value = await chatService.getSessionDetails(kbId, sessionId);
    } catch (err: any) {
      errorMessage.value = err.detail || "Erro ao carregar histórico da sessão.";
    }
  }

  async function createSession(kbId: string, title?: string) {
    errorMessage.value = null;
    try {
      const newSession = await chatService.createSession(kbId, title);
      sessions.value.unshift(newSession);
      currentSession.value = {
        ...newSession,
        messages: [],
      };
      return newSession;
    } catch (err: any) {
      errorMessage.value = err.detail || "Erro ao criar sessão de conversa.";
      throw err;
    }
  }

  async function deleteSession(kbId: string, sessionId: string) {
    try {
      await chatService.deleteSession(kbId, sessionId);
      sessions.value = sessions.value.filter((s) => s.id !== sessionId);
      if (currentSession.value?.id === sessionId) {
        if (sessions.value.length > 0) {
          await selectSession(kbId, sessions.value[0].id);
        } else {
          currentSession.value = null;
        }
      }
    } catch (err: any) {
      errorMessage.value = err.detail || "Erro ao excluir sessão.";
      throw err;
    }
  }

  async function sendMessage(kbId: string, content: string) {
    if (!currentSession.value) {
      // Auto-create session if none selected
      await createSession(kbId);
    }

    if (!currentSession.value) return;

    const sessionId = currentSession.value.id;

    // Optimistic user message in UI
    const tempUserMessage: ChatMessage = {
      id: "temp-" + Date.now(),
      chat_session_id: sessionId,
      role: "user",
      content: content,
      citations: [],
      created_at: new Date().toISOString(),
    };
    currentSession.value.messages.push(tempUserMessage);

    isThinking.value = true;
    errorMessage.value = null;

    try {
      const assistantMessage = await chatService.sendMessage(kbId, sessionId, { content });
      // Append real assistant response
      currentSession.value.messages.push(assistantMessage);

      // Update session title in sidebar if it was updated by backend
      const foundSession = sessions.value.find((s) => s.id === sessionId);
      if (foundSession && foundSession.title === "Nova Conversa") {
        foundSession.title = content.slice(0, 35) + (content.length > 35 ? "..." : "");
      }
    } catch (err: any) {
      errorMessage.value = err.detail || "Erro ao obter resposta do assistente.";
      // Add error bubble
      currentSession.value.messages.push({
        id: "error-" + Date.now(),
        chat_session_id: sessionId,
        role: "assistant",
        content: `⚠️ Erro: ${err.detail || "Não foi possível processar sua pergunta. Tente novamente."}`,
        citations: [],
        created_at: new Date().toISOString(),
      });
    } finally {
      isThinking.value = false;
    }
  }

  return {
    sessions,
    currentSession,
    isThinking,
    isLoadingSessions,
    errorMessage,
    fetchSessions,
    selectSession,
    createSession,
    deleteSession,
    sendMessage,
  };
});
