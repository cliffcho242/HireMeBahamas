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
 * User-friendly messages for different resource types
 */
const RESOURCE_MESSAGES: Record<string, { empty: string; notFound: string }> = {
  followers: {
    empty: 'This user has no followers yet',
    notFound: 'Could not load followers. The user may not exist.',
  },
  following: {
    empty: 'This user is not following anyone yet',
    notFound: 'Could not load following list. The user may not exist.',
  },
};

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
  
  // Check for client-side validation errors first
  if (apiError.message === 'Invalid user ID') {
    return 'Invalid user profile. Please try a different user.';
  }
  
  // First, check for specific error messages from the API response
  // These are more helpful than generic status code messages
  if (apiError.response?.data?.detail) {
    return apiError.response.data.detail;
  }
  
  if (apiError.response?.data?.message) {
    return apiError.response.data.message;
  }
  
  // Get resource-specific messages if available
  const resourceMessages = RESOURCE_MESSAGES[resourceType];
  
  // Fall back to status code-based messages if no specific message is available
  if (apiError.response?.status === 401) {
    return `Please log in to view ${resourceType}`;
  }
  
  if (apiError.response?.status === 404) {
    // Use resource-specific message if available
    return resourceMessages?.notFound || `User not found`;
  }
  
  if (apiError.response?.status === 400) {
    return 'Invalid request. Please try again.';
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
