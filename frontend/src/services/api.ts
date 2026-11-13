import axios, { type AxiosError } from "axios";
import type { ApiError } from "@/types";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export const apiClient = axios.create({
  baseURL: apiBaseUrl,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 45000, // 45 seconds to accommodate LLM cold starts
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("atlas_auth_token");
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    let message = "Ocorreu um erro inesperado ao se comunicar com o servidor.";
    let code = "UNKNOWN_ERROR";

    if (error.response?.data) {
      const data = error.response.data;
      if (typeof data.detail === "string") {
        message = data.detail;
      }
      if (data.code) {
        code = data.code;
      }
    } else if (error.code === "ERR_NETWORK") {
      message = "Não foi possível conectar ao backend do Atlas AI. Verifique se o servidor está ativo.";
      code = "NETWORK_ERROR";
    }

    return Promise.reject({ detail: message, code });
  }
);
