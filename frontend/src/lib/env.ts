/**
 * Safe VITE_API_BASE_URL Getter
 * 
 * This module provides a production-safe way to access the API base URL.
 * It guarantees builds never fail even if the environment variable is missing.
 * 
 * Features:
 * ✅ Never throws or blocks rendering
 * ✅ Logs warnings for missing configuration
 * ✅ Falls back to default Render backend
 * ✅ Prevents white screen on missing env vars
 */

/**
 * Default fallback API base URL for production
 * Used when VITE_API_BASE_URL is not set
 */
export const DEFAULT_API_BASE_URL = "https://hiremebahamas-backend.onrender.com";

export function getApiBase(): string {
  const url = import.meta.env.VITE_API_BASE_URL;

  if (!url || url.trim() === "") {
    console.warn(
      "⚠️ VITE_API_BASE_URL is missing. Falling back to default."
    );
    return DEFAULT_API_BASE_URL;
  }

  return url.replace(/\/+$/, "");
}

/**
 * Get API base URL with safe fallback
 * Use this instead of directly accessing import.meta.env.VITE_API_BASE_URL
 */
export const API_BASE_URL = getApiBase();
