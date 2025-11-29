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
 * Provides context-specific messages for common error codes.
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
  
  // Check for specific HTTP status codes
  if (apiError.response?.status === 401) {
    return `Please log in to view ${resourceType}`;
  }
  
  if (apiError.response?.status === 404) {
    return 'Resource not found';
  }
  
  if (apiError.response?.status === 403) {
    return `You don't have permission to view ${resourceType}`;
  }
  
  if (apiError.response?.status === 500) {
    return 'Server error. Please try again later.';
  }
  
  // Check for error message in response data
  if (apiError.response?.data?.detail) {
    return apiError.response.data.detail;
  }
  
  if (apiError.response?.data?.message) {
    return apiError.response.data.message;
  }
  
  // Use default message or a generic retry message
  return defaultMessage || `Failed to load ${resourceType}. Click again to retry.`;
}
