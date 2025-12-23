/**
 * PRODUCTION-SAFE API CONFIG
 * - Never throws during app boot to prevent white screens
 * - Logs warnings for missing configuration
 * - Falls back to build-time injected __API_BASE__ or default URL
 * - Wrapped in try-catch to ensure env issues never crash rendering
 */

// Import the safe fallback URL
import { DEFAULT_API_BASE_URL } from './env';

export function getApiBase(): string {
  try {
    const localOverride = import.meta.env.VITE_API_URL;
    const raw = localOverride || import.meta.env.VITE_API_BASE_URL;

    if (!raw) {
      // Try build-time injected global
      try {
        const buildTimeUrl = (typeof window !== 'undefined' && (window as any).__API_BASE__) || 
                             (typeof __API_BASE__ !== 'undefined' ? __API_BASE__ : undefined);
        if (buildTimeUrl) {
          return buildTimeUrl.replace(/\/+$/, "");
        }
      } catch {
        // Ignore errors accessing __API_BASE__
      }
      
      console.warn("⚠️ VITE_API_BASE_URL missing - using default fallback");
      return DEFAULT_API_BASE_URL;
    }

    // Allow http only when using a local override outside production builds
    const requiresHttps = import.meta.env.PROD || !localOverride;
    if (requiresHttps && !raw.startsWith("https://")) {
      console.warn("⚠️ VITE_API_BASE_URL should be HTTPS in production");
      // Don't throw - let the app render and show appropriate error UI
    }

    return raw.replace(/\/+$/, "");
  } catch {
    // If anything fails during API base URL processing, return default fallback
    return DEFAULT_API_BASE_URL;
  }
}

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
