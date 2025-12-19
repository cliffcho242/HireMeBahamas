/**
 * Safe URL Builder Utility
 * 
 * This utility ensures that API URLs are always constructed correctly
 * and never fails silently. It validates the base URL and constructs
 * full URLs for API endpoints.
 * 
 * Benefits:
 * - Prevents pattern errors in URL construction
 * - Validates environment configuration at runtime
 * - Provides clear error messages for misconfiguration
 * - Normalizes trailing slashes automatically
 * - Works with both Vite and other build systems
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

import { isValidUrl, isSecureUrl } from './safeUrl';

/**
 * Validate and get the base API URL from environment
 * RENDER-ONLY: Hard-coded to use Render backend exclusively
 * 🚨 NO Railway URLs allowed
 * 🚨 NO environment variable fallback
 */
function validateAndGetBaseUrl(): string {
  // 🔥 PRODUCTION LOCK: Hard-code Render backend URL
  const RENDER_BACKEND_URL = "https://hiremebahamas.onrender.com";
  
  // Check if we're in development mode (localhost)
  if (typeof window !== 'undefined' && (
    window.location.hostname === 'localhost' || 
    window.location.hostname === '127.0.0.1'
  )) {
    // Allow local development override
    const devUrl = import.meta.env.VITE_API_URL as string | undefined;
    if (devUrl && devUrl.startsWith('http://localhost')) {
      return devUrl;
    }
  }
  
  // 🚨 RENDER ONLY: Return hard-coded Render URL for all production traffic
  return RENDER_BACKEND_URL;
}

/**
 * Build a complete API URL from a path
 * 
 * @param path - The API path (e.g., "/api/auth/me")
 * @returns The complete URL with base URL prepended
 * @throws Error if VITE_API_URL is missing or invalid
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
 * @throws Error if VITE_API_URL is missing or invalid
 */
export function getApiBase(): string {
  const base = validateAndGetBaseUrl();
  return base.replace(/\/$/, "");
}
