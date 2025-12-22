/**
 * PRODUCTION-ONLY API CONFIG
 * - No fallbacks
 * - No localhost
 * - No same-origin
 * - Fail fast if misconfigured
 */

const RAW_API_BASE = import.meta.env.VITE_API_BASE_URL;

if (!RAW_API_BASE) {
  throw new Error(
    "❌ VITE_API_BASE_URL is missing in PRODUCTION build"
  );
}

if (!RAW_API_BASE.startsWith("https://")) {
  throw new Error(
    "❌ VITE_API_BASE_URL must be HTTPS in production"
  );
}

export const API_BASE_URL = RAW_API_BASE.replace(/\/+$/, "");

export function apiUrl(path: string): string {
  if (!path.startsWith("/")) path = "/" + path;
  return `${API_BASE_URL}${path}`;
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
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
