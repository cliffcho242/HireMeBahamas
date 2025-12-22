/**
 * FINAL production-safe API base URL resolver
 * - iOS safe
 * - No double slashes
 * - Dev + prod compatible
 */
export function getApiBaseUrl(): string {
  const prod = import.meta.env.VITE_API_BASE_URL?.trim();
  const dev = import.meta.env.VITE_API_URL?.trim();

  const normalize = (url: string) => url.replace(/\/+$/, "");

  // Local dev override
  if (dev && dev.startsWith("http://localhost")) {
    return normalize(dev);
  }

  // Production
  if (prod && prod.startsWith("https://")) {
    return normalize(prod);
  }

  // Same-origin fallback (Vercel proxy safety)
  return "";
}

export function apiUrl(path: string): string {
  if (!path.startsWith("/")) path = "/" + path;
  return `${getApiBaseUrl()}${path}`;
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = apiUrl(path);

  try {
    const res = await fetch(url, {
      credentials: "include",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
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

// Backward compatibility aliases
export const buildApiUrl = apiUrl;
export const getApiBase = getApiBaseUrl;
