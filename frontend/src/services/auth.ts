/**
 * Auth Service
 * 
 * Handles token refresh with queuing mechanism to prevent multiple
 * concurrent refresh requests. Provides Facebook-style stable sessions
 * with automatic silent token refresh.
 */

let refreshing = false;
let queue: (() => void)[] = [];

/**
 * Refresh the authentication token
 * 
 * This function ensures only one refresh request happens at a time.
 * Additional calls during an active refresh are queued and resolved
 * when the refresh completes.
 * 
 * @returns Promise that resolves when token is refreshed
 */
export async function refreshToken(): Promise<void> {
  // If already refreshing, queue this request
  if (refreshing) {
    return new Promise((resolve) => queue.push(resolve));
  }

  refreshing = true;

  try {
    const response = await fetch("/api/auth/refresh", {
      credentials: "include",
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });

    if (!response.ok) {
      throw new Error(`Token refresh failed: ${response.status}`);
    }

    const data = await response.json();
    
    // Update token in localStorage
    if (data.access_token) {
      localStorage.setItem('token', data.access_token);
    }

    // Update user data if provided
    if (data.user) {
      localStorage.setItem('hireme_user', JSON.stringify(data.user));
    }
  } catch (error) {
    console.error('Token refresh error:', error);
    throw error;
  } finally {
    refreshing = false;
    
    // Resolve all queued promises
    queue.forEach((resolve) => resolve());
    queue = [];
  }
}

/**
 * Fetch wrapper with automatic token refresh on 401
 * 
 * @param input - Request URL or Request object
 * @param init - Request init options
 * @returns Response from the API
 */
export async function apiFetch(
  input: RequestInfo,
  init?: RequestInit
): Promise<Response> {
  // Add authorization header if token exists
  const token = localStorage.getItem('token');
  const headers = {
    ...init?.headers,
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
  };

  // First attempt
  const res = await fetch(input, {
    ...init,
    headers,
    credentials: "include",
  });

  // If unauthorized, refresh token and retry
  if (res.status === 401) {
    try {
      await refreshToken();
      
      // Get the new token and retry the original request
      const newToken = localStorage.getItem('token');
      const newHeaders = {
        ...init?.headers,
        ...(newToken ? { 'Authorization': `Bearer ${newToken}` } : {}),
      };
      
      return fetch(input, {
        ...init,
        headers: newHeaders,
        credentials: "include",
      });
    } catch (error) {
      // If refresh fails, redirect to login
      console.error('Token refresh failed, redirecting to login');
      localStorage.removeItem('token');
      localStorage.removeItem('hireme_session');
      localStorage.removeItem('hireme_user');
      window.location.href = '/login';
      throw error;
    }
  }

  return res;
}
