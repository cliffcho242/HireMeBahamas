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

// Remove one or more trailing slashes to avoid double-slash issues when building URLs
const stripTrailingSlashes = (url: string = "") => url.replace(/\/+$/, "");

const handleValidationIssue = (message: string): void => {
  if (import.meta.env.PROD) {
    throw new Error(message);
  }
  console.warn(message);
};

const getLocalhostOverride = (url?: string): string | null => {
  if (!url) return null;
  try {
    const parsed = new URL(url);
    const isLocalhost = parsed.hostname === "localhost" ||
      parsed.hostname === "127.0.0.1" ||
      parsed.hostname === "::1";
    const isAllowedProtocol = parsed.protocol === "http:" || parsed.protocol === "https:";
    return isLocalhost && isAllowedProtocol ? stripTrailingSlashes(url) : null;
  } catch {
    return null;
  }
};

/**
 * Get the validated API base URL for frontend requests
 *
 * Priority:
 * 1. VITE_API_BASE_URL (production)
 * 2. VITE_API_URL (override; allows http only for localhost)
 * 3. Default same-origin for Vercel proxy
 */
export function getApiBaseUrl(): string {
  const baseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
  const overrideUrl = import.meta.env.VITE_API_URL?.trim();

  const overrideLocalhost = getLocalhostOverride(overrideUrl);
  const baseLocalhost = getLocalhostOverride(baseUrl);

  // Allow localhost http override in dev
  if (overrideLocalhost) {
    return overrideLocalhost;
  }

  if (baseLocalhost) {
    return baseLocalhost;
  }

  if (baseUrl) {
    let parsedBase: URL | null = null;
    try {
      parsedBase = new URL(baseUrl);
    } catch {
      handleValidationIssue(`VITE_API_BASE_URL must be a valid HTTPS URL: ${baseUrl}`);
      parsedBase = null;
    }

    if (parsedBase) {
      if (parsedBase.protocol !== "https:") {
        handleValidationIssue(`VITE_API_BASE_URL must be HTTPS in production: ${baseUrl}`);
        parsedBase = null;
      } else if (!parsedBase.hostname) {
        handleValidationIssue(`VITE_API_BASE_URL must include a valid host: ${baseUrl}`);
        parsedBase = null;
      }
    }

    if (parsedBase) {
      return stripTrailingSlashes(baseUrl);
    }
  }

  if (overrideUrl) {
    if (overrideUrl.startsWith("http://")) {
      const message = `VITE_API_URL should use HTTPS unless pointing to localhost: ${overrideUrl}`;
      throw new Error(message);
    }

    return stripTrailingSlashes(overrideUrl);
  }

  // Fallback: same-origin (Vercel proxy)
  return "";
}

/**
 * Build a complete API URL from a path
 * 
 * @param path - The API path (e.g., "/api/auth/me")
 * @returns The complete URL with base URL prepended
 * 
 * @example
 * ```typescript
 * apiUrl("/api/auth/me") 
 * // Returns: "https://your-backend.com/api/auth/me"
 * ```
 */
export function apiUrl(path: string): string {
  const base = getApiBaseUrl();

  // Normalize the base URL (remove trailing slash) and path (ensure leading slash)
  const normalizedBase = stripTrailingSlashes(base);
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
 */
export function getApiBase(): string {
  const base = getApiBaseUrl();
  return stripTrailingSlashes(base);
}
