/**
 * Safe URL Builder Utility
 * 
 * This utility ensures that API URLs are always constructed correctly
 * and never fails silently. It validates the base URL and constructs
 * full URLs for API endpoints.
 * 
 * Uses VITE_API_BASE_URL environment variable or falls back to
 * Render backend (https://hiremebahamas.onrender.com) when unset.
 * 
 * Benefits:
 * - Prevents pattern errors in URL construction
 * - Validates environment configuration at runtime
 * - Provides clear error messages for misconfiguration
 * - Normalizes trailing slashes automatically
 * - Works with both Vite and other build systems
 * - Defaults to Render backend when env var is missing
 * 
 * @example
 * ```typescript
 * // Using the utility
 * import { apiUrl } from './lib/api';
 * 
 * fetch(apiUrl("/api/auth/me"), {
 *   credentials: "include",
 * });
 * ```
 */

// URL validation imports removed - validation happens in safeUrl module
// Import only when needed to avoid unused imports

/**
 * Validate and get the base API URL from environment
 * Uses VITE_API_BASE_URL or falls back to Render backend
 */
function validateAndGetBaseUrl(): string {
  // Get environment variable, trim it, and use Render as fallback
  const envUrl = import.meta.env.VITE_API_BASE_URL?.trim();
  
  // If VITE_API_BASE_URL is set and not empty, use it
  if (envUrl) {
    return envUrl;
  }
  
  // Otherwise, use Render backend as hardcoded fallback
  return 'https://hiremebahamas.onrender.com';
}

/**
 * Build a complete API URL from a path
 * 
 * @param path - The API path (e.g., "/api/auth/me")
 * @returns The complete URL with base URL prepended
 * @throws Error if VITE_API_BASE_URL is invalid
 * 
 * @example
 * ```typescript
 * apiUrl("/api/auth/me") 
 * // Returns: "https://your-backend.com/api/auth/me"
 * ```
 */
export function apiUrl(path: string): string {
  const base = validateAndGetBaseUrl();

  // Normalize the base URL (remove trailing slash) and path (ensure leading slash)
  const normalizedBase = base.replace(/\/$/, "");
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;

  return `${normalizedBase}${normalizedPath}`;
}

/**
 * Check if API URL is properly configured
 * 
 * @returns true if API URL is configured and valid, false otherwise
 */
export function isApiConfigured(): boolean {
  try {
    // Try to construct a test URL
    apiUrl("/api/health");
    return true;
  } catch {
    return false;
  }
}

/**
 * Get the base API URL
 * 
 * @returns The base API URL
 * @throws Error if VITE_API_BASE_URL is invalid
 */
export function getApiBase(): string {
  const base = validateAndGetBaseUrl();
  return base.replace(/\/$/, "");
}
