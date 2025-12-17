/**
 * 🔒 SAFE URL BUILDER - VERCEL FOREVER FIX
 * 
 * This utility provides a safe wrapper around URL construction that:
 * 1. Validates URLs before construction to prevent pattern errors
 * 2. Provides clear error messages for debugging
 * 3. Prevents silent failures in production
 * 4. Enforces HTTPS in production environments
 * 5. Handles undefined/null values gracefully
 * 
 * This prevents the dreaded error:
 * "The string did not match the expected pattern"
 * 
 * @example
 * ```typescript
 * // Instead of: new URL(someUrl)
 * // Use: safeParseUrl(someUrl)
 * 
 * const result = safeParseUrl(apiUrl);
 * if (result.success) {
 *   const urlObj = result.url;
 *   // Use urlObj safely
 * } else {
 *   console.error(result.error);
 *   // Handle error gracefully
 * }
 * ```
 */

export interface SafeUrlResult {
  success: boolean;
  url?: URL;
  error?: string;
}

/**
 * Validate URL protocol format
 * Checks if URL starts with http:// or https://
 * @internal Shared utility for validation
 */
export function hasValidProtocol(url: string): boolean {
  return url.startsWith('http://') || url.startsWith('https://');
}

/**
 * Check if hostname is localhost
 * @internal Shared utility for validation
 */
function isLocalhostHostname(hostname: string): boolean {
  return hostname === 'localhost' || 
         hostname === '127.0.0.1' ||
         hostname === '0.0.0.0';
}

/**
 * Safely parse a URL string into a URL object
 * 
 * @param urlString - The URL string to parse
 * @param context - Optional context for better error messages (e.g., "API request")
 * @returns SafeUrlResult with success flag and either url or error
 */
export function safeParseUrl(
  urlString: string | undefined | null,
  context?: string
): SafeUrlResult {
  const contextPrefix = context ? `[${context}] ` : '';

  // Check for undefined/null/empty
  if (!urlString || urlString.trim() === '') {
    return {
      success: false,
      error: `${contextPrefix}URL is undefined, null, or empty. Check your environment variables.`,
    };
  }

  // Validate URL format before attempting to parse
  const trimmedUrl = urlString.trim();
  
  // Check for basic URL structure
  if (!hasValidProtocol(trimmedUrl)) {
    return {
      success: false,
      error: `${contextPrefix}Invalid URL format: "${trimmedUrl}". URL must start with http:// or https://`,
    };
  }

  // In production, enforce HTTPS (allow http only for localhost)
  if (import.meta.env.PROD) {
    // Check protocol using string inspection to avoid new URL()
    const protocolMatch = trimmedUrl.match(/^(https?):\/\//);
    if (!protocolMatch) {
      return {
        success: false,
        error: `${contextPrefix}Invalid URL format: "${trimmedUrl}". URL must start with http:// or https://`,
      };
    }
    
    const protocol = protocolMatch[1];
    
    // Extract hostname without using new URL()
    const hostnameMatch = trimmedUrl.match(/^https?:\/\/([^/:?#]+)/);
    if (!hostnameMatch) {
      return {
        success: false,
        error: `${contextPrefix}Unable to extract hostname from URL: "${trimmedUrl}"`,
      };
    }
    
    const hostname = hostnameMatch[1];
    
    if (protocol === 'http' && !isLocalhostHostname(hostname)) {
      return {
        success: false,
        error: `${contextPrefix}Production URLs must use HTTPS. Found: ${trimmedUrl}`,
      };
    }
  }

  // Attempt to construct URL
  try {
    const url = new URL(trimmedUrl);
    return {
      success: true,
      url,
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    return {
      success: false,
      error: `${contextPrefix}Failed to parse URL "${trimmedUrl}": ${errorMessage}`,
    };
  }
}

/**
 * Safely parse a URL or throw a user-friendly error
 * Use this when you want to fail fast with a clear error message
 * 
 * @param urlString - The URL string to parse
 * @param context - Optional context for better error messages
 * @returns URL object
 * @throws Error with clear message if URL is invalid
 */
export function parseUrlOrThrow(
  urlString: string | undefined | null,
  context?: string
): URL {
  const result = safeParseUrl(urlString, context);
  
  if (!result.success) {
    throw new Error(result.error);
  }
  
  return result.url!;
}

/**
 * Check if a string is a valid URL
 * 
 * @param urlString - The string to check
 * @returns true if valid URL, false otherwise
 */
export function isValidUrl(urlString: string | undefined | null): boolean {
  return safeParseUrl(urlString).success;
}

/**
 * Validate that URL uses HTTPS in production (or is localhost)
 * 
 * @param urlString - The URL to validate
 * @returns true if valid for environment, false otherwise
 */
export function isSecureUrl(urlString: string | undefined | null): boolean {
  const result = safeParseUrl(urlString);
  
  if (!result.success) {
    return false;
  }

  const url = result.url!;
  
  // In production, only allow HTTPS or localhost
  if (import.meta.env.PROD) {
    return url.protocol === 'https:' || (url.protocol === 'http:' && isLocalhostHostname(url.hostname));
  }
  
  // In development, allow both HTTP and HTTPS
  return true;
}

/**
 * Normalize a URL by removing trailing slashes and extra spaces
 * 
 * @param urlString - The URL to normalize
 * @returns Normalized URL string or null if invalid
 */
export function normalizeUrl(urlString: string | undefined | null): string | null {
  const result = safeParseUrl(urlString);
  
  if (!result.success) {
    return null;
  }

  const url = result.url!;
  // Reconstruct URL to normalize it (removes trailing slashes from pathname)
  let normalized = `${url.protocol}//${url.host}${url.pathname}`;
  
  // Remove trailing slash from pathname unless it's just "/"
  if (url.pathname !== '/' && normalized.endsWith('/')) {
    normalized = normalized.slice(0, -1);
  }
  
  // Add search params if present
  if (url.search) {
    normalized += url.search;
  }
  
  return normalized;
}
