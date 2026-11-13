import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { geminiCredentialService } from "@/services/geminiCredentialService";
import type { ApiKeyStatus } from "@/types";

export const useGeminiCredentialStore = defineStore("geminiCredential", () => {
  const status = ref<ApiKeyStatus>("NOT_CONFIGURED");
  const keyHint = ref<string | null>(null);
  const lastValidatedAt = ref<string | null>(null);
  const isLoading = ref<boolean>(false);
  const isModalOpen = ref<boolean>(false);

  const isValid = computed(() => status.value === "VALID");
  const isNotConfigured = computed(() => status.value === "NOT_CONFIGURED");
  const isInvalid = computed(() => status.value === "INVALID");

  async function fetchStatus(): Promise<void> {
    const token = localStorage.getItem("atlas_auth_token");
    if (!token) {
      status.value = "NOT_CONFIGURED";
      keyHint.value = null;
      return;
    }

    try {
      isLoading.value = true;
      const res = await geminiCredentialService.getStatus();
      status.value = res.status;
      keyHint.value = res.key_hint;
      lastValidatedAt.value = res.last_validated_at;
    } catch {
      status.value = "NOT_CONFIGURED";
      keyHint.value = null;
    } finally {
      isLoading.value = false;
    }
  }

  async function saveKey(apiKey: string): Promise<void> {
    isLoading.value = true;
    try {
      const res = await geminiCredentialService.saveKey(apiKey);
      status.value = res.status;
      keyHint.value = res.key_hint;
      lastValidatedAt.value = res.last_validated_at;
    } finally {
      isLoading.value = false;
    }
  }

  async function removeKey(): Promise<void> {
    isLoading.value = true;
    try {
      const res = await geminiCredentialService.deleteKey();
      status.value = res.status;
      keyHint.value = null;
      lastValidatedAt.value = null;
    } finally {
      isLoading.value = false;
    }
  }

  function openModal(): void {
    isModalOpen.value = true;
  }

  function closeModal(): void {
    isModalOpen.value = false;
  }

  return {
    status,
    keyHint,
    lastValidatedAt,
    isLoading,
    isModalOpen,
    isValid,
    isNotConfigured,
    isInvalid,
    fetchStatus,
    saveKey,
    removeKey,
    openModal,
    closeModal,
  };
});
