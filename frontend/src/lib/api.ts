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

// URL validation imports removed - validation happens in safeUrl module
// Import only when needed to avoid unused imports

const DEFAULT_RENDER_BACKEND_URL = "https://hiremebahamas-backend.onrender.com";

/**
 * Validate and get the base API URL from environment
 * Prefers VITE_API_BASE_URL, falls back to VITE_API_URL, then same-origin, then Render default
 */
function validateAndGetBaseUrl(): string {
  // Step 1: Try VITE_API_BASE_URL first, then VITE_API_URL
  const envUrl = (import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL) as string | undefined;
  
  if (envUrl) {
    const trimmedUrl = envUrl.trim();
    
    // Validate scheme: must start with http:// or https://
    if (!trimmedUrl.startsWith('http://') && !trimmedUrl.startsWith('https://')) {
      throw new Error(
        `Invalid API URL: "${trimmedUrl}". ` +
        "URL must start with 'http://' or 'https://'. " +
        "Example: VITE_API_BASE_URL=https://your-backend.com"
      );
    }
    
    // Extract hostname for validation
    let hostname: string;
    try {
      hostname = new URL(trimmedUrl).hostname.toLowerCase();
    } catch {
      throw new Error(`Failed to parse API URL: "${trimmedUrl}"`);
    }
    
    // Check if localhost
    const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '0.0.0.0';
    
    // Enforce HTTPS in production unless localhost
    if (!isLocalhost && trimmedUrl.startsWith('http://')) {
      throw new Error(
        `API URL must use HTTPS in production: "${trimmedUrl}". ` +
        "HTTP is only allowed for localhost in development. " +
        "Change to: VITE_API_BASE_URL=https://your-domain.com"
      );
    }
    
    // Remove trailing slash and return
    return trimmedUrl.replace(/\/$/, "");
  }
  
  // Step 2: No env variable set - use same-origin fallback in browser (Vercel proxy)
  if (typeof window !== 'undefined') {
    return window.location.origin;
  }
  
  // Step 3: Final fallback to Render default (server-side rendering or build time)
  return DEFAULT_RENDER_BACKEND_URL;
}

/**
 * Build a complete API URL from a path
 * 
 * @param path - The API path (e.g., "/api/auth/me")
 * @returns The complete URL with base URL prepended
 * @throws Error if URL validation fails
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
 * @throws Error if URL validation fails
 */
export function getApiBase(): string {
  const base = validateAndGetBaseUrl();
  return base.replace(/\/$/, "");
}
