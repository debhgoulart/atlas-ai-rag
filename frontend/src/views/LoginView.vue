<script setup lang="ts">
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import {
  Bot,
  LogIn,
  UserPlus,
  AlertCircle,
  Loader2,
  Eye,
  EyeOff,
  Lock,
  Mail,
  ShieldCheck,
} from "lucide-vue-next";
import { useAuthStore } from "@/stores/authStore";
import { useGeminiCredentialStore } from "@/stores/geminiCredentialStore";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const credentialStore = useGeminiCredentialStore();

const isRegister = ref(false);
const email = ref("");
const password = ref("");
const confirmPassword = ref("");
const showPassword = ref(false);
const showConfirmPassword = ref(false);
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

  if (isRegister.value) {
    if (password.value.length < 8) {
      errorMessage.value = "A senha deve conter no mínimo 8 caracteres.";
      return;
    }
    if (password.value !== confirmPassword.value) {
      errorMessage.value = "As senhas não coincidem. Digite a mesma senha em ambos os campos.";
      return;
    }
  }

  try {
    if (isRegister.value) {
      await authStore.register({ email: email.value, password: password.value });
    } else {
      await authStore.login({ email: email.value, password: password.value });
    }

    // Check Gemini credential status after successful login
    await credentialStore.fetchStatus();

    // Determine target redirect
    const rawRedirect = route.query.redirect;
    const target =
      typeof rawRedirect === "string" && rawRedirect.startsWith("/") && !rawRedirect.startsWith("/login")
        ? rawRedirect
        : "/";

    await router.push(target);

    // If key not configured, prompt modal
    if (credentialStore.isNotConfigured || credentialStore.isInvalid) {
      credentialStore.openModal();
    }
  } catch (err: any) {
    errorMessage.value =
      err?.detail || "Falha na autenticação. Verifique os dados informados e tente novamente.";
  }
}
</script>

