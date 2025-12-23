/**
 * Robust API Client with automatic retries, timeouts, and typed errors
 * 
 * Features:
 * - Automatic base URL prefixing
 * - Configurable timeouts with defaults
 * - Retry logic for idempotent GET requests with exponential backoff
 * - Typed error responses
 * - User-friendly error messages
 */

import { API_BASE_URL } from './api';

/**
 * API error types for better error handling
 */
export enum ApiErrorType {
  NETWORK = 'NETWORK',
  TIMEOUT = 'TIMEOUT',
  SERVER = 'SERVER',
  CLIENT = 'CLIENT',
  UNKNOWN = 'UNKNOWN',
}

/**
 * Structured API error with type information
 */
export class ApiError extends Error {
  type: ApiErrorType;
  status?: number;
  data?: unknown;
  endpoint?: string;

  constructor(
    message: string,
    type: ApiErrorType,
    status?: number,
    data?: unknown,
    endpoint?: string
  ) {
    super(message);
    this.name = 'ApiError';
    this.type = type;
    this.status = status;
    this.data = data;
    this.endpoint = endpoint;
  }

  /**
   * Get user-friendly error message based on error type
   */
  getUserMessage(): string {
    switch (this.type) {
      case ApiErrorType.NETWORK:
        return 'Unable to connect to server. Please check your internet connection.';
      case ApiErrorType.TIMEOUT:
        return 'Request timed out. The server is taking too long to respond.';
      case ApiErrorType.SERVER:
        return 'Server error. Please try again in a moment.';
      case ApiErrorType.CLIENT:
        if (this.status === 401) {
          return 'Your session has expired. Please log in again.';
        }
        if (this.status === 403) {
          return "You don't have permission to access this resource.";
        }
        if (this.status === 404) {
          return 'The requested resource was not found.';
        }
        return 'Invalid request. Please try again.';
      default:
        return 'An unexpected error occurred. Please try again.';
    }
  }
}

/**
 * Configuration options for API requests
 */
export interface ApiClientOptions extends RequestInit {
  timeout?: number;
  retry?: boolean;
  retries?: number;
  retryDelay?: number;
  includeCredentials?: boolean;
}

/**
 * Default configuration
 */
const DEFAULT_OPTIONS: Required<Pick<ApiClientOptions, 'timeout' | 'retry' | 'retries' | 'retryDelay' | 'includeCredentials'>> = {
  timeout: 30000, // 30 seconds default
  retry: true,
  retries: 3,
  retryDelay: 1000, // 1 second base delay
  includeCredentials: true,
};

/**
 * Sleep utility for retry delays
 */
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Calculate exponential backoff delay
 */
function getBackoffDelay(attempt: number, baseDelay: number): number {
  // Exponential backoff with jitter: baseDelay * 2^attempt + random(0-1000ms)
  const exponentialDelay = baseDelay * Math.pow(2, attempt);
  const jitter = Math.random() * 1000;
  return Math.min(exponentialDelay + jitter, 30000); // Cap at 30 seconds
}

/**
 * Check if HTTP method is idempotent (safe to retry)
 * 
 * Note: Only GET, HEAD, and OPTIONS are truly safe to retry.
 * PUT and DELETE can have side effects on retry:
 * - PUT: May fail if resource state has changed
 * - DELETE: Will fail if resource is already deleted
 * 
 * We intentionally exclude PUT and DELETE from retries to prevent
 * unintended side effects and confusing error messages.
 */
function isIdempotent(method: string): boolean {
  const idempotentMethods = ['GET', 'HEAD', 'OPTIONS'];
  return idempotentMethods.includes(method.toUpperCase());
}

/**
 * Check if error is retryable
 */
function isRetryableError(status?: number, errorType?: ApiErrorType): boolean {
  // Network and timeout errors are retryable
  if (errorType === ApiErrorType.NETWORK || errorType === ApiErrorType.TIMEOUT) {
    return true;
  }
  
  // 5xx server errors are retryable (except 501 Not Implemented)
  if (status && status >= 500 && status !== 501) {
    return true;
  }
  
  // 408 Request Timeout, 429 Too Many Requests are retryable
  if (status === 408 || status === 429) {
    return true;
  }
  
  return false;
}

/**
 * Build full URL from path
 */
function buildUrl(path: string): string {
  if (!API_BASE_URL) {
    throw new ApiError(
      'API base URL is not configured. Set VITE_API_BASE_URL environment variable.',
      ApiErrorType.CLIENT
    );
  }
  
  // Handle absolute URLs (pass through)
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path;
  }
  
  // Ensure path starts with /
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  
  // Combine base URL and path
  return `${API_BASE_URL}${normalizedPath}`;
}

/**
 * Make an API request with timeout
 */
