<script setup lang="ts">
import { ref } from "vue";
import { Send, Loader2 } from "lucide-vue-next";

const props = defineProps<{
  isThinking: boolean;
}>();

const emit = defineEmits<{
  (e: "send", text: string): void;
}>();

const inputContent = ref("");

function handleKeydown(e: KeyboardEvent) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    handleSend();
  }
}

function handleSend() {
  const trimmed = inputContent.value.trim();
  if (!trimmed || props.isThinking) return;

  emit("send", trimmed);
  inputContent.value = "";
}
</script>

<template>
  <div class="p-4 bg-white border-t border-slate-200">
    <div class="max-w-4xl mx-auto relative flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-2xl p-1.5 focus-within:ring-2 focus-within:ring-indigo-500/20 focus-within:border-indigo-600 transition-all">
      <textarea
        v-model="inputContent"
        @keydown="handleKeydown"
        rows="1"
        :disabled="isThinking"
        placeholder="Faça uma pergunta sobre os documentos da base de conhecimento... (Pressione Enter para enviar)"
        class="flex-1 bg-transparent px-3 py-2 text-sm text-slate-800 placeholder-slate-400 focus:outline-hidden resize-none max-h-32 min-h-[40px]"
      ></textarea>

      <button
        @click="handleSend"
        :disabled="!inputContent.trim() || isThinking"
        type="button"
        class="w-10 h-10 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 text-white flex items-center justify-center shrink-0 transition-colors shadow-xs"
        title="Enviar mensagem"
      >
        <Loader2 v-if="isThinking" class="w-4 h-4 animate-spin" />
        <Send v-else class="w-4 h-4" />
      </button>
    </div>
  </div>
</template>
