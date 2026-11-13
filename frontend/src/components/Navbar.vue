<script setup lang="ts">
import { Bot, Database, Github, Sun, Moon } from "lucide-vue-next";
import { RouterLink } from "vue-router";
import { useThemeStore } from "@/stores/themeStore";

const themeStore = useThemeStore();
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

        <!-- Right Side: Engine info, Theme Toggle & Links -->
        <div class="flex items-center gap-2 sm:gap-3">
          <div class="hidden sm:flex items-center gap-2 px-3 py-1 text-xs text-slate-600 bg-slate-100 border border-slate-200 dark:text-zinc-300 dark:bg-zinc-900 dark:border-zinc-800 rounded-full transition-colors">
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>Gemini Flash + pgvector</span>
          </div>

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
</template>
