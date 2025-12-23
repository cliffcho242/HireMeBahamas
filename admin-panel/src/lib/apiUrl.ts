/**
 * FINAL, LOCKED, PRODUCTION API HANDLER
 * - iOS Safari safe
 * - Chrome safe
 * - No double slashes
 * - No silent failures
 */

export function getApiBaseUrl(): string {
  const prod = import.meta.env.VITE_API_BASE_URL?.trim();
  const dev = import.meta.env.VITE_API_URL?.trim();

  const normalize = (url: string) => url.replace(/\/+$/, "");

  if (dev && dev.startsWith("http://localhost")) return normalize(dev);
  if (prod && prod.startsWith("https://")) return normalize(prod);

  return "";
}

export function apiUrl(path: string): string {
  if (!path.startsWith("/")) path = "/" + path;
  return `${getApiBaseUrl()}${path}`;
}

// Alias export to mirror the frontend package (`getApiBase`) so shared imports keep working
export const getApiBase = getApiBaseUrl;

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = apiUrl(path);

  try {
    const res = await fetch(url, {
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
      ...options,
    });

    if (!res.ok) {
      const text = await res.text();
      console.error("API ERROR", res.status, text);
      throw new Error(`API ${res.status}`);
    }

    return res.json();
  } catch (err) {
    console.error("NETWORK FAILURE", err);
    throw err;
  }
}
