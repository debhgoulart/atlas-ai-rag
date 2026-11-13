<script setup lang="ts">
import { ref } from "vue";
import { UploadCloud, AlertCircle, Loader2, KeyRound } from "lucide-vue-next";
import { useGeminiCredentialStore } from "@/stores/geminiCredentialStore";

const props = defineProps<{
  isUploading: boolean;
}>();

const emit = defineEmits<{
  (e: "upload", file: File): void;
}>();

const credentialStore = useGeminiCredentialStore();

const isDragging = ref(false);
const localError = ref<string | null>(null);

const ALLOWED_EXTENSIONS = [".pdf", ".txt", ".md"];
const MAX_SIZE_MB = 10;
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

function validateAndEmit(file: File) {
  localError.value = null;

  if (!credentialStore.isValid) {
    localError.value = "Você precisa cadastrar uma Gemini API Key válida para processar e gerar embeddings dos documentos.";
    return;
  }

  // Validate format
  const fileName = file.name.toLowerCase();
  const hasValidExt = ALLOWED_EXTENSIONS.some((ext) => fileName.endsWith(ext));
  if (!hasValidExt) {
    localError.value = `Formato não suportado. Por favor, envie arquivos PDF, TXT ou Markdown (.md).`;
    return;
  }

  // Validate size
  if (file.size > MAX_SIZE_BYTES) {
    localError.value = `O arquivo excede o limite máximo permitido de ${MAX_SIZE_MB} MB.`;
    return;
  }

  if (file.size <= 0) {
    localError.value = "O arquivo selecionado está vazio.";
    return;
  }

  emit("upload", file);
}

function handleDrop(e: DragEvent) {
  isDragging.value = false;
  if (props.isUploading) return;
  const files = e.dataTransfer?.files;
  if (files && files.length > 0) {
    validateAndEmit(files[0]);
  }
}

function handleFileInput(e: Event) {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    validateAndEmit(target.files[0]);
    target.value = ""; // Reset input
  }
}
</script>

<template>
  <div class="space-y-3">
    <!-- Unconfigured Warning Banner -->
    <div
      v-if="!credentialStore.isValid"
      class="flex items-center justify-between px-4 py-2.5 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 rounded-xl text-xs text-amber-800 dark:text-amber-300"
    >
      <div class="flex items-center gap-2">
        <KeyRound class="w-4 h-4 shrink-0" />
        <span>
          {{ credentialStore.isInvalid ? "Sua Gemini API Key expirou ou é inválida. Cadastre uma nova chave para vetorizar documentos." : "Cadastre sua Gemini API Key pessoal para habilitar o upload e vetorização de documentos." }}
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

    <div
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
      :class="[
        'relative rounded-2xl border-2 border-dashed p-8 text-center transition-all flex flex-col items-center justify-center',
        !credentialStore.isValid
          ? 'border-slate-200 dark:border-zinc-800 bg-slate-50/50 dark:bg-zinc-950/30 opacity-70 cursor-not-allowed'
          : isDragging
          ? 'border-indigo-500 bg-indigo-50/50 dark:bg-indigo-950/30 scale-[1.01] cursor-pointer'
          : 'border-slate-300 hover:border-indigo-400 hover:bg-slate-50/50 dark:border-zinc-850 dark:hover:border-zinc-700 dark:hover:bg-zinc-950/60 bg-white dark:bg-black cursor-pointer',
        isUploading ? 'opacity-60 pointer-events-none' : '',
      ]"
    >
      <input
        type="file"
        accept=".pdf,.txt,.md"
        @change="handleFileInput"
        class="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
        :disabled="isUploading || !credentialStore.isValid"
      />

      <div class="w-12 h-12 rounded-2xl bg-indigo-50 text-indigo-600 dark:bg-zinc-900 dark:text-indigo-400 dark:border dark:border-zinc-800 flex items-center justify-center mb-3">
        <Loader2 v-if="isUploading" class="w-6 h-6 animate-spin" />
        <UploadCloud v-else class="w-6 h-6" />
      </div>

      <p class="text-sm font-semibold text-slate-800 dark:text-zinc-200">
        <span v-if="isUploading">Processando documento e gerando embeddings...</span>
        <span v-else-if="!credentialStore.isValid">Upload bloqueado até a configuração da Gemini API Key</span>
        <span v-else>Arraste seu documento aqui ou <span class="text-indigo-600 dark:text-indigo-400 underline">procure no computador</span></span>
      </p>

      <p class="text-xs text-slate-400 dark:text-zinc-500 mt-1">
        Suporta PDF, TXT ou Markdown (.md) até 10 MB
      </p>
    </div>

    <!-- Error Alert -->
    <div
      v-if="localError"
      class="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 dark:bg-rose-950/40 dark:border-rose-900/60 dark:text-rose-300 text-xs flex items-center gap-2"
    >
      <AlertCircle class="w-4 h-4 shrink-0 text-rose-500 dark:text-rose-400" />
      <span>{{ localError }}</span>
    </div>
  </div>
</template>
