/**
 * Retry Utility with Network Error Handling
 * 
 * Provides intelligent retry logic with user-friendly messaging for operations
 * that may fail due to temporary network issues or server connectivity problems.
 * 
 * Note: This retry logic is at the application layer (login/register operations)
 * and works in conjunction with the axios interceptor retry logic in api.ts.
 * The axios layer handles network-level retries, while this handles operation-level
 * retries with user-friendly messaging.
 */

import { debugLog } from './debugLogger';

export interface RetryOptions {
  maxRetries?: number;
  baseDelay?: number;
  maxDelay?: number;
  backoffIncrement?: number;
  onRetry?: (attempt: number, error: unknown) => void;
  shouldRetry?: (error: unknown) => boolean;
}

export interface ApiErrorType {
  response?: { status?: number; data?: unknown };
  code?: string;
  message?: string;
}

/**
 * Type guard to check if error is API-like
 */
function isApiError(error: unknown): error is ApiErrorType {
  return (
    typeof error === 'object' &&
    error !== null &&
    ('response' in error || 'code' in error || 'message' in error)
  );
}

/**
 * Check if an error indicates a temporary server unavailability or network issue
 */
function isTemporaryError(error: unknown): boolean {
  if (!isApiError(error)) {
    return false;
  }
  
  // Check for common temporary error indicators
  const isTemporary = 
    // Server unavailable
    error.response?.status === 503 ||
    // Bad gateway
    error.response?.status === 502 ||
    // Gateway timeout
    error.response?.status === 504 ||
    // Connection refused
    error.code === 'ECONNREFUSED' ||
    // Timeout
    (error.code === 'ECONNABORTED' && error.message?.includes('timeout')) ||
    // Network error
    error.code === 'ERR_NETWORK';
    
  return isTemporary;
}

/**
 * Check if error message or response indicates a temporary connection issue
 */
function hasTemporaryErrorMessage(error: unknown): boolean {
  if (!isApiError(error)) {
    return false;
  }
  
  const message = error.message?.toLowerCase() || '';
  
  // Safely check response data with type guard
  let responseMessage = '';
  if (error.response?.data && typeof error.response.data === 'object') {
    const data = error.response.data as Record<string, unknown>;
    if (typeof data.message === 'string') {
      responseMessage = data.message.toLowerCase();
    } else if (typeof data.detail === 'string') {
      responseMessage = data.detail.toLowerCase();
    }
  }
  
  return (
    message.includes('timeout') ||
    message.includes('connection') ||
    message.includes('network') ||
    responseMessage.includes('timeout') ||
    responseMessage.includes('connection') ||
    responseMessage.includes('network')
  );
}

/**
 * Retry a promise-based operation with exponential backoff
 * 
 * @param operation - The async operation to retry
 * @param options - Retry configuration options
 * @returns Promise that resolves with the operation result or rejects after max retries
 * 
 * @example
 * ```typescript
 * const result = await retryWithBackoff(
 *   async () => await authAPI.login({ email, password }),
 *   {
 *     maxRetries: 3,
 *     onRetry: (attempt, error) => {
 *       console.log(`Retry attempt ${attempt} after error:`, error);
 *     }
 *   }
 * );
 * ```
 */
export async function retryWithBackoff<T>(
  operation: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const {
    maxRetries = 3,
    baseDelay = 3000,      // 3 seconds base delay (backend is always on)
    maxDelay = 10000,      // 10 seconds maximum
    backoffIncrement = 2000, // 2 seconds increment per retry
    onRetry,
    shouldRetry,
  } = options;

  let lastError: unknown;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      // Try to execute the operation
      return await operation();
    } catch (error) {
      lastError = error;
      
      // Check if this is the last attempt
      const isLastAttempt = attempt === maxRetries;
      
      if (isLastAttempt) {
        // No more retries, throw the error
        throw error;
      }

      // Determine if we should retry this error
      const isTemporary = isTemporaryError(error) || hasTemporaryErrorMessage(error);
      const customShouldRetry = shouldRetry ? shouldRetry(error) : true;
      
      if (!isTemporary && !customShouldRetry) {
        // Not a temporary error and custom logic says don't retry
        throw error;
      }

      // Calculate delay with linear backoff (avoids compounding with axios retries)
      // For temporary errors: 3s, 5s, 7s, 9s (capped at maxDelay)
      const delay = Math.min(baseDelay + (attempt * backoffIncrement), maxDelay);
      
      // Notify about retry
      if (onRetry) {
        onRetry(attempt + 1, error);
      }

      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  // This should never be reached, but TypeScript needs it
  throw lastError;
}

