<script setup lang="ts">
import { Sparkles, Database, MessageSquareText, Github } from "lucide-vue-next";
import { RouterLink } from "vue-router";
</script>

<template>
  <header class="sticky top-0 z-30 bg-white/80 backdrop-blur-md border-b border-slate-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo and Brand -->
        <div class="flex items-center gap-6">
          <RouterLink to="/" class="flex items-center gap-2.5 group">
            <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-600 flex items-center justify-center text-white shadow-md shadow-indigo-500/20 group-hover:scale-105 transition-transform">
              <Sparkles class="w-5 h-5" />
            </div>
            <div>
              <span class="text-lg font-bold text-slate-900 tracking-tight">Atlas <span class="text-indigo-600">AI</span></span>
              <span class="hidden sm:inline-block ml-2 px-2 py-0.5 text-xs font-medium rounded-full bg-indigo-50 text-indigo-700 border border-indigo-100">
                RAG Engine
              </span>
            </div>
          </RouterLink>

          <!-- Navigation Links -->
          <nav class="hidden md:flex items-center gap-1">
            <RouterLink
              to="/"
              class="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium text-slate-600 hover:text-indigo-600 hover:bg-slate-50 transition-colors"
              active-class="!text-indigo-600 !bg-indigo-50"
            >
              <Database class="w-4 h-4" />
              Bases de Conhecimento
            </RouterLink>
          </nav>
        </div>

        <!-- Right Side: Engine info & Links -->
        <div class="flex items-center gap-3">
          <div class="hidden sm:flex items-center gap-2 px-3 py-1 text-xs text-slate-600 rounded-full bg-slate-100 border border-slate-200">
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>Gemini Flash + pgvector</span>
          </div>

          <a
            href="https://github.com/debhgoulart/atlas-ai-rag"
            target="_blank"
            rel="noopener noreferrer"
            class="p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors"
            title="Repositório no GitHub"
          >
            <Github class="w-5 h-5" />
          </a>
        </div>
      </div>
    </div>
  </header>
</template>
