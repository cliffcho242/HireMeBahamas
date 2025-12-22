/**
 * Robust API base URL getter
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
