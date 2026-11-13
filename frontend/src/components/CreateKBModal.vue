<script setup lang="ts">
import { ref, reactive } from "vue";
import { X, FolderPlus, Loader2 } from "lucide-vue-next";

const props = defineProps<{
  isOpen: boolean;
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (e: "created", payload: { name: string; description?: string }): void;
}>();

const form = reactive({
  name: "",
  description: "",
});

const isSubmitting = ref(false);
const errorMessage = ref<string | null>(null);

function closeModal() {
  form.name = "";
  form.description = "";
  errorMessage.value = null;
  emit("close");
}

async function handleSubmit() {
  if (!form.name.trim()) {
    errorMessage.value = "Por favor, informe um nome para a base de conhecimento.";
    return;
  }

  isSubmitting.value = true;
  errorMessage.value = null;

  try {
    emit("created", {
      name: form.name.trim(),
      description: form.description.trim() || undefined,
    });
    closeModal();
  } catch (err: any) {
    errorMessage.value = err.detail || "Erro ao criar a base.";
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 dark:bg-black/80 backdrop-blur-sm animate-in fade-in duration-200"
  >
    <div
      class="bg-white dark:bg-black rounded-2xl border border-slate-200 dark:border-zinc-850 shadow-2xl max-w-md w-full overflow-hidden scale-100 transition-transform"
    >
      <!-- Header -->
      <div class="px-6 py-4 border-b border-slate-100 dark:border-zinc-900 flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-lg bg-indigo-50 border border-indigo-100 text-indigo-600 dark:bg-zinc-900 dark:border-zinc-800 dark:text-indigo-400 flex items-center justify-center">
            <FolderPlus class="w-4 h-4" />
          </div>
          <h2 class="text-base font-semibold text-slate-900 dark:text-white">Nova Base de Conhecimento</h2>
        </div>
        <button
          @click="closeModal"
          class="p-1 text-slate-400 hover:text-slate-600 dark:text-zinc-400 dark:hover:text-white rounded-lg transition-colors cursor-pointer"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Body Form -->
      <form @submit.prevent="handleSubmit" class="p-6 space-y-4">
        <div v-if="errorMessage" class="p-3 rounded-lg bg-rose-50 border border-rose-100 text-rose-700 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-900/60 text-sm">
          {{ errorMessage }}
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-700 dark:text-zinc-300 uppercase tracking-wider mb-1.5">
            Nome da Base *
          </label>
          <input
            v-model="form.name"
            type="text"
            required
            maxlength="100"
            placeholder="Ex: Manuais de Engenharia, Políticas Internas"
            class="w-full px-3.5 py-2 rounded-xl border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-sm text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-zinc-600 focus:outline-hidden focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 dark:focus:border-indigo-400 transition-all"
            autofocus
          />
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-700 dark:text-zinc-300 uppercase tracking-wider mb-1.5">
            Descrição (Opcional)
          </label>
          <textarea
            v-model="form.description"
            rows="3"
            maxlength="500"
            placeholder="Descreva o escopo e objetivo desta coleção de documentos..."
            class="w-full px-3.5 py-2 rounded-xl border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-sm text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-zinc-600 focus:outline-hidden focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 dark:focus:border-indigo-400 transition-all resize-none"
          ></textarea>
        </div>

        <!-- Footer Buttons -->
        <div class="pt-2 flex items-center justify-end gap-2.5">
          <button
            type="button"
            @click="closeModal"
            class="px-4 py-2 rounded-xl border border-slate-200 dark:border-zinc-800 text-sm font-medium text-slate-600 dark:text-zinc-300 hover:bg-slate-50 dark:hover:bg-zinc-900 transition-colors cursor-pointer"
          >
            Cancelar
          </button>
          <button
            type="submit"
            :disabled="isSubmitting"
            class="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50 transition-colors shadow-xs cursor-pointer"
          >
            <Loader2 v-if="isSubmitting" class="w-4 h-4 animate-spin" />
            <span>Criar Base</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
