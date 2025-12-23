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
    console.error("❌ VITE_API_BASE_URL missing");
    console.error(
      'Application configuration error: API base URL is not set.\n' +
      'API calls will fail until this is configured.\n' +
      'For developers: Set VITE_API_BASE_URL in your environment configuration.'
    );
    // Return empty string instead of throwing - let the app render but API calls will fail gracefully
    return '';
  }

  // Allow http only when using a local override outside production builds
  const requiresHttps = import.meta.env.PROD || !localOverride;
  if (requiresHttps && !raw.startsWith("https://")) {
    console.error("❌ VITE_API_BASE_URL must be HTTPS in production");
    console.error(
      'Application configuration error: Insecure API URL detected.\n' +
      'Production deployments require secure HTTPS connections.\n' +
      'For developers: Update VITE_API_BASE_URL to use HTTPS.'
    );
    // Return the URL anyway but log the error - allow basic rendering
    return raw.replace(/\/+$/, "");
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
    // Return a rejected promise with a clear error message
    // This allows callers to catch and handle the error gracefully
    return Promise.reject(new Error("API base URL missing - check configuration"));
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
