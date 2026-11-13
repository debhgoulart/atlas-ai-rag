import { apiClient } from "@/services/api";
import type { LoginCredentials, RegisterData, TokenResponse, User } from "@/types";

export const authService = {
  async register(data: RegisterData): Promise<User> {
    const response = await apiClient.post<User>("/auth/register", data);
    return response.data;
  },

  async login(credentials: LoginCredentials): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>("/auth/login", credentials);
    return response.data;
  },

  async getMe(): Promise<User> {
    const response = await apiClient.get<User>("/auth/me");
    return response.data;
  },
};
