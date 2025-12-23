/**
 * PRODUCTION-SAFE API CONFIG
 * - Never throws during app boot to prevent white screens
 * - Logs warnings for missing configuration
 * - Uses getApiBase from env.ts for consistent fallback behavior
 * - Wrapped in try-catch to ensure env issues never crash rendering
 */

// Import the safe API base URL getter and fallback
import { getApiBase } from './env';

export { getApiBase } from './env';
export const API_BASE_URL = getApiBase();

export function apiUrl(path: string): string {
  if (!API_BASE_URL) {
    console.warn("API base missing, using relative URL", { path });
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
