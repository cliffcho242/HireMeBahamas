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
  const normalize = (url: string) => url.replace(/\/+$/, "");

  if (overrideUrl && overrideUrl.startsWith("http://localhost")) return normalize(overrideUrl);
  if (baseUrl) return normalize(baseUrl);

  return "";
}

export function buildApiUrl(path: string): string {
  const base = getApiBaseUrl();
  if (!path.startsWith("/")) path = "/" + path;
  return `${base}${path}`;
}

// Backward compatibility for existing imports
export const apiUrl = buildApiUrl;
export const getApiBase = getApiBaseUrl;
export function isApiConfigured(): boolean {
  const base = getApiBaseUrl();
  if (!base) return true;
  return base.startsWith("https://") || base.startsWith("http://localhost");
}