/**
 * Specialized retry wrapper for login operations with user-friendly messaging
 * 
 * @param credentials - Login credentials
 * @param loginFn - The login function to call
 * @param onProgress - Callback for progress updates
 * @returns Promise that resolves with login response
 * 
 * @example
 * ```typescript
 * const result = await loginWithRetry(
 *   { email: 'user@example.com', password: 'pass123' },
 *   (creds) => authAPI.login(creds),
 *   (message) => {
 *     console.log('Login progress:', message);
 *     toast.loading(message);
 *   }
 * );
 * ```
 */
export async function loginWithRetry<T>(
  credentials: { email: string; password: string },
  loginFn: (credentials: { email: string; password: string }) => Promise<T>,
  onProgress?: (message: string, attempt: number) => void
): Promise<T> {
  return retryWithBackoff(
    () => loginFn(credentials),
    {
      maxRetries: 3,
      baseDelay: 3000, // 3 seconds base delay
      onRetry: (attempt, error) => {
        const isTemporary = isTemporaryError(error) || hasTemporaryErrorMessage(error);
        
        let message: string;
        if (isTemporary) {
          message = `Connection issue detected. Retrying (attempt ${attempt + 1})...`;
        } else {
          message = `Request failed. Retrying (attempt ${attempt + 1})...`;
        }
        
        if (onProgress) {
          onProgress(message, attempt);
        }
        
        // Log for debugging
        debugLog.log(`[Login Retry ${attempt}]`, message, 'Error:', error);
      },
      shouldRetry: (error) => {
        if (!isApiError(error)) {
          return true;
        }
        
        // Don't retry on authentication failures (wrong credentials)
        if (error.response?.status === 401) {
          return false;
        }
        
        // Don't retry on rate limiting
        if (error.response?.status === 429) {
          return false;
        }
        
        // Don't retry on validation errors
        if (error.response?.status === 422 || error.response?.status === 400) {
          return false;
        }
        
        // Retry everything else (network errors, server errors)
        return true;
      }
    }
  );
}

/**
 * Specialized retry wrapper for registration operations
 * 
 * @param userData - Registration data
 * @param registerFn - The registration function to call
 * @param onProgress - Callback for progress updates
 * @returns Promise that resolves with registration response
 */
export async function registerWithRetry<T, D = unknown>(
  userData: D,
  registerFn: (userData: D) => Promise<T>,
  onProgress?: (message: string, attempt: number) => void
): Promise<T> {
  return retryWithBackoff(
    () => registerFn(userData),
    {
      maxRetries: 3,
      baseDelay: 3000, // 3 seconds base delay
      onRetry: (attempt, error) => {
        const isTemporary = isTemporaryError(error) || hasTemporaryErrorMessage(error);
        
        let message: string;
        if (isTemporary) {
          message = `Connection issue detected. Retrying (attempt ${attempt + 1})...`;
        } else {
          message = `Retrying registration... Attempt ${attempt + 1}`;
        }
        
        if (onProgress) {
          onProgress(message, attempt);
        }
      },
      shouldRetry: (error) => {
        if (!isApiError(error)) {
          return true;
        }
        
        // Don't retry on validation errors (bad input)
        if (error.response?.status === 422 || error.response?.status === 400) {
          return false;
        }
        
        // Don't retry on conflicts (email already exists)
        if (error.response?.status === 409) {
          return false;
        }
        
        // Don't retry on rate limiting
        if (error.response?.status === 429) {
          return false;
        }
        
        // Retry network errors and temporary server issues
        return true;
      }
    }
  );
}
