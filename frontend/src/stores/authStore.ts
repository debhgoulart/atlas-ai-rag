import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { authService } from "@/services/authService";
import type { LoginCredentials, RegisterData, User } from "@/types";

export const useAuthStore = defineStore("auth", () => {
  const token = ref<string | null>(localStorage.getItem("atlas_auth_token"));
  const user = ref<User | null>(null);
  const isLoading = ref<boolean>(false);

  const isAuthenticated = computed(() => !!token.value);

  async function initAuth(): Promise<void> {
    if (!token.value) return;
    try {
      isLoading.value = true;
      user.value = await authService.getMe();
    } catch {
      logout();
    } finally {
      isLoading.value = false;
    }
  }

  async function login(credentials: LoginCredentials): Promise<void> {
    isLoading.value = true;
    try {
      const response = await authService.login(credentials);
      token.value = response.access_token;
      localStorage.setItem("atlas_auth_token", response.access_token);
      user.value = await authService.getMe();
    } finally {
      isLoading.value = false;
    }
  }

  async function register(data: RegisterData): Promise<void> {
    isLoading.value = true;
    try {
      await authService.register(data);
      await login({ email: data.email, password: data.password });
    } finally {
      isLoading.value = false;
    }
  }

  function logout(): void {
    token.value = null;
    user.value = null;
    localStorage.removeItem("atlas_auth_token");
  }

  return {
    token,
    user,
    isLoading,
    isAuthenticated,
    initAuth,
    login,
    register,
    logout,
  };
});