async function fetchWithTimeout(
  url: string,
  options: RequestInit,
  timeout: number
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    
    // Check if it was a timeout
    if (error instanceof Error && error.name === 'AbortError') {
      throw new ApiError(
        `Request timeout after ${timeout}ms`,
        ApiErrorType.TIMEOUT,
        undefined,
        undefined,
        url
      );
    }
    
    // Network error
    throw new ApiError(
      error instanceof Error ? error.message : 'Network error',
      ApiErrorType.NETWORK,
      undefined,
      undefined,
      url
    );
  }
}

/**
 * Parse error response and create ApiError
 */
async function parseErrorResponse(
  response: Response,
  endpoint: string
): Promise<ApiError> {
  let data: unknown;
  let message = `HTTP ${response.status}: ${response.statusText}`;
  
  try {
    const text = await response.text();
    if (text) {
      try {
        data = JSON.parse(text);
        // Try to extract error message from common formats
        if (typeof data === 'object' && data !== null) {
          const errorObj = data as Record<string, unknown>;
          message = (errorObj.message || errorObj.error || errorObj.detail || message) as string;
        }
      } catch {
        // Not JSON, use text as message if it's short
        if (text.length < 200) {
          message = text;
        }
      }
    }
  } catch {
    // Failed to read response body
  }
  
  // Determine error type
  let type: ApiErrorType;
  if (response.status >= 500) {
    type = ApiErrorType.SERVER;
  } else if (response.status >= 400) {
    type = ApiErrorType.CLIENT;
  } else {
    type = ApiErrorType.UNKNOWN;
  }
  
  return new ApiError(message, type, response.status, data, endpoint);
}

/**
 * Main API client function with retry logic
 */
export async function apiClient<T = unknown>(
  path: string,
  options: ApiClientOptions = {}
): Promise<T> {
  const {
    timeout = DEFAULT_OPTIONS.timeout,
    retry = DEFAULT_OPTIONS.retry,
    retries = DEFAULT_OPTIONS.retries,
    retryDelay = DEFAULT_OPTIONS.retryDelay,
    includeCredentials = DEFAULT_OPTIONS.includeCredentials,
    ...fetchOptions
  } = options;
  
  const method = fetchOptions.method || 'GET';
  const url = buildUrl(path);
  
  // Get auth token from localStorage
  const token = localStorage.getItem('token');
  
  // Build headers
  const headers = new Headers(fetchOptions.headers);
  if (!headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  
  const finalOptions: RequestInit = {
    ...fetchOptions,
    method,
    headers,
    credentials: includeCredentials ? 'include' : 'same-origin',
  };
  
  let lastError: ApiError | null = null;
  const shouldRetry = retry && isIdempotent(method);
  const maxAttempts = shouldRetry ? retries + 1 : 1;
  
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    try {
      // Add delay before retry (not on first attempt)
      if (attempt > 0) {
        const delay = getBackoffDelay(attempt - 1, retryDelay);
        console.log(`Retrying request (attempt ${attempt + 1}/${maxAttempts}) after ${delay}ms...`);
        await sleep(delay);
      }
      
      // Make request with timeout
      const response = await fetchWithTimeout(url, finalOptions, timeout);
      
      // Check if response is ok
      if (!response.ok) {
        const error = await parseErrorResponse(response, path);
        
        // Check if we should retry
        if (shouldRetry && attempt < maxAttempts - 1 && isRetryableError(error.status, error.type)) {
          lastError = error;
          continue;
        }
        
        throw error;
      }
      
      // Parse successful response
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }
      
      // Return text for non-JSON responses
      return (await response.text()) as T;
    } catch (error) {
      // If it's already an ApiError, store and potentially retry
      if (error instanceof ApiError) {
        lastError = error;
        
        // Check if we should retry
        if (shouldRetry && attempt < maxAttempts - 1 && isRetryableError(error.status, error.type)) {
          continue;
        }
        
        throw error;
      }
      
      // Unknown error
      lastError = new ApiError(
        error instanceof Error ? error.message : 'Unknown error',
        ApiErrorType.UNKNOWN,
        undefined,
        undefined,
        path
      );
      
      throw lastError;
    }
  }
  
  // If we exhausted all retries, throw the last error
  if (lastError) {
    throw lastError;
  }
  
  // This should never happen
  throw new ApiError('Request failed after all retries', ApiErrorType.UNKNOWN, undefined, undefined, path);
}

/**
 * Convenience methods for common HTTP verbs
 */
export const api = {
  get: <T = unknown>(path: string, options?: ApiClientOptions) =>
    apiClient<T>(path, { ...options, method: 'GET' }),
  
  post: <T = unknown>(path: string, body?: unknown, options?: ApiClientOptions) =>
    apiClient<T>(path, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    }),
  
  put: <T = unknown>(path: string, body?: unknown, options?: ApiClientOptions) =>
    apiClient<T>(path, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    }),
  
  patch: <T = unknown>(path: string, body?: unknown, options?: ApiClientOptions) =>
    apiClient<T>(path, {
      ...options,
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    }),
  
  delete: <T = unknown>(path: string, options?: ApiClientOptions) =>
    apiClient<T>(path, { ...options, method: 'DELETE' }),
};
