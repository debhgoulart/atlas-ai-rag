<script setup lang="ts">
import { computed } from "vue";
import { marked } from "marked";
import { Sparkles, User, FileText, Zap, Clock } from "lucide-vue-next";
import type { ChatMessage, CitationItem } from "@/types";

const props = defineProps<{
  message: ChatMessage;
}>();

const emit = defineEmits<{
  (e: "open-citation", citation: CitationItem): void;
}>();

const renderedContent = computed(() => {
  try {
    return marked.parse(props.message.content);
  } catch {
    return props.message.content;
  }
});

function formatSimilarity(score: number): string {
  return `${Math.round(score * 100)}% similaridade`;
}
</script>

<template>
  <div
    :class="[
      'flex gap-3 max-w-4xl w-full my-4',
      message.role === 'user' ? 'ml-auto justify-end' : 'mr-auto justify-start',
    ]"
  >
    <!-- Assistant Avatar -->
    <div
      v-if="message.role === 'assistant'"
      class="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-600 text-white flex items-center justify-center shrink-0 shadow-xs"
    >
      <Sparkles class="w-4 h-4" />
    </div>

    <!-- Bubble Body -->
    <div
      :class="[
        'rounded-2xl px-5 py-4 transition-all max-w-[85%] sm:max-w-[75%]',
        message.role === 'user'
          ? 'bg-indigo-600 text-white rounded-tr-xs shadow-xs'
          : 'bg-white border border-slate-200/90 text-slate-800 rounded-tl-xs shadow-xs',
      ]"
    >
      <!-- Message Content -->
      <div
        v-if="message.role === 'assistant'"
        class="prose prose-slate prose-sm max-w-none leading-relaxed prose-pre:bg-slate-900 prose-pre:text-slate-100"
        v-html="renderedContent"
      ></div>
      <div v-else class="text-sm leading-relaxed whitespace-pre-wrap">
        {{ message.content }}
      </div>

      <!-- Sources & Citations Section (Assistant only) -->
      <div
        v-if="message.role === 'assistant' && message.citations && message.citations.length > 0"
        class="mt-4 pt-3 border-t border-slate-100"
      >
        <span class="text-xs font-semibold text-slate-400 block mb-2 uppercase tracking-wider">
          Fontes Citadas:
        </span>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="(cit, idx) in message.citations"
            :key="idx"
            @click="emit('open-citation', cit)"
            type="button"
            class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-50 hover:bg-indigo-50 border border-slate-200 hover:border-indigo-200 text-slate-700 hover:text-indigo-700 transition-colors cursor-pointer group"
          >
            <FileText class="w-3.5 h-3.5 text-indigo-500" />
            <span class="max-w-[160px] truncate">[{{ idx + 1 }}] {{ cit.document_name }}</span>
            <span class="text-[10px] text-indigo-600/70 font-mono">({{ formatSimilarity(cit.similarity_score) }})</span>
          </button>
        </div>
      </div>

      <!-- Observability Meta footer (Assistant only) -->
      <div
        v-if="message.role === 'assistant' && (message.latency_ms || message.prompt_tokens)"
        class="mt-3 flex items-center gap-3 text-[11px] text-slate-400 font-mono"
      >
        <span v-if="message.latency_ms" class="inline-flex items-center gap-1">
          <Clock class="w-3 h-3 text-slate-400" />
          {{ (message.latency_ms / 1000).toFixed(2) }}s
        </span>
        <span v-if="message.prompt_tokens || message.completion_tokens" class="inline-flex items-center gap-1">
          <Zap class="w-3 h-3 text-amber-500" />
          {{ (message.prompt_tokens || 0) + (message.completion_tokens || 0) }} tokens
        </span>
      </div>
    </div>

    <!-- User Avatar -->
    <div
      v-if="message.role === 'user'"
      class="w-8 h-8 rounded-xl bg-slate-200 text-slate-600 flex items-center justify-center shrink-0 shadow-xs"
    >
      <User class="w-4 h-4" />
    </div>
  </div>
</template>
