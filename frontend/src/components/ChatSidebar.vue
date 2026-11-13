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
  <aside class="w-64 sm:w-72 border-r border-slate-200 dark:border-zinc-850 bg-slate-50/70 dark:bg-black flex flex-col h-full shrink-0 transition-colors">
    <!-- Top Action -->
    <div class="p-4 border-b border-slate-200/80 dark:border-zinc-850">
      <button
        @click="emit('create')"
        type="button"
        class="w-full inline-flex items-center justify-center gap-2 px-3.5 py-2 rounded-xl bg-white dark:bg-zinc-900 hover:bg-slate-50 dark:hover:bg-zinc-850 border border-slate-200 dark:border-zinc-800 text-sm font-semibold text-slate-800 dark:text-white shadow-2xs hover:border-slate-300 dark:hover:border-zinc-700 transition-all cursor-pointer"
      >
        <Plus class="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
        <span>Nova Conversa</span>
      </button>
    </div>

    <!-- Sessions List -->
    <div class="flex-1 overflow-y-auto p-2 space-y-1">
      <div v-if="isLoading" class="p-4 text-xs text-slate-400 dark:text-zinc-500 text-center">
        Carregando conversas...
      </div>

      <div v-else-if="sessions.length === 0" class="p-6 text-center text-xs text-slate-400 dark:text-zinc-500">
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
            ? 'bg-white dark:bg-zinc-900 border-indigo-200 dark:border-zinc-800 text-indigo-900 dark:text-indigo-300 shadow-2xs font-medium'
            : 'border-transparent hover:bg-slate-100/70 dark:hover:bg-zinc-950 text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white',
        ]"
      >
        <div class="flex items-center gap-2.5 truncate flex-1 mr-2">
          <MessageSquare
            :class="[
              'w-4 h-4 shrink-0',
              activeSessionId === session.id ? 'text-indigo-600 dark:text-indigo-400' : 'text-slate-400 dark:text-zinc-500',
            ]"
          />
          <span class="truncate">{{ session.title || "Conversa sem título" }}</span>
        </div>

        <button
          @click="(e) => handleDelete(e, session.id)"
          type="button"
          class="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-rose-600 dark:text-zinc-500 dark:hover:text-rose-400 rounded-md transition-opacity cursor-pointer"
          title="Excluir conversa"
        >
          <Trash2 class="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  </aside>
</template>
