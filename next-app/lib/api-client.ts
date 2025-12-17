/**
 * API Client Utilities for React Query
 * 
 * This module provides type-safe fetch utilities optimized for use with React Query.
 * Features:
 * - Automatic token handling from cookies
 * - Type-safe error handling
 * - Request deduplication via React Query
 * - Configurable stale times to reduce duplicate fetches
 */

// API base URL - defaults to relative path for same-origin requests
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";

/**
 * Type-safe API error class
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: unknown
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Generic API fetch function with error handling
 * 
 * @param endpoint - API endpoint (e.g., "/api/jobs")
 * @param options - Fetch options
 * @returns Promise with typed response
 */
export async function apiFetch<T = unknown>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    // Handle non-OK responses
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.message || `Request failed: ${response.statusText}`,
        response.status,
        errorData
      );
    }

    // Parse JSON response
    const data = await response.json();
    return data;
  } catch (error) {
    // Re-throw ApiError as-is
    if (error instanceof ApiError) {
      throw error;
    }

    // Wrap network errors
    throw new ApiError(
      error instanceof Error ? error.message : "Network error",
      0
    );
  }
}

/**
 * GET request helper
 */
export const apiGet = <T = unknown>(endpoint: string) =>
  apiFetch<T>(endpoint, { method: "GET" });

/**
 * POST request helper
 */
export const apiPost = <T = unknown>(endpoint: string, data?: unknown) =>
  apiFetch<T>(endpoint, {
    method: "POST",
    body: JSON.stringify(data),
  });

/**
 * PUT request helper
 */
export const apiPut = <T = unknown>(endpoint: string, data?: unknown) =>
  apiFetch<T>(endpoint, {
    method: "PUT",
    body: JSON.stringify(data),
  });

/**
 * DELETE request helper
 */
export const apiDelete = <T = unknown>(endpoint: string) =>
  apiFetch<T>(endpoint, { method: "DELETE" });
