/**
 * Retry Utility with Cold Start Support
 * 
 * Provides intelligent retry logic with user-friendly messaging for operations
 * that may fail due to backend cold starts or temporary network issues.
 * 
 * Note: This retry logic is at the application layer (login/register operations)
 * and works in conjunction with the axios interceptor retry logic in api.ts.
 * The axios layer handles network-level retries, while this handles operation-level
 * retries with user-friendly messaging.
 */

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
 * Check if an error indicates a cold start or temporary server unavailability
 */
function isColdStartError(error: unknown): boolean {
  if (!isApiError(error)) {
    return false;
  }
  
  // Check for common cold start indicators
  const isColdStart = 
    // Server unavailable
    error.response?.status === 503 ||
    // Bad gateway (server starting)
    error.response?.status === 502 ||
    // Gateway timeout (server taking too long to start)
    error.response?.status === 504 ||
    // Connection refused
    error.code === 'ECONNREFUSED' ||
    // Timeout during startup
    (error.code === 'ECONNABORTED' && error.message?.includes('timeout')) ||
    // Network error during cold start
    error.code === 'ERR_NETWORK';
    
  return isColdStart;
}

/**
 * Check if error message or response indicates cold start
 */
function hasColdStartMessage(error: unknown): boolean {
  if (!isApiError(error)) {
    return false;
  }
  
  const message = error.message?.toLowerCase() || '';
  const responseData = error.response?.data as { message?: string; detail?: string } | undefined;
  const responseMessage = (responseData?.message || responseData?.detail || '').toLowerCase();
  
  return (
    message.includes('cold start') ||
    message.includes('starting up') ||
    message.includes('waking up') ||
    responseMessage.includes('cold start') ||
    responseMessage.includes('starting up') ||
    responseMessage.includes('waking up')
  );
}

/**
 * Retry a promise-based operation with exponential backoff and cold start handling
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
    baseDelay = 20000, // 20 seconds for cold starts
    maxDelay = 60000,  // 60 seconds maximum
    backoffIncrement = 10000, // 10 seconds increment per retry
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
      const isColdStart = isColdStartError(error) || hasColdStartMessage(error);
      const customShouldRetry = shouldRetry ? shouldRetry(error) : true;
      
      if (!isColdStart && !customShouldRetry) {
        // Not a cold start and custom logic says don't retry
        throw error;
      }

      // Calculate delay with linear backoff (avoids compounding with axios retries)
      // For cold starts: 20s, 30s, 40s, 50s (capped at maxDelay)
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
      baseDelay: 20000, // 20 seconds for cold starts
      onRetry: (attempt, error) => {
        const isColdStart = isColdStartError(error) || hasColdStartMessage(error);
        
        let message: string;
        if (isColdStart) {
          if (attempt === 1) {
            message = 'Backend is starting up (cold start). This can take 30-60 seconds. Please wait...';
          } else {
            message = `Still waking up the backend... Attempt ${attempt + 1}. Almost there!`;
          }
        } else {
          message = `Connection issue detected. Retrying (attempt ${attempt + 1})...`;
        }
        
        if (onProgress) {
          onProgress(message, attempt);
        }
        
        // Log for debugging
        if (import.meta.env.DEV) {
          console.log(`[Retry ${attempt}]`, message, 'Error:', error);
        }
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
        
        // Retry everything else (cold starts, network errors, server errors)
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
      baseDelay: 20000,
      onRetry: (attempt, error) => {
        const isColdStart = isColdStartError(error) || hasColdStartMessage(error);
        
        let message: string;
        if (isColdStart) {
          message = `Backend is waking up... Attempt ${attempt + 1}. Please wait...`;
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
        
        // Retry cold starts and network errors
        return true;
      }
    }
  );
}
