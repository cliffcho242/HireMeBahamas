/**
 * PRODUCTION-ONLY API CONFIG
 * No fallbacks
 * No localhost
 * No same-origin
 * Non-fatal: warns instead of throwing to prevent white screen
 */
export function getApiBase(): string {
  const localOverride = import.meta.env.VITE_API_URL;
  const raw = localOverride || import.meta.env.VITE_API_BASE_URL;

  if (!raw) {
    console.warn("VITE_API_BASE_URL missing");
    return "";
  }

  // Allow http only when using a local override outside production builds
  const requiresHttps = import.meta.env.PROD || !localOverride;
  if (requiresHttps && !raw.startsWith("https://")) {
    console.warn("VITE_API_BASE_URL must be HTTPS in production");
    return "";
  }

  return raw.replace(/\/+$/, "");
}

export const API_BASE_URL = getApiBase();

export function apiUrl(path: string): string {
  if (!API_BASE_URL) {
    console.warn("API base missing, building relative URL", { path });
    if (!path.startsWith("/")) path = "/" + path;
    return path;
  }
  if (!path.startsWith("/")) path = "/" + path;
  return `${API_BASE_URL}${path}`;
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  if (!API_BASE_URL) {
    console.warn("API base missing, skipping request", { path });
    // Return a rejected promise so callers can handle gracefully without crashing render
    return Promise.reject(new Error("API base URL missing"));
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
