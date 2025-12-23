/**
 * Token Storage Module
 * 
 * Mobile-safe and bulletproof token storage that handles:
 * - iOS Safari
 * - Android WebView
 * - PWA
 * - Private/incognito mode
 * 
 * NEVER reads localStorage at import time - prevents crash on boot.
 */

const KEY = "hm_auth_token";

/**
 * Safely get the authentication token from localStorage.
 * 
 * @returns The token string or null if not available or on error
 */
export function getToken(): string | null {
  // Guard against SSR/non-browser environments
  if (typeof window === "undefined") return null;
  
  try {
    return localStorage.getItem(KEY);
  } catch {
    // localStorage not available (private mode, storage quota, etc.)
    return null;
  }
}

/**
 * Safely set the authentication token in localStorage.
 * 
 * @param token - The token string to store
 */
export function setToken(token: string): void {
  // Guard against SSR/non-browser environments
  if (typeof window === "undefined") return;
  
  try {
    localStorage.setItem(KEY, token);
  } catch {
    // localStorage not available - silently fail
    // This can happen in private mode or when storage quota is exceeded
    console.warn("⚠️ Could not save token to localStorage");
  }
}

/**
 * Safely remove the authentication token from localStorage.
 */
export function clearToken(): void {
  // Guard against SSR/non-browser environments
  if (typeof window === "undefined") return;
  
  try {
    localStorage.removeItem(KEY);
  } catch {
    // localStorage not available - silently fail
    console.warn("⚠️ Could not clear token from localStorage");
  }
}
