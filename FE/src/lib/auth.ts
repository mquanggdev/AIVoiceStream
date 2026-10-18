import { API_URL } from "./api";

export type AdminUser = {
  id: number;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
};

export const TOKEN_KEY = "ocean_park_admin_token";

export function getToken() {
  return typeof window === "undefined" ? null : localStorage.getItem(TOKEN_KEY);
}

export async function adminFetch(path: string, init: RequestInit = {}) {
  const token = getToken();
  const headers = new Headers(init.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (init.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  const response = await fetch(`${API_URL}${path}`, { ...init, headers });
  if (response.status === 401 && typeof window !== "undefined") {
    localStorage.removeItem(TOKEN_KEY);
    window.location.href = "/admin/login";
  }
  return response;
}

/** Tải file ghi âm (cần token) và trả về object URL để gán cho <audio>. */
export async function fetchAudioUrl(messageId: number): Promise<string | null> {
  const response = await adminFetch(`/admin/messages/${messageId}/audio`);
  if (!response.ok) return null;
  return URL.createObjectURL(await response.blob());
}
