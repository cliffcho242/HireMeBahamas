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

  const isProd = import.meta.env.PROD;

  if (isProd && !base.startsWith("https://")) {
    console.error("❌ VITE_API_BASE_URL must be HTTPS in production");
    return "";
  }

  if (!base.startsWith("https://") && !base.startsWith("http://")) {
    console.error("❌ VITE_API_BASE_URL must start with http:// or https://");
    return "";
  }

  if (!isProd && base.startsWith("http://")) {
    console.warn("⚠️ VITE_API_BASE_URL is not HTTPS (allowed in development)");
  }

  return base.replace(/\/+$/, "");
}

export const API_BASE_URL = getApiBase();

export function apiUrl(path: string): string {
  if (!API_BASE_URL) return "";
  if (!path.startsWith("/")) path = "/" + path;
  return `${API_BASE_URL}${path}`;
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const targetUrl = apiUrl(path);
  if (!targetUrl) {
    console.error("API base missing, skipping request for", path);
    throw new Error("API base URL is not configured");
  }

  const res = await fetch(targetUrl, {
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