<template>
  <div class="flex-1 flex items-center justify-center p-4 sm:p-6 lg:p-8">
    <div class="w-full max-w-md">
      <!-- Card Container -->
      <div
        class="bg-white dark:bg-zinc-950 border border-slate-200 dark:border-zinc-850 rounded-3xl p-6 sm:p-8 shadow-xl dark:shadow-2xl dark:shadow-indigo-950/20 transition-all"
      >
        <!-- Brand Header -->
        <div class="text-center mb-6">
          <div
            class="inline-flex w-12 h-12 rounded-2xl bg-gradient-to-tr from-indigo-600 to-violet-600 items-center justify-center text-white shadow-lg shadow-indigo-500/25 mb-3"
          >
            <Bot class="w-6 h-6" />
          </div>
          <div class="flex items-center justify-center gap-2 mb-1">
            <h1 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
              Atlas <span class="text-indigo-600 dark:text-indigo-400">AI</span>
            </h1>
            <span
              class="px-2 py-0.5 text-xs font-medium rounded-full bg-indigo-50 text-indigo-700 border border-indigo-100 dark:bg-indigo-950/70 dark:text-indigo-300 dark:border-indigo-800/60"
            >
              RAG Engine
            </span>
          </div>
          <p class="text-xs sm:text-sm text-slate-500 dark:text-zinc-400">
            {{
              isRegister
                ? "Crie sua conta para gerenciar suas bases e conversar com a IA"
                : "Entre com suas credenciais para acessar a plataforma"
            }}
          </p>
        </div>

        <!-- Segmented Tab Navigation -->
        <div
          class="flex border border-slate-200 dark:border-zinc-800 rounded-xl bg-slate-100/70 dark:bg-zinc-900/70 p-1 mb-6"
        >
          <button
            type="button"
            @click="switchTab(false)"
            class="flex-1 py-2 text-xs font-semibold rounded-lg transition-all flex items-center justify-center gap-1.5 cursor-pointer"
            :class="
              !isRegister
                ? 'bg-white dark:bg-zinc-800 text-indigo-600 dark:text-indigo-400 shadow-xs'
                : 'text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white'
            "
          >
            <LogIn class="w-3.5 h-3.5" />
            <span>Entrar</span>
          </button>
          <button
            type="button"
            @click="switchTab(true)"
            class="flex-1 py-2 text-xs font-semibold rounded-lg transition-all flex items-center justify-center gap-1.5 cursor-pointer"
            :class="
              isRegister
                ? 'bg-white dark:bg-zinc-800 text-indigo-600 dark:text-indigo-400 shadow-xs'
                : 'text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white'
            "
          >
            <UserPlus class="w-3.5 h-3.5" />
            <span>Cadastre-se</span>
          </button>
        </div>

        <!-- Error Alert Banner -->
        <div
          v-if="errorMessage"
          class="mb-4 flex items-start gap-2.5 p-3.5 text-xs text-rose-700 bg-rose-50 border border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-900/60 rounded-xl animate-in fade-in"
        >
          <AlertCircle class="w-4 h-4 shrink-0 mt-0.5 text-rose-500 dark:text-rose-400" />
          <span>{{ errorMessage }}</span>
        </div>

        <!-- Authentication Form -->
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- E-mail -->
          <div>
            <label class="block text-xs font-medium text-slate-700 dark:text-zinc-300 mb-1.5">
              E-mail
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400 dark:text-zinc-500">
                <Mail class="w-4 h-4" />
              </div>
              <input
                v-model="email"
                type="email"
                required
                autocomplete="email"
                placeholder="seu.email@exemplo.com"
                class="w-full pl-10 pr-3.5 py-2.5 text-sm bg-slate-50 dark:bg-zinc-900/70 border border-slate-200 dark:border-zinc-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-zinc-500 transition-colors"
              />
            </div>
          </div>

          <!-- Senha -->
          <div>
            <label class="block text-xs font-medium text-slate-700 dark:text-zinc-300 mb-1.5">
              Senha
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400 dark:text-zinc-500">
                <Lock class="w-4 h-4" />
              </div>
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                required
                :autocomplete="isRegister ? 'new-password' : 'current-password'"
                placeholder="••••••••"
                class="w-full pl-10 pr-10 py-2.5 text-sm bg-slate-50 dark:bg-zinc-900/70 border border-slate-200 dark:border-zinc-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-zinc-500 transition-colors"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600 dark:hover:text-zinc-300 transition-colors"
                tabindex="-1"
              >
                <EyeOff v-if="showPassword" class="w-4 h-4" />
                <Eye v-else class="w-4 h-4" />
              </button>
            </div>
            <p v-if="isRegister" class="text-[11px] text-slate-500 dark:text-zinc-400 mt-1">
              Mínimo de 8 caracteres.
            </p>
          </div>

          <!-- Confirmar Senha (apenas no Cadastro) -->
          <div v-if="isRegister">
            <label class="block text-xs font-medium text-slate-700 dark:text-zinc-300 mb-1.5">
              Confirmar Senha
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400 dark:text-zinc-500">
                <Lock class="w-4 h-4" />
              </div>
              <input
                v-model="confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                required
                autocomplete="new-password"
                placeholder="••••••••"
                class="w-full pl-10 pr-10 py-2.5 text-sm bg-slate-50 dark:bg-zinc-900/70 border border-slate-200 dark:border-zinc-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-zinc-500 transition-colors"
              />
              <button
                type="button"
                @click="showConfirmPassword = !showConfirmPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600 dark:hover:text-zinc-300 transition-colors"
                tabindex="-1"
              >
                <EyeOff v-if="showConfirmPassword" class="w-4 h-4" />
                <Eye v-else class="w-4 h-4" />
              </button>
            </div>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="authStore.isLoading"
            class="w-full mt-2 py-3 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-semibold rounded-xl shadow-xs hover:shadow transition-all flex items-center justify-center gap-2 cursor-pointer"
          >
            <Loader2 v-if="authStore.isLoading" class="w-4 h-4 animate-spin" />
            <span>{{ isRegister ? "Criar Conta e Acessar" : "Acessar Plataforma" }}</span>
          </button>
        </form>

        <!-- Footnote / Security Assurance -->
        <div class="mt-6 pt-5 border-t border-slate-100 dark:border-zinc-900 text-center">
          <p class="text-[11px] text-slate-400 dark:text-zinc-500 flex items-center justify-center gap-1.5">
            <ShieldCheck class="w-3.5 h-3.5 text-emerald-500 shrink-0" />
            <span>Sessão segura e chaves individuais protegidas com AES-128</span>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
