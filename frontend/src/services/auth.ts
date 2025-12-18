/**
 * Auth Service
 * 
 * Handles token refresh with queuing mechanism to prevent multiple
 * concurrent refresh requests. Provides Facebook-style stable sessions
 * with automatic silent token refresh.
 */

import { apiUrl } from '../lib/api';
import { User } from '../types/user';

// Session storage key - must match sessionManager.ts
const SESSION_KEY = 'hireme_session';
const USER_KEY = 'hireme_user';

let refreshing = false;
let queue: (() => void)[] = [];

/**
 * Get the current session from the backend
 * 
 * This function is called once on app startup to bootstrap authentication.
 * It uses the /api/auth/me endpoint with credentials: 'include' for Safari
 * cookie support.
 * 
 * ✅ Page refresh safe
 * ✅ Safari safe
 * ✅ Vercel safe
 * 
 * @returns User data if authenticated, null if not authenticated or error
 */
export async function getSession(): Promise<User | null> {
  try {
    const res = await fetch(apiUrl("/api/auth/me"), {
      credentials: 'include',
    });

    if (!res.ok) {
      // Not authenticated or error - return null safely
      return null;
    }

    const data = await res.json();
    
    // The backend returns UserResponse which contains the user data directly
    return data as User;
  } catch (error) {
    // Network error or other issue - return null safely (no guessing)
    if (import.meta.env.DEV) {
      console.error('Session fetch error:', error);
    }
    return null;
  }
}

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
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('No token available to refresh');
    }

    const response = await fetch(apiUrl("/api/auth/refresh"), {
      credentials: "include",
      headers: {
        'Authorization': `Bearer ${token}`,
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
      localStorage.setItem(USER_KEY, JSON.stringify(data.user));
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
      localStorage.removeItem(SESSION_KEY);
      localStorage.removeItem(USER_KEY);
      window.location.href = '/login';
      throw error;
    }
  }

  return res;
}
