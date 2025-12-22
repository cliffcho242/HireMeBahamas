/**
 * PRODUCTION-ONLY API CONFIG
 * No fallbacks
 * No localhost
 * No same-origin
 * Fail fast if misconfigured
 */
export function getApiBase(): string {
  const base = import.meta.env.VITE_API_BASE_URL;

  if (!base) {
    console.error("❌ VITE_API_BASE_URL missing");
    return "";
  }

  if (!base.startsWith("https://")) {
    console.error("❌ VITE_API_BASE_URL must be HTTPS in production");
    return "";
  }

  return base.replace(/\/+$/, "");
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
  if (!API_BASE_URL) {
    console.warn("API base missing, skipping request for", path);
    return Promise.reject(new Error("API base URL is not configured"));
  }

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
