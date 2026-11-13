<script setup lang="ts">
import { ref } from "vue";
import {
  X,
  KeyRound,
  Eye,
  EyeOff,
  CheckCircle2,
  AlertCircle,
  AlertTriangle,
  Trash2,
  Loader2,
  ShieldCheck,
} from "lucide-vue-next";
import { useGeminiCredentialStore } from "@/stores/geminiCredentialStore";
import { useAuthStore } from "@/stores/authStore";

const credentialStore = useGeminiCredentialStore();
const authStore = useAuthStore();

const apiKeyInput = ref("");
const showKey = ref(false);
const errorMessage = ref("");
const successMessage = ref("");
const showDeleteConfirm = ref(false);

function toggleVisibility() {
  showKey.value = !showKey.value;
}

async function handleSaveKey() {
  errorMessage.value = "";
  successMessage.value = "";

  if (!apiKeyInput.value || apiKeyInput.value.trim().length < 15) {
    errorMessage.value = "Por favor, insira uma Gemini API Key válida.";
    return;
  }

  try {
    await credentialStore.saveKey(apiKeyInput.value.trim());
    successMessage.value = "Chave validada junto ao Google e salva com sucesso!";
    apiKeyInput.value = "";
    showKey.value = false;
  } catch (err: any) {
    errorMessage.value = err?.detail || "Chave inválida ou recusada pela API do Google Gemini.";
  }
}

async function handleRemoveKey() {
  errorMessage.value = "";
  successMessage.value = "";
  try {
    await credentialStore.removeKey();
    showDeleteConfirm.value = false;
    successMessage.value = "Chave removida com sucesso. O status foi redefinido para não configurado.";
  } catch (err: any) {
    errorMessage.value = err?.detail || "Falha ao remover a chave.";
  }
}
</script>

