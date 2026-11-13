<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from "vue";
import { useRoute, RouterLink } from "vue-router";
import {
  ArrowLeft,
  Files,
  MessageSquare,
  Sparkles,
  Database,
  Info,
} from "lucide-vue-next";
import { useKnowledgeBaseStore } from "@/stores/knowledgeBaseStore";
import { useChatStore } from "@/stores/chatStore";
import FileDropzone from "@/components/FileDropzone.vue";
import DocumentTable from "@/components/DocumentTable.vue";
import ChatSidebar from "@/components/ChatSidebar.vue";
import MessageBubble from "@/components/MessageBubble.vue";
import ChatInputBar from "@/components/ChatInputBar.vue";
import CitationModal from "@/components/CitationModal.vue";
import type { CitationItem } from "@/types";

const route = useRoute();
const kbStore = useKnowledgeBaseStore();
const chatStore = useChatStore();

const kbId = computed(() => route.params.id as string);
const activeTab = ref<"documents" | "chat">("documents");
const selectedCitation = ref<CitationItem | null>(null);
const messageContainer = ref<HTMLDivElement | null>(null);

onMounted(async () => {
  if (kbId.value) {
    await kbStore.selectKnowledgeBase(kbId.value);
    await chatStore.fetchSessions(kbId.value);
  }
});

watch(
  () => chatStore.currentSession?.messages.length,
  async () => {
    await nextTick();
    scrollToBottom();
  }
);

function scrollToBottom() {
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight;
  }
}

async function handleUpload(file: File) {
  await kbStore.uploadDocument(kbId.value, file);
}

async function handleDeleteDocument(docId: string) {
  if (confirm("Deseja realmente excluir este documento e todos os seus chunks vetoriais?")) {
    await kbStore.deleteDocument(kbId.value, docId);
  }
}

async function handleSendMessage(content: string) {
  await chatStore.sendMessage(kbId.value, content);
}

async function handleSelectSession(sessionId: string) {
  await chatStore.selectSession(kbId.value, sessionId);
}

async function handleCreateSession() {
  await chatStore.createSession(kbId.value);
}

async function handleDeleteSession(sessionId: string) {
  await chatStore.deleteSession(kbId.value, sessionId);
}
</script>

