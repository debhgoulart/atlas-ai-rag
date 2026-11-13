<script setup lang="ts">
import { Plus, MessageSquare, Trash2 } from "lucide-vue-next";
import type { ChatSession } from "@/types";

defineProps<{
  sessions: ChatSession[];
  activeSessionId: string | null;
  isLoading: boolean;
}>();

const emit = defineEmits<{
  (e: "select", id: string): void;
  (e: "create"): void;
  (e: "delete", id: string): void;
}>();

function handleDelete(e: Event, id: string) {
  e.stopPropagation();
  if (confirm("Deseja realmente apagar esta sessão de conversa?")) {
    emit("delete", id);
  }
}
</script>

<template>
  <aside class="w-64 sm:w-72 border-r border-slate-200 bg-slate-50/60 flex flex-col h-full shrink-0">
    <!-- Top Action -->
    <div class="p-4 border-b border-slate-200/80">
      <button
        @click="emit('create')"
        type="button"
        class="w-full inline-flex items-center justify-center gap-2 px-3.5 py-2 rounded-xl bg-white hover:bg-slate-50 border border-slate-200 text-sm font-semibold text-slate-800 shadow-2xs hover:border-slate-300 transition-all"
      >
        <Plus class="w-4 h-4 text-indigo-600" />
        <span>Nova Conversa</span>
      </button>
    </div>

    <!-- Sessions List -->
    <div class="flex-1 overflow-y-auto p-2 space-y-1">
      <div v-if="isLoading" class="p-4 text-xs text-slate-400 text-center">
        Carregando conversas...
      </div>

      <div v-else-if="sessions.length === 0" class="p-6 text-center text-xs text-slate-400">
        Nenhuma conversa criada nesta base ainda.
      </div>

      <div
        v-else
        v-for="session in sessions"
        :key="session.id"
        @click="emit('select', session.id)"
        :class="[
          'group flex items-center justify-between p-2.5 rounded-xl cursor-pointer text-sm transition-all border',
          activeSessionId === session.id
            ? 'bg-white border-indigo-200 text-indigo-900 shadow-2xs font-medium'
            : 'border-transparent hover:bg-slate-100/70 text-slate-600 hover:text-slate-900',
        ]"
      >
        <div class="flex items-center gap-2.5 truncate flex-1 mr-2">
          <MessageSquare
            :class="[
              'w-4 h-4 shrink-0',
              activeSessionId === session.id ? 'text-indigo-600' : 'text-slate-400',
            ]"
          />
          <span class="truncate">{{ session.title || "Conversa sem título" }}</span>
        </div>

        <button
          @click="(e) => handleDelete(e, session.id)"
          type="button"
          class="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-rose-600 rounded-md transition-opacity"
          title="Excluir conversa"
        >
          <Trash2 class="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  </aside>
</template>
