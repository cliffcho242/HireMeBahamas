/**
 * PRODUCTION-ONLY API CONFIG
 * No fallbacks
 * No localhost
 * No same-origin
 * Fail fast if misconfigured
 */
export function getApiBase(): string {
  const raw = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL;

  if (!raw) {
    throw new Error("❌ VITE_API_BASE_URL is required");
  }

  if (import.meta.env.PROD && !raw.startsWith("https://")) {
    throw new Error("❌ VITE_API_BASE_URL must be HTTPS in production");
  }

  return raw.replace(/\/+$/, "");
}

export const API_BASE_URL = getApiBase();

export function getApiBaseUrl(): string {
  return getApiBase();
}

export function apiUrl(path: string): string {
  if (!path.startsWith("/")) path = "/" + path;
  return `${API_BASE_URL}${path}`;
}

export function buildApiUrl(path: string): string {
  return apiUrl(path);
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const res = await fetch(apiUrl(path), {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }

  return res.json();
}
