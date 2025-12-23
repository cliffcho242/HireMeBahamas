/**
 * PRODUCTION-SAFE API CONFIG
 * - Never throws during app boot to prevent white screens
 * - Logs warnings for missing configuration
 * - Returns empty string if API URL is not configured
 * - Wrapped in try-catch to ensure env issues never crash rendering
 */
export function getApiBase(): string {
  try {
    const localOverride = import.meta.env.VITE_API_URL;
    const raw = localOverride || import.meta.env.VITE_API_BASE_URL;

    if (!raw) {
      console.warn("⚠️ VITE_API_BASE_URL missing - API calls will fail gracefully");
      return "";
    }

    // Allow http only when using a local override outside production builds
    const requiresHttps = import.meta.env.PROD || !localOverride;
    if (requiresHttps && !raw.startsWith("https://")) {
      console.warn("⚠️ VITE_API_BASE_URL should be HTTPS in production");
      // Don't throw - let the app render and show appropriate error UI
    }

    return raw.replace(/\/+$/, "");
  } catch {
    // If anything fails during env access, return empty string safely
    return "";
  }
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
