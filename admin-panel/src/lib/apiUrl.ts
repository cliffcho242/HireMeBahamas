/**
 * Safe URL Builder Utility - Admin Panel
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
 * import { apiUrl } from './lib/apiUrl';
 * 
 * fetch(apiUrl("/admin/users"), {
 *   credentials: "include",
 * });
 * ```
 */

import { isValidUrl, isSecureUrl } from './safeUrl';

/**
 * Validate and get the base API URL from environment
 * @throws Error if VITE_API_URL is missing or invalid
 */
function validateAndGetBaseUrl(): string {
  const base = import.meta.env.VITE_API_URL as string | undefined;

  // If no explicit API URL is set, use same-origin (for Vercel serverless)
  if (!base) {
    // Check if we're in a browser environment
    if (typeof window !== 'undefined') {
      return window.location.origin;
    }
    
    // If not in browser and no URL is set, throw an error
    throw new Error(
      "VITE_API_URL is missing or invalid. " +
      "Set VITE_API_URL environment variable to your backend URL, " +
      "or deploy to a serverless environment where same-origin is used."
    );
  }

  // Use our safe URL validator instead of manual checks
  if (!isValidUrl(base)) {
    throw new Error(
      `VITE_API_URL is invalid: "${base}". ` +
      "URL must start with 'http://' or 'https://'. " +
      "Example: VITE_API_URL=https://your-backend.com"
    );
  }

  // Validate HTTPS in production
  if (!isSecureUrl(base)) {
    throw new Error(
      `VITE_API_URL must use HTTPS in production: "${base}". ` +
      "HTTP is only allowed for localhost in development. " +
      "Change to: VITE_API_URL=https://your-domain.com"
    );
  }

  return base;
}

/**
 * Build a complete API URL from a path
 * 
 * @param path - The API path (e.g., "/admin/users")
 * @returns The complete URL with base URL prepended
 * @throws Error if VITE_API_URL is missing or invalid
 * 
 * @example
 * ```typescript
 * apiUrl("/admin/users") 
 * // Returns: "https://your-backend.com/admin/users"
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
