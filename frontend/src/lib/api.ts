/**
 * PRODUCTION-ONLY API CONFIG
 * No fallbacks
 * No localhost
 * No same-origin
 * Fail fast if misconfigured
 */
export function getApiBase(): string {
  const localOverride = import.meta.env.VITE_API_URL;
  const raw = localOverride || import.meta.env.VITE_API_BASE_URL;

  if (!raw) {
    throw new Error("❌ VITE_API_BASE_URL is required");
  }

  const requiresHttps = import.meta.env.PROD || !localOverride;
  if (requiresHttps && !raw.startsWith("https://")) {
    throw new Error("❌ VITE_API_BASE_URL must be HTTPS in production");
  }

  return raw.replace(/\/+$/, "");
}

export const API_BASE_URL = getApiBase();

export function apiUrl(path: string): string {
  if (!path.startsWith("/")) path = "/" + path;
  return `${API_BASE_URL}${path}`;
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