<template>
  <div
    v-if="credentialStore.isModalOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs transition-opacity"
  >
    <div
      class="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150"
    >
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100 dark:border-zinc-800">
        <div class="flex items-center gap-2.5">
          <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-amber-500 to-orange-500 flex items-center justify-center text-white shadow-xs">
            <KeyRound class="w-4 h-4" />
          </div>
          <div>
            <h2 class="text-base font-semibold text-slate-900 dark:text-white">
              Gemini API Key Pessoal
            </h2>
            <p class="text-xs text-slate-500 dark:text-zinc-400">
              Gerenciamento individual, seguro e criptografado
            </p>
          </div>
        </div>
        <button
          @click="credentialStore.closeModal()"
          type="button"
          class="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-zinc-200 rounded-lg hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors"
        >
          <X class="w-4 h-4" />
        </button>
      </div>

      <!-- Body -->
      <div class="p-6 space-y-5">
        <!-- Security Banner -->
        <div class="flex items-start gap-3 p-3.5 bg-slate-50 dark:bg-zinc-950/70 border border-slate-200 dark:border-zinc-800 rounded-xl text-xs text-slate-600 dark:text-zinc-300">
          <ShieldCheck class="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
          <div class="space-y-1">
            <span class="font-medium text-slate-800 dark:text-zinc-200">Segurança de Nível de Produção:</span>
            <p class="leading-relaxed text-slate-500 dark:text-zinc-400">
              Sua chave é validada diretamente com o Google, criptografada simetricamente no banco com chave mestra isolada e jamais trafega em logs ou texto puro.
            </p>
          </div>
        </div>

        <!-- Status Card -->
        <div class="p-4 rounded-xl border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 flex items-center justify-between">
          <div>
            <span class="text-xs font-medium text-slate-400 dark:text-zinc-500 uppercase tracking-wider block mb-1">
              Status Atual
            </span>
            <div class="flex items-center gap-2">
              <span
                v-if="credentialStore.isValid"
                class="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/60"
              >
                <CheckCircle2 class="w-3.5 h-3.5" />
                Configurada e Válida ({{ credentialStore.keyHint }})
              </span>
              <span
                v-else-if="credentialStore.isInvalid"
                class="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-full bg-rose-50 text-rose-700 dark:bg-rose-950/60 dark:text-rose-400 border border-rose-200 dark:border-rose-800/60"
              >
                <AlertCircle class="w-3.5 h-3.5" />
                Chave Inválida / Desativada
              </span>
              <span
                v-else
                class="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-full bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-400 border border-amber-200 dark:border-amber-800/60"
              >
                <AlertTriangle class="w-3.5 h-3.5" />
                Não Configurada
              </span>
            </div>
          </div>

          <button
            v-if="credentialStore.isValid && !showDeleteConfirm"
            @click="showDeleteConfirm = true"
            type="button"
            class="text-xs text-rose-600 hover:text-rose-700 dark:text-rose-400 dark:hover:text-rose-300 font-medium flex items-center gap-1 hover:underline cursor-pointer"
          >
            <Trash2 class="w-3.5 h-3.5" />
            Remover
          </button>
        </div>

        <!-- Deletion Confirmation Dialog -->
        <div v-if="showDeleteConfirm" class="p-3.5 bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900/60 rounded-xl space-y-2">
          <p class="text-xs text-rose-800 dark:text-rose-300 font-medium">
            Tem certeza de que deseja remover sua Gemini API Key?
          </p>
          <p class="text-[11px] text-rose-700/80 dark:text-rose-400">
            Você não poderá realizar uploads ou conversar no chat até cadastrar uma nova chave.
          </p>
          <div class="flex items-center gap-2 pt-1">
            <button
              @click="handleRemoveKey"
              :disabled="credentialStore.isLoading"
              type="button"
              class="px-3 py-1.5 text-xs font-semibold bg-rose-600 hover:bg-rose-700 text-white rounded-lg transition-colors cursor-pointer"
            >
              Sim, remover chave
            </button>
            <button
              @click="showDeleteConfirm = false"
              type="button"
              class="px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-800 dark:text-zinc-400 dark:hover:text-white rounded-lg hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors cursor-pointer"
            >
              Cancelar
            </button>
          </div>
        </div>

        <!-- Feedback Alerts -->
        <div v-if="errorMessage" class="flex items-center gap-2 p-3 text-xs text-rose-700 bg-rose-50 border border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-900/60 rounded-xl">
          <AlertCircle class="w-4 h-4 shrink-0" />
          <span>{{ errorMessage }}</span>
        </div>

        <div v-if="successMessage" class="flex items-center gap-2 p-3 text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-900/60 rounded-xl">
          <CheckCircle2 class="w-4 h-4 shrink-0" />
          <span>{{ successMessage }}</span>
        </div>

        <!-- Key Input Form -->
        <form @submit.prevent="handleSaveKey" class="space-y-3">
          <div>
            <label class="block text-xs font-medium text-slate-700 dark:text-zinc-300 mb-1.5">
              {{ credentialStore.isValid ? "Substituir por uma nova Gemini API Key" : "Informe sua Gemini API Key" }}
            </label>
            <div class="relative">
              <input
                v-model="apiKeyInput"
                :type="showKey ? 'text' : 'password'"
                placeholder="AIzaSy..."
                autocomplete="off"
                required
                class="w-full pl-3.5 pr-10 py-2.5 text-sm font-mono bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500 text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-zinc-600"
              />
              <button
                @click="toggleVisibility"
                type="button"
                class="absolute right-2.5 top-1/2 -translate-y-1/2 p-1 text-slate-400 hover:text-slate-600 dark:hover:text-zinc-200 transition-colors cursor-pointer"
                :title="showKey ? 'Ocultar chave' : 'Mostrar chave'"
              >
                <EyeOff v-if="showKey" class="w-4 h-4" />
                <Eye v-else class="w-4 h-4" />
              </button>
            </div>
            <p class="text-[11px] text-slate-400 dark:text-zinc-500 mt-1.5">
              Obtenha sua chave gratuitamente no
              <a
                href="https://aistudio.google.com/app/apikey"
                target="_blank"
                rel="noopener noreferrer"
                class="text-indigo-600 dark:text-indigo-400 hover:underline"
              >
                Google AI Studio
              </a>.
            </p>
          </div>

          <button
            type="submit"
            :disabled="credentialStore.isLoading"
            class="w-full py-2.5 px-4 bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 disabled:opacity-50 text-white text-sm font-medium rounded-xl shadow-xs transition-all flex items-center justify-center gap-2 cursor-pointer"
          >
            <Loader2 v-if="credentialStore.isLoading" class="w-4 h-4 animate-spin" />
            <span>{{ credentialStore.isValid ? "Validar e Substituir Chave" : "Validar e Salvar Chave" }}</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>
