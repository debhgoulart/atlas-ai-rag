<script setup lang="ts">
import { ref } from "vue";
import { Bot, Database, Github, Sun, Moon, KeyRound, LogIn, LogOut, User as UserIcon } from "lucide-vue-next";
import { RouterLink } from "vue-router";
import { useThemeStore } from "@/stores/themeStore";
import { useAuthStore } from "@/stores/authStore";
import { useGeminiCredentialStore } from "@/stores/geminiCredentialStore";
import AuthModal from "@/components/AuthModal.vue";

const themeStore = useThemeStore();
const authStore = useAuthStore();
const credentialStore = useGeminiCredentialStore();

const isAuthModalOpen = ref(false);

function openAuth() {
  isAuthModalOpen.value = true;
}

function handleKeyClick() {
  if (!authStore.isAuthenticated) {
    isAuthModalOpen.value = true;
  } else {
    credentialStore.openModal();
  }
}
</script>

<template>
  <header class="sticky top-0 z-30 bg-white/85 dark:bg-black/90 backdrop-blur-md border-b border-slate-200 dark:border-zinc-850 transition-colors">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo and Brand -->
        <div class="flex items-center gap-6">
          <RouterLink to="/" class="flex items-center gap-2.5 group">
            <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-600 flex items-center justify-center text-white shadow-md shadow-indigo-500/20 group-hover:scale-105 transition-transform">
              <Bot class="w-5 h-5" />
            </div>
            <div>
              <span class="text-lg font-bold text-slate-900 dark:text-white tracking-tight">Atlas <span class="text-indigo-600 dark:text-indigo-400">AI</span></span>
              <span class="hidden sm:inline-block ml-2 px-2 py-0.5 text-xs font-medium rounded-full bg-indigo-50 text-indigo-700 border border-indigo-100 dark:bg-indigo-950/70 dark:text-indigo-300 dark:border-indigo-800/60">
                RAG Engine
              </span>
            </div>
          </RouterLink>

          <!-- Navigation Links -->
          <nav class="hidden md:flex items-center gap-1">
            <RouterLink
              to="/"
              class="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium text-slate-600 hover:text-indigo-600 hover:bg-slate-100/80 dark:text-zinc-400 dark:hover:text-white dark:hover:bg-zinc-900 transition-colors"
              active-class="!text-indigo-600 !bg-indigo-50 dark:!text-indigo-400 dark:!bg-zinc-900"
            >
              <Database class="w-4 h-4" />
              Bases de Conhecimento
            </RouterLink>
          </nav>
        </div>

        <!-- Right Side: Key status, Auth, Theme Toggle & Links -->
        <div class="flex items-center gap-2 sm:gap-3">
          <!-- Gemini Key Status Button -->
          <button
            @click="handleKeyClick"
            type="button"
            class="flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-lg border transition-all cursor-pointer"
            :class="[
              credentialStore.isValid
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/50 dark:text-emerald-400 dark:border-emerald-800/60 hover:bg-emerald-100'
                : credentialStore.isInvalid
                ? 'bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/50 dark:text-rose-400 dark:border-rose-800/60 hover:bg-rose-100'
                : 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/50 dark:text-amber-400 dark:border-amber-800/60 hover:bg-amber-100'
            ]"
            :title="credentialStore.isValid ? 'Sua chave do Gemini está ativa e configurada' : 'Clique para configurar sua Gemini API Key'"
          >
            <span
              class="w-2 h-2 rounded-full"
              :class="[
                credentialStore.isValid ? 'bg-emerald-500 animate-pulse' : credentialStore.isInvalid ? 'bg-rose-500' : 'bg-amber-500 animate-bounce'
              ]"
            ></span>
            <KeyRound class="w-3.5 h-3.5" />
            <span class="hidden sm:inline">
              {{ credentialStore.isValid ? `Gemini Key (${credentialStore.keyHint})` : credentialStore.isInvalid ? 'Chave Inválida' : 'Configurar Chave' }}
            </span>
          </button>

          <!-- User Authentication Actions -->
          <div v-if="authStore.isAuthenticated" class="flex items-center gap-1.5">
            <div class="hidden md:flex items-center gap-1.5 px-2.5 py-1 text-xs text-slate-700 dark:text-zinc-300 bg-slate-100 dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-lg">
              <UserIcon class="w-3.5 h-3.5 text-indigo-500" />
              <span class="max-w-[120px] truncate">{{ authStore.user?.email || 'Minha Conta' }}</span>
            </div>
            <button
              @click="authStore.logout()"
              type="button"
              class="p-2 text-slate-500 hover:text-rose-600 hover:bg-slate-100 dark:text-zinc-400 dark:hover:text-rose-400 dark:hover:bg-zinc-900 rounded-lg transition-colors cursor-pointer"
              title="Sair da Conta"
            >
              <LogOut class="w-4 h-4" />
            </button>
          </div>
          <button
            v-else
            @click="openAuth"
            type="button"
            class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg shadow-2xs transition-colors cursor-pointer"
          >
            <LogIn class="w-3.5 h-3.5" />
            <span>Entrar</span>
          </button>

          <!-- Theme Toggle Button -->
          <button
            @click="themeStore.toggleTheme"
            type="button"
            class="p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-100 dark:text-zinc-400 dark:hover:text-white dark:hover:bg-zinc-900 rounded-lg transition-colors cursor-pointer"
            :title="themeStore.isDark ? 'Alternar para Modo Claro' : 'Alternar para Modo Escuro (Preto OLED)'"
          >
            <Sun v-if="themeStore.isDark" class="w-5 h-5 text-amber-400 transition-transform rotate-0 hover:rotate-45" />
            <Moon v-else class="w-5 h-5 text-slate-700 transition-transform hover:-rotate-12" />
          </button>

          <a
            href="https://github.com/debhgoulart/atlas-ai-rag"
            target="_blank"
            rel="noopener noreferrer"
            class="p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-100 dark:text-zinc-400 dark:hover:text-white dark:hover:bg-zinc-900 rounded-lg transition-colors cursor-pointer"
            title="Repositório no GitHub"
          >
            <Github class="w-5 h-5" />
          </a>
        </div>
      </div>
    </div>
  </header>

  <!-- Auth Modal -->
  <AuthModal :is-open="isAuthModalOpen" @close="isAuthModalOpen = false" />
</template>
