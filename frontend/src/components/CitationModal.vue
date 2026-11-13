<script setup lang="ts">
import { X, FileText, CheckCircle, Hash } from "lucide-vue-next";
import type { CitationItem } from "@/types";

defineProps<{
  citation: CitationItem | null;
}>();

const emit = defineEmits<{
  (e: "close"): void;
}>();
</script>

<template>
  <div
    v-if="citation"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 dark:bg-black/80 backdrop-blur-xs animate-in fade-in duration-150"
  >
    <div
      class="bg-white dark:bg-black rounded-2xl border border-slate-200 dark:border-zinc-850 shadow-2xl max-w-lg w-full overflow-hidden flex flex-col max-h-[85vh]"
    >
      <!-- Header -->
      <div class="px-6 py-4 border-b border-slate-100 dark:border-zinc-900 flex items-center justify-between bg-slate-50/50 dark:bg-zinc-950">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-lg bg-indigo-50 border border-indigo-100 text-indigo-600 dark:bg-zinc-900 dark:border-zinc-800 dark:text-indigo-400 flex items-center justify-center">
            <FileText class="w-4 h-4" />
          </div>
          <div>
            <h3 class="text-sm font-semibold text-slate-900 dark:text-white truncate max-w-xs">
              {{ citation.document_name }}
            </h3>
            <span class="text-xs text-slate-400 dark:text-zinc-500">Fonte Documental Auditada</span>
          </div>
        </div>

        <button
          @click="emit('close')"
          class="p-1 text-slate-400 hover:text-slate-600 dark:text-zinc-400 dark:hover:text-white rounded-lg transition-colors cursor-pointer"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Content -->
      <div class="p-6 overflow-y-auto space-y-4">
        <!-- Badges row -->
        <div class="flex items-center gap-2">
          <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800/60">
            <CheckCircle class="w-3.5 h-3.5 text-emerald-500 dark:text-emerald-400" />
            Similaridade: {{ (citation.similarity_score * 100).toFixed(1) }}%
          </span>

          <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-mono font-medium bg-slate-100 text-slate-700 dark:bg-zinc-900 dark:text-zinc-300 dark:border dark:border-zinc-800">
            <Hash class="w-3 h-3 text-slate-500 dark:text-zinc-400" />
            Chunk #{{ citation.chunk_index }}
          </span>
        </div>

        <!-- Text Slice -->
        <div>
          <label class="block text-xs font-semibold text-slate-500 dark:text-zinc-400 uppercase tracking-wider mb-2">
            Trecho Original Recuperado do pgvector:
          </label>
          <div class="p-4 rounded-xl bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-850 text-sm text-slate-700 dark:text-zinc-200 leading-relaxed font-sans whitespace-pre-wrap select-text">
            "{{ citation.content_snippet }}"
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="px-6 py-3 border-t border-slate-100 dark:border-zinc-900 bg-slate-50/50 dark:bg-zinc-950 flex justify-end">
        <button
          type="button"
          @click="emit('close')"
          class="px-4 py-1.5 rounded-xl bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 text-xs font-semibold text-slate-700 dark:text-zinc-200 hover:bg-slate-50 dark:hover:bg-zinc-850 transition-colors shadow-2xs cursor-pointer"
        >
          Fechar
        </button>
      </div>
    </div>
  </div>
</template>