<template>
  <div class="flex-1 flex flex-col h-[calc(100vh-64px)] overflow-hidden">
    <!-- Subheader: Navigation & Title -->
    <div class="bg-white border-b border-slate-200 px-4 sm:px-6 py-3.5 flex flex-wrap items-center justify-between gap-4 shrink-0">
      <div class="flex items-center gap-3">
        <RouterLink
          to="/"
          class="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
          title="Voltar para as bases"
        >
          <ArrowLeft class="w-5 h-5" />
        </RouterLink>

        <div>
          <h1 class="text-base font-bold text-slate-900 flex items-center gap-2">
            <span>{{ kbStore.currentKnowledgeBase?.name || "Carregando Base..." }}</span>
          </h1>
          <p class="text-xs text-slate-400 line-clamp-1">
            {{ kbStore.currentKnowledgeBase?.description || "Base de conhecimento sem descrição." }}
          </p>
        </div>
      </div>

      <!-- Tab Switcher -->
      <div class="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200">
        <button
          @click="activeTab = 'documents'"
          :class="[
            'flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all',
            activeTab === 'documents'
              ? 'bg-white text-indigo-600 shadow-2xs'
              : 'text-slate-600 hover:text-slate-900',
          ]"
        >
          <Files class="w-4 h-4" />
          <span>Documentos ({{ kbStore.documents.length }})</span>
        </button>

        <button
          @click="activeTab = 'chat'"
          :class="[
            'flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all',
            activeTab === 'chat'
              ? 'bg-white text-indigo-600 shadow-2xs'
              : 'text-slate-600 hover:text-slate-900',
          ]"
        >
          <MessageSquare class="w-4 h-4" />
          <span>Chat Inteligente</span>
        </button>
      </div>
    </div>

    <!-- Tab 1: Documents & Ingestion View -->
    <div
      v-if="activeTab === 'documents'"
      class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 max-w-6xl mx-auto w-full space-y-6"
    >
      <!-- Upload Dropzone -->
      <div>
        <h2 class="text-sm font-semibold text-slate-800 mb-2">Enviar Documentos</h2>
        <FileDropzone
          :is-uploading="kbStore.isUploading"
          @upload="handleUpload"
        />
      </div>

      <!-- Document Table -->
      <div>
        <h2 class="text-sm font-semibold text-slate-800 mb-2">Documentos Ingeridos</h2>
        <DocumentTable
          :documents="kbStore.documents"
          @delete="handleDeleteDocument"
        />
      </div>
    </div>

    <!-- Tab 2: Conversational RAG Chat View -->
    <div v-else class="flex-1 flex overflow-hidden">
      <!-- Sessions Sidebar -->
      <ChatSidebar
        :sessions="chatStore.sessions"
        :active-session-id="chatStore.currentSession?.id || null"
        :is-loading="chatStore.isLoadingSessions"
        @select="handleSelectSession"
        @create="handleCreateSession"
        @delete="handleDeleteSession"
      />

      <!-- Chat Dialogue Area -->
      <div class="flex-1 flex flex-col bg-slate-50/50 h-full overflow-hidden">
        <!-- Messages Stream -->
        <div
          ref="messageContainer"
          class="flex-1 overflow-y-auto p-4 sm:p-6 flex flex-col"
        >
          <!-- Empty State: No messages yet -->
          <div
            v-if="!chatStore.currentSession?.messages || chatStore.currentSession.messages.length === 0"
            class="m-auto text-center max-w-md p-8"
          >
            <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-500 to-violet-600 text-white flex items-center justify-center mx-auto mb-4 shadow-md shadow-indigo-500/20">
              <Sparkles class="w-7 h-7" />
            </div>
            <h3 class="text-base font-bold text-slate-900 mb-1">
              Como posso ajudar com esta base de conhecimento?
            </h3>
            <p class="text-xs text-slate-500 mb-4 leading-relaxed">
              Faça perguntas sobre o conteúdo dos documentos que você enviou. Respostas serão sintetizadas pelo Gemini e fundamentadas com citações das fontes.
            </p>

            <div v-if="kbStore.documents.length === 0" class="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-800 flex items-center gap-2">
              <Info class="w-4 h-4 shrink-0 text-amber-600" />
              <span>Aviso: Nenhum documento ingerido nesta base. Envie arquivos na aba "Documentos" primeiro!</span>
            </div>
          </div>

          <!-- Message Bubbles -->
          <div v-else class="space-y-2">
            <MessageBubble
              v-for="msg in chatStore.currentSession.messages"
              :key="msg.id"
              :message="msg"
              @open-citation="selectedCitation = $event"
            />

            <!-- Thinking Pulse -->
            <div
              v-if="chatStore.isThinking"
              class="flex items-center gap-3 my-4 mr-auto max-w-md animate-in fade-in"
            >
              <div class="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-600 text-white flex items-center justify-center shrink-0 shadow-xs">
                <Sparkles class="w-4 h-4 animate-spin" />
              </div>
              <div class="bg-white border border-slate-200/90 rounded-2xl px-4 py-3 text-xs text-slate-500 flex items-center gap-2 shadow-xs">
                <span class="flex gap-1">
                  <span class="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-bounce"></span>
                  <span class="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-bounce [animation-delay:0.2s]"></span>
                  <span class="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-bounce [animation-delay:0.4s]"></span>
                </span>
                <span>Buscando no pgvector e sintetizando resposta...</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Chat Input Bar -->
        <ChatInputBar
          :is-thinking="chatStore.isThinking"
          @send="handleSendMessage"
        />
      </div>
    </div>

    <!-- Citation Modal/Drawer -->
    <CitationModal
      :citation="selectedCitation"
      @close="selectedCitation = null"
    />
  </div>
</template>
