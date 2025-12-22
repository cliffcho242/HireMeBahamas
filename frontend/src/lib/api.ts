/**
 * Robust API base URL getter
 * Priority:
 * VITE_API_BASE_URL (production)
 * VITE_API_URL (dev override; HTTP allowed only for localhost)
 * Same-origin fallback (Vercel proxy)
 */
export function getApiBaseUrl(): string {
  const baseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
  const overrideUrl = import.meta.env.VITE_API_URL?.trim();

  const normalize = (url: string) => url.replace(/\/+$/, "");

  if (baseUrl) {
    if (!baseUrl.startsWith("https://")) {
      console.warn(
        `[getApiBaseUrl] Warning: VITE_API_BASE_URL must be HTTPS in production: ${baseUrl}`
      );
    }
    return normalize(baseUrl);
  }

  if (overrideUrl && overrideUrl.startsWith("http://localhost")) {
    return normalize(overrideUrl);
  }

  return "";
}

export function buildApiUrl(path: string): string {
  const base = getApiBaseUrl();
  if (!path.startsWith("/")) path = "/" + path;
  return `${base}${path}`;
}

export const apiUrl = buildApiUrl;
export const getApiBase = getApiBaseUrl;
export function isApiConfigured(): boolean {
  const base = getApiBaseUrl();
  if (!base) return true;
  return (
    base.startsWith("https://") ||
    base.startsWith("http://localhost")
  );
}
