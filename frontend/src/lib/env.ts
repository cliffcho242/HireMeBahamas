/**
 * Safe VITE_API_BASE_URL Getter
 * 
 * This module provides a production-safe way to access the API base URL.
 * It guarantees builds never fail even if the environment variable is missing.
 * 
 * Features:
 * ✅ Never throws or blocks rendering
 * ✅ Logs warnings for missing configuration
 * ✅ Falls back to build-time injected __API_BASE__ (set in vite.config.ts)
 * ✅ Prevents white screen on missing env vars
 * 
 * Fallback order:
 * 1. Runtime env: import.meta.env.VITE_API_BASE_URL
 * 2. Build-time global: window.__API_BASE__ or __API_BASE__
 * 3. Default: "https://hiremebahamas-backend.onrender.com"
 */

/**
 * Default fallback API base URL for production
 * Used when both VITE_API_BASE_URL and __API_BASE__ are not available
 */
export const DEFAULT_API_BASE_URL = "https://hiremebahamas-backend.onrender.com";

/**
 * Helper function to safely access __API_BASE__ global
 * Returns undefined if not available
 */
function getBuildTimeApiBase(): string | undefined {
  try {
    // Check window object (for runtime in browser)
    if (typeof window !== 'undefined' && (window as any).__API_BASE__) {
      return (window as any).__API_BASE__;
    }
    
    // Check global variable (for module evaluation time)
    if (typeof __API_BASE__ !== 'undefined') {
      return __API_BASE__;
    }
  } catch {
    // Ignore errors accessing __API_BASE__
  }
  
  return undefined;
}

export function getApiBase(): string {
  // Try runtime environment variable first
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  
  if (envUrl && envUrl.trim() !== "") {
    return envUrl.replace(/\/+$/, "");
  }

  // Try build-time injected global (from vite.config.ts define)
  const buildTimeUrl = getBuildTimeApiBase();
  if (buildTimeUrl && buildTimeUrl.trim() !== "") {
    return buildTimeUrl.replace(/\/+$/, "");
  }

  // Final fallback
  console.warn(
    "⚠️ VITE_API_BASE_URL is missing. Falling back to default:",
    DEFAULT_API_BASE_URL
  );
  return DEFAULT_API_BASE_URL;
}

/**
 * Get API base URL with safe fallback
 * Use this instead of directly accessing import.meta.env.VITE_API_BASE_URL
 */
export const API_BASE_URL = getApiBase();
