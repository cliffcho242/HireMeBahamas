/**
 * Data Preloader Service
 * 
 * Preloads critical data after login to ensure instant page loads.
 * This eliminates loading spinners on first navigation to key pages.
 * 
 * Preloaded data includes:
 * - User profile details
 * - Recent jobs list
 * - Unread message count
 * - Friend/follower counts
 * - Notification count
 * 
 * Usage:
 *   import { preloadCriticalData } from './dataPreloader';
 *   
 *   // After successful login:
 *   preloadCriticalData(token).catch(console.error);
 */

import { QueryClient } from '@tanstack/react-query';

// API base URL
const API_URL = import.meta.env.VITE_API_URL || '';

// Query keys for React Query cache
export const QUERY_KEYS = {
  PROFILE: ['profile'],
  JOBS: ['jobs'],
  JOBS_RECENT: ['jobs', 'recent'],
  POSTS: ['posts'],
  POSTS_FEED: ['posts', 'feed'],
  NOTIFICATIONS: ['notifications'],
  NOTIFICATIONS_COUNT: ['notifications', 'count'],
  MESSAGES: ['messages'],
  MESSAGES_UNREAD: ['messages', 'unread-count'],
  FRIENDS: ['friends'],
  FRIENDS_LIST: ['friends', 'list'],
  FRIENDS_SUGGESTIONS: ['friends', 'suggestions'],
};

// Fetch with auth header helper
async function fetchWithAuth(url: string, token: string): Promise<Response> {
  return fetch(`${API_URL}${url}`, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });
}

/**
 * Preload jobs data
 */
async function preloadJobs(token: string, queryClient: QueryClient): Promise<void> {
  try {
    const response = await fetchWithAuth('/api/jobs?limit=20', token);
    if (response.ok) {
      const data = await response.json();
      queryClient.setQueryData(QUERY_KEYS.JOBS, data);
      queryClient.setQueryData(QUERY_KEYS.JOBS_RECENT, data);
    }
  } catch (error) {
    console.warn('Failed to preload jobs:', error);
  }
}

/**
 * Preload posts/feed data
 */
async function preloadPosts(token: string, queryClient: QueryClient): Promise<void> {
  try {
    const response = await fetchWithAuth('/api/posts?limit=20', token);
    if (response.ok) {
      const data = await response.json();
      queryClient.setQueryData(QUERY_KEYS.POSTS, data);
      queryClient.setQueryData(QUERY_KEYS.POSTS_FEED, data);
    }
  } catch (error) {
    console.warn('Failed to preload posts:', error);
  }
}

/**
 * Preload notification count
 */
async function preloadNotificationCount(token: string, queryClient: QueryClient): Promise<void> {
  try {
    const response = await fetchWithAuth('/api/notifications/unread-count', token);
    if (response.ok) {
      const data = await response.json();
      queryClient.setQueryData(QUERY_KEYS.NOTIFICATIONS_COUNT, data);
    }
  } catch (error) {
    console.warn('Failed to preload notification count:', error);
  }
}

/**
 * Preload unread message count
 */
async function preloadMessageCount(token: string, queryClient: QueryClient): Promise<void> {
  try {
    const response = await fetchWithAuth('/api/messages/unread-count', token);
    if (response.ok) {
      const data = await response.json();
      queryClient.setQueryData(QUERY_KEYS.MESSAGES_UNREAD, data);
    }
  } catch (error) {
    console.warn('Failed to preload message count:', error);
  }
}

/**
 * Preload friends list
 */
async function preloadFriends(token: string, queryClient: QueryClient): Promise<void> {
  try {
    const response = await fetchWithAuth('/api/friends/list', token);
    if (response.ok) {
      const data = await response.json();
      queryClient.setQueryData(QUERY_KEYS.FRIENDS_LIST, data);
    }
  } catch (error) {
    console.warn('Failed to preload friends:', error);
  }
}

/**
 * Preload friend suggestions
 */
async function preloadFriendSuggestions(token: string, queryClient: QueryClient): Promise<void> {
  try {
    const response = await fetchWithAuth('/api/friends/suggestions', token);
    if (response.ok) {
      const data = await response.json();
      queryClient.setQueryData(QUERY_KEYS.FRIENDS_SUGGESTIONS, data);
    }
  } catch (error) {
    console.warn('Failed to preload friend suggestions:', error);
  }
}

/**
 * Preload user profile
 */
async function preloadProfile(token: string, queryClient: QueryClient): Promise<void> {
  try {
    const response = await fetchWithAuth('/api/profile', token);
    if (response.ok) {
      const data = await response.json();
      queryClient.setQueryData(QUERY_KEYS.PROFILE, data);
    }
  } catch (error) {
    console.warn('Failed to preload profile:', error);
  }
}

/**
 * Main preload function - preloads all critical data in parallel
 * 
 * @param token - JWT authentication token
 * @param queryClient - React Query client instance
 * @returns Promise that resolves when all preloading is complete
 */
export async function preloadCriticalData(
  token: string,
  queryClient: QueryClient
): Promise<void> {
  console.log('🚀 Preloading critical data for instant navigation...');
  
  const startTime = performance.now();
  
  // Preload all data in parallel for maximum speed
  await Promise.allSettled([
    preloadProfile(token, queryClient),
    preloadJobs(token, queryClient),
    preloadPosts(token, queryClient),
    preloadNotificationCount(token, queryClient),
    preloadMessageCount(token, queryClient),
    preloadFriends(token, queryClient),
    preloadFriendSuggestions(token, queryClient),
  ]);
  
  const elapsed = Math.round(performance.now() - startTime);
  console.log(`✅ Critical data preloaded in ${elapsed}ms`);
}

/**
 * Preload data for a specific page
 * 
 * Call this when navigating to ensure data is ready before render
 */
export async function preloadForPage(
  page: 'jobs' | 'messages' | 'profile' | 'friends' | 'home',
  token: string,
  queryClient: QueryClient
): Promise<void> {
  switch (page) {
    case 'jobs':
      await preloadJobs(token, queryClient);
      break;
    case 'messages':
      await preloadMessageCount(token, queryClient);
      break;
    case 'profile':
      await preloadProfile(token, queryClient);
      break;
    case 'friends':
      await Promise.allSettled([
        preloadFriends(token, queryClient),
        preloadFriendSuggestions(token, queryClient),
      ]);
      break;
    case 'home':
      await Promise.allSettled([
        preloadPosts(token, queryClient),
        preloadNotificationCount(token, queryClient),
      ]);
      break;
  }
}

export default preloadCriticalData;
