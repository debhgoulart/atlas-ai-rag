<script setup lang="ts">
import Navbar from "@/components/Navbar.vue";
import { RouterView } from "vue-router";
</script>

<template>
  <div class="min-h-screen flex flex-col bg-slate-50 text-slate-900">
    <Navbar />
    <main class="flex-1 flex flex-col">
      <RouterView />
    </main>
  </div>
</template>
