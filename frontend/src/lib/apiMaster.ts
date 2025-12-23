/**
 * MASTER PLAYBOOK - Safe API URL Builder
 * 
 * Stack: React + Vite + TypeScript + Vercel
 * 
 * ABSOLUTE LAWS:
 * ✅ ALWAYS use VITE_* prefix (not NEXT_PUBLIC_*)
 * ✅ ALWAYS validate URL format
 * ✅ ALWAYS use fallback on misconfiguration (never throw during build)
 * ✅ NEVER fail silently (log warnings)
 */

// Import the safe API base URL from env.ts
import { API_BASE_URL } from './env';

/**
 * Safe API URL builder with strict validation
 * Uses fallback URL if VITE_API_BASE_URL is invalid or missing
 * Logs warnings instead of throwing to prevent build failures
 */
export function apiUrl(path: string): string {
  const base = API_BASE_URL;
  
  // Validate base URL exists (env.ts provides fallback)
  if (!base || !base.startsWith("https://")) {
    console.warn(
      "⚠️ API base URL is missing or invalid. API calls may fail.",
      { base, path }
    );
    // Return path as-is for relative URL fallback
    return path.startsWith("/") ? path : `/${path}`;
  }
  
  // Remove trailing slash from base, ensure leading slash on path
  const normalizedBase = base.replace(/\/$/, "");
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  
  return `${normalizedBase}${normalizedPath}`;
}


/**
 * Type-safe fetch wrapper with error handling
 * 
 * @example
 * const user = await apiFetch<User>("/api/auth/me");
 */
export async function apiFetch<T>(path: string): Promise<T> {
  const res = await fetch(apiUrl(path), { 
    credentials: "include" 
  });
  
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  
  return res.json();
}


/**
 * Query Error Boundary Example
 * 
 * Note: This is a placeholder. Real error boundaries require class components.
 * 
 * For production, use:
 * - react-error-boundary package
 * - Class component with componentDidCatch
 * - React Query's error handling with ErrorBoundary
 * 
 * @example
 * import { ErrorBoundary } from 'react-error-boundary';
 * 
 * <ErrorBoundary fallback={<ErrorFallback />}>
 *   <YourComponent />
 * </ErrorBoundary>
 */
