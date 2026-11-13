import { createRouter, createWebHistory } from "vue-router";
import DashboardView from "@/views/DashboardView.vue";
import KnowledgeBaseDetailView from "@/views/KnowledgeBaseDetailView.vue";
import LoginView from "@/views/LoginView.vue";
import { useAuthStore } from "@/stores/authStore";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/login",
      name: "login",
      component: LoginView,
      meta: { guestOnly: true },
    },
    {
      path: "/",
      name: "dashboard",
      component: DashboardView,
      meta: { requiresAuth: true },
    },
    {
      path: "/knowledge-bases/:id",
      name: "knowledge-base-detail",
      component: KnowledgeBaseDetailView,
      props: true,
      meta: { requiresAuth: true },
    },
    {
      path: "/:pathMatch(.*)*",
      redirect: "/",
    },
  ],
});

let authInitialized = false;

router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore();

  // Validate stored token with backend once upon application start
  if (!authInitialized) {
    authInitialized = true;
    if (authStore.token) {
      await authStore.initAuth();
    }
  }

  const isAuth = authStore.isAuthenticated;

  if (to.meta.guestOnly && isAuth) {
    next({ name: "dashboard" });
  } else if (to.name !== "login" && !isAuth) {
    next({
      name: "login",
      query: to.fullPath !== "/" ? { redirect: to.fullPath } : {},
    });
  } else {
    next();
  }
});

export default router;
