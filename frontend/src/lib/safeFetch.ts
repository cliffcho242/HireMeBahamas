/**
 * Safe Fetch Wrapper
 * 
 * This module provides a production-safe fetch wrapper that prevents
 * network/API errors from crashing the entire application.
 * 
 * Features:
 * ✅ Prevents fetch crashes from breaking the app
 * ✅ Returns degraded fallback on errors
 * ✅ Never causes white screen
 * ✅ Logs errors for debugging
 */

import { getApiBase } from "./env";

export interface SafeFetchError {
  error: true;
  message: string;
}

/**
 * Safe fetch wrapper that handles errors gracefully
 * 
 * @param endpoint - API endpoint (e.g., "/api/jobs" or "api/jobs")
 * @param options - Standard fetch options
 * @returns Promise with JSON response or error object
 */
export async function safeFetch(
  endpoint: string,
  options?: RequestInit
): Promise<any> {
  const url = `${getApiBase()}${endpoint.startsWith("/") ? "" : "/"}${endpoint}`;
  
  try {
    const res = await fetch(url, options);
    
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }
    
    return await res.json();
  } catch (err: any) {
    console.error("⚠️ Network/API error", err);
    
    // Return degraded fallback to avoid blank screen
    return {
      error: true,
      message: err.message
    } as SafeFetchError;
  }
}

/**
 * Type guard to check if response is an error
 */
export function isSafeFetchError(response: any): response is SafeFetchError {
  return response && response.error === true && typeof response.message === "string";
}
