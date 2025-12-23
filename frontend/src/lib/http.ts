/**
 * HTTP Client Module
 * 
 * Robust API client that:
 * - Never throws on network errors silently (errors bubble to ErrorBoundary)
 * - Automatically adds Authorization header from token storage
 * - Logs errors with context for debugging
 * - Safe for mobile environments
 */

import { getApiBase } from "./api";
import { getToken } from "./token";

/**
 * Make an authenticated API fetch request.
 * 
 * This is a complementary function to the existing apiFetch in api.ts.
 * Use this when you need automatic token injection from the token module.
 * 
 * Features:
 * - Automatically retrieves and applies auth token
 * - Handles network errors gracefully
 * - Parses JSON responses
 * - Throws structured errors for UI handling
 * 
 * @param path - API endpoint path (e.g., "/api/users/me")
 * @param options - Standard fetch RequestInit options
 * @returns Parsed JSON response
 * @throws Error with status and message for failed requests
 */
export async function authenticatedFetch<T = unknown>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const base = getApiBase();
  const token = getToken();

  // Build full URL
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const url = base ? `${base}${normalizedPath}` : normalizedPath;

  // Build headers - only set Content-Type for requests with JSON body
  const headers: Record<string, string> = {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
  
  // Only add Content-Type: application/json when body is present and is a string (JSON)
  if (options.body && typeof options.body === "string") {
    headers["Content-Type"] = "application/json";
  }

  try {
    const res = await fetch(url, {
      ...options,
      credentials: "include", // Include cookies for Safari support
      headers: {
        ...headers,
        ...options.headers,
      },
    });

    if (!res.ok) {
      const text = await res.text();
      const error = new Error(`${res.status}: ${text}`);
      (error as unknown as { status: number }).status = res.status;
      throw error;
    }

    // Handle empty responses
    const contentType = res.headers.get("content-type");
    if (contentType && contentType.includes("application/json")) {
      return res.json();
    }

    // Return text for non-JSON responses
    return (await res.text()) as unknown as T;
  } catch (err) {
    // Log the error for debugging
    console.error("🌐 API error:", err);
    
    // Re-throw so ErrorBoundary or caller can handle it
    throw err;
  }
}

/**
 * Convenience methods for common HTTP verbs
 */
export const http = {
  /**
   * Make a GET request
   */
  get: <T = unknown>(path: string, options?: RequestInit) =>
    authenticatedFetch<T>(path, { ...options, method: "GET" }),

  /**
   * Make a POST request with JSON body
   */
  post: <T = unknown>(path: string, body?: unknown, options?: RequestInit) =>
    authenticatedFetch<T>(path, {
      ...options,
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    }),

  /**
   * Make a PUT request with JSON body
   */
  put: <T = unknown>(path: string, body?: unknown, options?: RequestInit) =>
    authenticatedFetch<T>(path, {
      ...options,
      method: "PUT",
      body: body ? JSON.stringify(body) : undefined,
    }),

  /**
   * Make a PATCH request with JSON body
   */
  patch: <T = unknown>(path: string, body?: unknown, options?: RequestInit) =>
    authenticatedFetch<T>(path, {
      ...options,
      method: "PATCH",
      body: body ? JSON.stringify(body) : undefined,
    }),

  /**
   * Make a DELETE request
   */
  delete: <T = unknown>(path: string, options?: RequestInit) =>
    authenticatedFetch<T>(path, { ...options, method: "DELETE" }),
};
