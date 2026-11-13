import { defineStore } from "pinia";
import { ref, computed } from "vue";

export type ThemeMode = "dark" | "light";

export const useThemeStore = defineStore("theme", () => {
  const THEME_STORAGE_KEY = "atlas_ai_theme";

  // Initialize theme from localStorage or fallback to 'light'
  const savedTheme = (typeof window !== "undefined"
    ? localStorage.getItem(THEME_STORAGE_KEY)
    : null) as ThemeMode | null;

  const currentTheme = ref<ThemeMode>(savedTheme || "light");

  const isDark = computed(() => currentTheme.value === "dark");

  function applyTheme(theme: ThemeMode) {
    if (typeof document === "undefined") return;
    const root = document.documentElement;
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
  }

  function initTheme() {
    applyTheme(currentTheme.value);
  }

  function toggleTheme() {
    const nextTheme: ThemeMode = currentTheme.value === "dark" ? "light" : "dark";
    currentTheme.value = nextTheme;
    if (typeof window !== "undefined") {
      localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
    }
    applyTheme(nextTheme);
  }

  function setTheme(theme: ThemeMode) {
    currentTheme.value = theme;
    if (typeof window !== "undefined") {
      localStorage.setItem(THEME_STORAGE_KEY, theme);
    }
    applyTheme(theme);
  }

  return {
    currentTheme,
    isDark,
    initTheme,
    toggleTheme,
    setTheme,
  };
});
