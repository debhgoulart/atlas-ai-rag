<script setup lang="ts">
import { ref } from "vue";
import { Folder, Files, MessageSquare, Trash2, ArrowRight } from "lucide-vue-next";
import { RouterLink } from "vue-router";
import type { KnowledgeBase } from "@/types";

const props = defineProps<{
  kb: KnowledgeBase;
}>();

const emit = defineEmits<{
  (e: "delete", id: string): void;
}>();

const isDeleting = ref(false);

function handleDelete(e: Event) {
  e.preventDefault();
  e.stopPropagation();
  if (confirm(`Tem certeza que deseja excluir a base "${props.kb.name}"? Todos os documentos e chats serão apagados permanentemente.`)) {
    isDeleting.value = true;
    emit("delete", props.kb.id);
  }
}
</script>

<template>
  <div
    class="group relative bg-white rounded-2xl border border-slate-200/80 p-5 shadow-xs hover:shadow-md hover:border-indigo-300 transition-all duration-200 flex flex-col justify-between"
  >
    <div>
      <!-- Header row: Icon, Badge and Actions -->
      <div class="flex items-start justify-between gap-3 mb-3">
        <div class="w-10 h-10 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600 group-hover:scale-105 transition-transform">
          <Folder class="w-5 h-5" />
        </div>

        <div class="flex items-center gap-1.5">
          <span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700">
            <Files class="w-3 h-3 text-slate-500" />
            {{ kb.document_count }} {{ kb.document_count === 1 ? 'doc' : 'docs' }}
          </span>

          <button
            @click="handleDelete"
            class="p-1 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
            title="Excluir base de conhecimento"
          >
            <Trash2 class="w-4 h-4" />
          </button>
        </div>
      </div>

      <!-- Title & Description -->
      <h3 class="text-base font-semibold text-slate-900 group-hover:text-indigo-600 transition-colors mb-1.5 line-clamp-1">
        {{ kb.name }}
      </h3>
      <p class="text-sm text-slate-500 line-clamp-2 leading-relaxed mb-4">
        {{ kb.description || "Nenhuma descrição fornecida." }}
      </p>
    </div>

    <!-- Actions Footer -->
    <div class="pt-3 border-t border-slate-100 flex items-center justify-between">
      <span class="text-xs text-slate-400">
        Criado em {{ new Date(kb.created_at).toLocaleDateString('pt-BR') }}
      </span>

      <RouterLink
        :to="`/knowledge-bases/${kb.id}`"
        class="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-600 hover:text-indigo-700 group-hover:translate-x-0.5 transition-transform"
      >
        <span>Acessar</span>
        <ArrowRight class="w-3.5 h-3.5" />
      </RouterLink>
    </div>
  </div>
</template>
