/**
 * Utility functions for handling API errors consistently across the application.
 */

/**
 * Type for API errors that may contain response status codes
 */
export interface ApiErrorResponse {
  response?: { 
    status?: number;
    data?: {
      detail?: string;
      message?: string;
    };
  }; 
  message?: string;
}

/**
 * Get a user-friendly error message based on the error response.
 * Prioritizes specific error messages from the API, then falls back to status code messages.
 * 
 * @param error - The error object from the API call
 * @param resourceType - The type of resource being accessed (e.g., 'followers', 'comments')
 * @param defaultMessage - Fallback message if error type cannot be determined
 * @returns A user-friendly error message
 */
export function getApiErrorMessage(
  error: unknown, 
  resourceType: string, 
  defaultMessage?: string
): string {
  const apiError = error as ApiErrorResponse;
  
  // First, check for specific error messages from the API response
  // These are more helpful than generic status code messages
  if (apiError.response?.data?.detail) {
    return apiError.response.data.detail;
  }
  
  if (apiError.response?.data?.message) {
    return apiError.response.data.message;
  }
  
  // Fall back to status code-based messages if no specific message is available
  if (apiError.response?.status === 401) {
    return `Please log in to view ${resourceType}`;
  }
  
  if (apiError.response?.status === 404) {
    // For followers/following, a 404 likely means the user doesn't exist
    // Not that the list is empty (empty lists return 200 with an empty array)
    if (resourceType === 'followers' || resourceType === 'following') {
      return 'User not found';
    }
    return `The requested ${resourceType} could not be found`;
  }
  
  if (apiError.response?.status === 403) {
    return `You don't have permission to view ${resourceType}`;
  }
  
  if (apiError.response?.status === 500) {
    return 'Server error. Please try again later.';
  }
  
  // Use default message or a generic retry message
  return defaultMessage || `Failed to load ${resourceType}. Click again to retry.`;
}

/**
 * Safely parse an ID value to ensure it's a valid positive integer.
 * Works with both string and number inputs.
 * 
 * @param id - The ID value to parse (string or number)
 * @returns A valid positive integer, or null if parsing fails
 */
export function parseUserId(id: string | number | undefined | null): number | null {
  if (id === undefined || id === null) {
    return null;
  }
  
  // If already a number, validate it's a positive integer
  if (typeof id === 'number') {
    if (!Number.isFinite(id) || id <= 0 || !Number.isInteger(id)) {
      return null;
    }
    return id;
  }
  
  // Parse string to integer
  const trimmed = id.trim();
  if (!trimmed || !/^\d+$/.test(trimmed)) {
    return null;
  }
  
  const parsed = parseInt(trimmed, 10);
  if (!Number.isFinite(parsed) || parsed <= 0 || parsed > Number.MAX_SAFE_INTEGER) {
    return null;
  }
  
  return parsed;
}
