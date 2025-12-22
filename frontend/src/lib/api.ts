/**
 * Robust API base URL getter
 * 
 * Priority:
 * 1. VITE_API_BASE_URL (production)
 * 2. VITE_API_URL (dev override; HTTP allowed only for localhost)
 * 3. Same-origin fallback (Vercel proxy)
 */
export function getApiBaseUrl(): string {
  const baseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
  const overrideUrl = import.meta.env.VITE_API_URL?.trim();

  const normalize = (url: string) => url.replace(/\/+$/, ""); // remove trailing slash

  // Dev override for localhost (HTTP allowed)
  if (
    overrideUrl &&
    (overrideUrl.startsWith("http://localhost") ||
      overrideUrl.startsWith("http://127.0.0.1") ||
      overrideUrl.startsWith("http://0.0.0.0"))
  ) {
    return normalize(overrideUrl);
  }

  // Production environment variable
  if (baseUrl) {
    if (!baseUrl.startsWith("https://")) {
      console.warn(
        `[getApiBaseUrl] Warning: VITE_API_BASE_URL must be HTTPS in production: ${baseUrl}`
      );
    }
    return normalize(baseUrl);
  }

  // Default fallback: same-origin (Vercel proxy)
  return "";
}

/**
 * Helper to build full endpoint URLs safely
 * Example:
 *   const url = buildApiUrl("/api/auth/login");
 */
export function buildApiUrl(path: string): string {
  const base = getApiBaseUrl();
  if (!path.startsWith("/")) {
    path = "/" + path;
  }
  return `${base}${path}`;
}

// Backward compatibility for existing imports
export const apiUrl = buildApiUrl;
export const getApiBase = getApiBaseUrl;
export function isApiConfigured(): boolean {
  const base = getApiBaseUrl();
  if (!base) return true; // same-origin fallback
  return (
    base.startsWith("https://") ||
    base.startsWith("http://localhost") ||
    base.startsWith("http://127.0.0.1") ||
    base.startsWith("http://0.0.0.0")
  );
}
