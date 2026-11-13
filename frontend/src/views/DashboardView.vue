<script setup lang="ts">
import { ref, onMounted } from "vue";
import { Plus, Database, Sparkles, AlertCircle } from "lucide-vue-next";
import { useKnowledgeBaseStore } from "@/stores/knowledgeBaseStore";
import KnowledgeBaseCard from "@/components/KnowledgeBaseCard.vue";
import CreateKBModal from "@/components/CreateKBModal.vue";

const kbStore = useKnowledgeBaseStore();
const isModalOpen = ref(false);

onMounted(() => {
  kbStore.fetchKnowledgeBases();
});

async function handleCreate(payload: { name: string; description?: string }) {
  await kbStore.createKnowledgeBase(payload);
}

async function handleDelete(id: string) {
  await kbStore.deleteKnowledgeBase(id);
}
</script>

<template>
  <div class="max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header Section -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 tracking-tight">Bases de Conhecimento</h1>
        <p class="text-sm text-slate-500 mt-1">
          Crie e organize seus domínios temáticos de documentos para consulta contextual via RAG.
        </p>
      </div>

      <button
        @click="isModalOpen = true"
        class="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium shadow-sm hover:shadow transition-all self-start sm:self-auto"
      >
        <Plus class="w-4 h-4" />
        <span>Nova Base</span>
      </button>
    </div>

    <!-- Error Banner -->
    <div
      v-if="kbStore.errorMessage"
      class="mb-6 p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-sm flex items-center gap-3"
    >
      <AlertCircle class="w-5 h-5 shrink-0 text-rose-500" />
      <span>{{ kbStore.errorMessage }}</span>
    </div>

    <!-- Loading State -->
    <div v-if="kbStore.isLoading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="i in 3"
        :key="i"
        class="bg-white rounded-2xl border border-slate-200/80 p-5 h-44 animate-pulse flex flex-col justify-between"
      >
        <div class="space-y-3">
          <div class="w-10 h-10 rounded-xl bg-slate-100"></div>
          <div class="h-4 bg-slate-100 rounded-md w-3/4"></div>
          <div class="h-3 bg-slate-100 rounded-md w-1/2"></div>
        </div>
        <div class="h-3 bg-slate-100 rounded-md w-1/3"></div>
      </div>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="kbStore.knowledgeBases.length === 0"
      class="bg-white rounded-3xl border border-slate-200 p-12 text-center max-w-lg mx-auto my-12 shadow-xs"
    >
      <div class="w-16 h-16 rounded-2xl bg-indigo-50 border border-indigo-100 text-indigo-600 flex items-center justify-center mx-auto mb-4">
        <Database class="w-8 h-8" />
      </div>
      <h3 class="text-lg font-bold text-slate-900 mb-1">Nenhuma base encontrada</h3>
      <p class="text-sm text-slate-500 mb-6 leading-relaxed">
        Você ainda não criou nenhuma base de conhecimento. Comece criando uma para enviar documentos e conversar com o chatbot.
      </p>
      <button
        @click="isModalOpen = true"
        class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium shadow-xs transition-colors"
      >
        <Plus class="w-4 h-4" />
        <span>Criar Primeira Base</span>
      </button>
    </div>

    <!-- Cards Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <KnowledgeBaseCard
        v-for="kb in kbStore.knowledgeBases"
        :key="kb.id"
        :kb="kb"
        @delete="handleDelete"
      />
    </div>

    <!-- Create Modal -->
    <CreateKBModal
      :is-open="isModalOpen"
      @close="isModalOpen = false"
      @created="handleCreate"
    />
  </div>
</template>
