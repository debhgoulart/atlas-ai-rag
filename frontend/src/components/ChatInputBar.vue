<script setup lang="ts">
import { ref } from "vue";
import { Send, Loader2, KeyRound } from "lucide-vue-next";
import { useGeminiCredentialStore } from "@/stores/geminiCredentialStore";

const props = defineProps<{
  isThinking: boolean;
}>();

const emit = defineEmits<{
  (e: "send", text: string): void;
}>();

const credentialStore = useGeminiCredentialStore();
const inputContent = ref("");

function handleKeydown(e: KeyboardEvent) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    handleSend();
  }
}

function handleSend() {
  const trimmed = inputContent.value.trim();
  if (!trimmed || props.isThinking || !credentialStore.isValid) return;

  emit("send", trimmed);
  inputContent.value = "";
}
</script>

<template>
  <div class="p-4 bg-white dark:bg-black border-t border-slate-200 dark:border-zinc-850 transition-colors">
    <div class="max-w-4xl mx-auto space-y-2">
      <!-- Unconfigured Key Warning Banner -->
      <div
        v-if="!credentialStore.isValid"
        class="flex items-center justify-between px-4 py-2.5 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 rounded-xl text-xs text-amber-800 dark:text-amber-300"
      >
        <div class="flex items-center gap-2">
          <KeyRound class="w-4 h-4 shrink-0" />
          <span>
            {{ credentialStore.isInvalid ? "Sua Gemini API Key é inválida ou expirou. Cadastre uma nova chave para conversar." : "Você precisa cadastrar sua Gemini API Key pessoal para enviar perguntas." }}
          </span>
        </div>
        <button
          @click="credentialStore.openModal()"
          type="button"
          class="px-2.5 py-1 font-semibold bg-amber-600 hover:bg-amber-700 text-white rounded-lg transition-colors cursor-pointer shrink-0 ml-3"
        >
          Configurar Chave
        </button>
      </div>

      <div class="relative flex items-center gap-2 bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-850 rounded-2xl p-1.5 focus-within:ring-2 focus-within:ring-indigo-500/20 focus-within:border-indigo-600 dark:focus-within:border-indigo-400 transition-all">
        <textarea
          v-model="inputContent"
          @keydown="handleKeydown"
          rows="1"
          :disabled="isThinking || !credentialStore.isValid"
          :placeholder="credentialStore.isValid ? 'Faça uma pergunta sobre os documentos da base de conhecimento... (Pressione Enter para enviar)' : 'Configure sua Gemini API Key acima para habilitar o envio de perguntas...'"
          class="flex-1 bg-transparent px-3 py-2 text-sm text-slate-800 dark:text-white placeholder-slate-400 dark:placeholder-zinc-600 focus:outline-hidden resize-none max-h-32 min-h-[40px] disabled:opacity-50"
        ></textarea>

        <button
          @click="handleSend"
          :disabled="!inputContent.trim() || isThinking || !credentialStore.isValid"
          type="button"
          class="w-10 h-10 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-30 text-white flex items-center justify-center shrink-0 transition-colors shadow-xs cursor-pointer"
          title="Enviar mensagem"
        >
          <Loader2 v-if="isThinking" class="w-4 h-4 animate-spin" />
          <Send v-else class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>
