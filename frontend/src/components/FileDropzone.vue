<script setup lang="ts">
import { ref } from "vue";
import { UploadCloud, FileText, AlertCircle, Loader2 } from "lucide-vue-next";

const props = defineProps<{
  isUploading: boolean;
}>();

const emit = defineEmits<{
  (e: "upload", file: File): void;
}>();

const isDragging = ref(false);
const localError = ref<string | null>(null);

const ALLOWED_EXTENSIONS = [".pdf", ".txt", ".md"];
const MAX_SIZE_MB = 10;
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

function validateAndEmit(file: File) {
  localError.value = null;

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
    <div
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
      :class="[
        'relative rounded-2xl border-2 border-dashed p-8 text-center transition-all cursor-pointer flex flex-col items-center justify-center',
        isDragging
          ? 'border-indigo-500 bg-indigo-50/50 scale-[1.01]'
          : 'border-slate-300 hover:border-indigo-400 hover:bg-slate-50/50 bg-white',
        isUploading ? 'opacity-60 pointer-events-none' : '',
      ]"
    >
      <input
        type="file"
        accept=".pdf,.txt,.md"
        @change="handleFileInput"
        class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        :disabled="isUploading"
      />

      <div class="w-12 h-12 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mb-3">
        <Loader2 v-if="isUploading" class="w-6 h-6 animate-spin" />
        <UploadCloud v-else class="w-6 h-6" />
      </div>

      <p class="text-sm font-semibold text-slate-800">
        <span v-if="isUploading">Processando documento e gerando embeddings...</span>
        <span v-else>Arraste seu documento aqui ou <span class="text-indigo-600 underline">procure no computador</span></span>
      </p>

      <p class="text-xs text-slate-400 mt-1">
        Suporta PDF, TXT ou Markdown (.md) até 10 MB
      </p>
    </div>

    <!-- Error Alert -->
    <div
      v-if="localError"
      class="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2"
    >
      <AlertCircle class="w-4 h-4 shrink-0 text-rose-500" />
      <span>{{ localError }}</span>
    </div>
  </div>
</template>
