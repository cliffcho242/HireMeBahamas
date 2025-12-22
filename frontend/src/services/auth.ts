/**
 * Auth Service
 * 
 * Handles token refresh with queuing mechanism to prevent multiple
 * concurrent refresh requests. Provides Facebook-style stable sessions
 * with automatic silent token refresh.
 */

import { apiFetch as baseApiFetch, apiUrl } from '../lib/api';
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
    const data = await baseApiFetch<User | null>("/api/auth/me");
    
    // The backend returns UserResponse which contains the user data directly
    if (!data) return null;
    return data;
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

    const data = await baseApiFetch<{ access_token?: string; user?: User }>("/api/auth/refresh", {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
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
