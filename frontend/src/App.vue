<script setup lang="ts">
import { onMounted } from "vue";
import Navbar from "@/components/Navbar.vue";
import GeminiKeyModal from "@/components/GeminiKeyModal.vue";
import { RouterView } from "vue-router";
import { useThemeStore } from "@/stores/themeStore";
import { useAuthStore } from "@/stores/authStore";
import { useGeminiCredentialStore } from "@/stores/geminiCredentialStore";

const themeStore = useThemeStore();
const authStore = useAuthStore();
const credentialStore = useGeminiCredentialStore();

onMounted(async () => {
  themeStore.initTheme();
  await authStore.initAuth();
  await credentialStore.fetchStatus();

  // If user is authenticated but has no key configured or key is invalid, prompt configuration
  if (authStore.isAuthenticated && (credentialStore.isNotConfigured || credentialStore.isInvalid)) {
    credentialStore.openModal();
  }
});
</script>

<template>
  <div class="min-h-screen flex flex-col bg-slate-50 dark:bg-black text-slate-900 dark:text-white transition-colors duration-150">
    <Navbar />
    <main class="flex-1 flex flex-col">
      <RouterView />
    </main>
    <GeminiKeyModal />
  </div>
</template>
