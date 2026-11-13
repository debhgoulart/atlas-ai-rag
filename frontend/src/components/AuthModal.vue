<script setup lang="ts">
import { ref } from "vue";
import { X, LogIn, UserPlus, AlertCircle, Loader2 } from "lucide-vue-next";
import { useAuthStore } from "@/stores/authStore";
import { useGeminiCredentialStore } from "@/stores/geminiCredentialStore";

const props = defineProps<{
  isOpen: boolean;
}>();

const emit = defineEmits<{
  (e: "close"): void;
}>();

const authStore = useAuthStore();
const credentialStore = useGeminiCredentialStore();

const isRegister = ref(false);
const email = ref("");
const password = ref("");
const errorMessage = ref("");

function switchTab(register: boolean) {
  isRegister.value = register;
  errorMessage.value = "";
}

async function handleSubmit() {
  errorMessage.value = "";
  if (!email.value || !password.value) {
    errorMessage.value = "Por favor, preencha todos os campos.";
    return;
  }

  if (isRegister.value && password.value.length < 8) {
    errorMessage.value = "A senha deve conter no mínimo 8 caracteres.";
    return;
  }

  try {
    if (isRegister.value) {
      await authStore.register({ email: email.value, password: password.value });
    } else {
      await authStore.login({ email: email.value, password: password.value });
    }
    await credentialStore.fetchStatus();
    emit("close");
    email.value = "";
    password.value = "";
  } catch (err: any) {
    errorMessage.value = err?.detail || "Falha na autenticação. Verifique os dados informados.";
  }
}
</script>

<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs transition-opacity"
  >
    <div
      class="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-2xl w-full max-w-md shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150"
    >
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100 dark:border-zinc-800">
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-950 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
            <LogIn v-if="!isRegister" class="w-4 h-4" />
            <UserPlus v-else class="w-4 h-4" />
          </div>
          <h2 class="text-base font-semibold text-slate-900 dark:text-white">
            {{ isRegister ? "Criar Conta no Atlas AI" : "Entrar no Atlas AI" }}
          </h2>
        </div>
        <button
          @click="emit('close')"
          type="button"
          class="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-zinc-200 rounded-lg hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors"
        >
          <X class="w-4 h-4" />
        </button>
      </div>

      <!-- Tabs -->
      <div class="flex border-b border-slate-100 dark:border-zinc-800 bg-slate-50 dark:bg-zinc-950/40 p-1">
        <button
          @click="switchTab(false)"
          type="button"
          class="flex-1 py-2 text-xs font-medium rounded-lg transition-all"
          :class="!isRegister ? 'bg-white dark:bg-zinc-900 text-indigo-600 dark:text-indigo-400 shadow-2xs font-semibold' : 'text-slate-500 dark:text-zinc-400 hover:text-slate-800 dark:hover:text-zinc-200'"
        >
          Entrar
        </button>
        <button
          @click="switchTab(true)"
          type="button"
          class="flex-1 py-2 text-xs font-medium rounded-lg transition-all"
          :class="isRegister ? 'bg-white dark:bg-zinc-900 text-indigo-600 dark:text-indigo-400 shadow-2xs font-semibold' : 'text-slate-500 dark:text-zinc-400 hover:text-slate-800 dark:hover:text-zinc-200'"
        >
          Cadastre-se
        </button>
      </div>

      <!-- Form Body -->
      <form @submit.prevent="handleSubmit" class="p-6 space-y-4">
        <div v-if="errorMessage" class="flex items-center gap-2 p-3 text-xs text-rose-700 bg-rose-50 border border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-900/60 rounded-xl">
          <AlertCircle class="w-4 h-4 shrink-0" />
          <span>{{ errorMessage }}</span>
        </div>

        <div>
          <label class="block text-xs font-medium text-slate-700 dark:text-zinc-300 mb-1.5">
            E-mail
          </label>
          <input
            v-model="email"
            type="email"
            required
            placeholder="seu.email@exemplo.com"
            class="w-full px-3.5 py-2 text-sm bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-zinc-500"
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-slate-700 dark:text-zinc-300 mb-1.5">
            Senha
          </label>
          <input
            v-model="password"
            type="password"
            required
            placeholder="••••••••"
            class="w-full px-3.5 py-2 text-sm bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-zinc-500"
          />
          <p v-if="isRegister" class="text-[11px] text-slate-400 dark:text-zinc-500 mt-1">
            Mínimo de 8 caracteres.
          </p>
        </div>

        <button
          type="submit"
          :disabled="authStore.isLoading"
          class="w-full mt-2 py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-medium rounded-xl shadow-xs transition-colors flex items-center justify-center gap-2 cursor-pointer"
        >
          <Loader2 v-if="authStore.isLoading" class="w-4 h-4 animate-spin" />
          <span>{{ isRegister ? "Concluir Cadastro" : "Acessar Conta" }}</span>
        </button>
      </form>
    </div>
  </div>
</template>
