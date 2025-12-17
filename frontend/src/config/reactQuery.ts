/**
 * React Query Configuration for Facebook-Level Performance
 * 
 * Implements aggressive caching and optimistic updates:
 * - Stale-while-revalidate pattern
 * - Background refetching
 * - Optimistic updates for instant UI
 * - Smart cache invalidation
 */
import { QueryClient, QueryCache, MutationCache } from '@tanstack/react-query';

// Cache time configurations (in milliseconds)
// Note: React Query v5 renamed `cacheTime` to `gcTime` (garbage collection time)
const CACHE_TIMES = {
  // Very stable data (rarely changes)
  STABLE: {
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes (formerly cacheTime)
  },
  // Semi-stable data (jobs, user profiles)
  SEMI_STABLE: {
    staleTime: 2 * 60 * 1000, // 2 minutes
    gcTime: 15 * 60 * 1000, // 15 minutes (formerly cacheTime)
  },
  // Dynamic data (posts, feed)
  DYNAMIC: {
    staleTime: 30 * 1000, // 30 seconds
    gcTime: 5 * 60 * 1000, // 5 minutes (formerly cacheTime)
  },
  // Real-time data (messages, notifications)
  REALTIME: {
    staleTime: 0, // Always stale, refetch on focus
    gcTime: 60 * 1000, // 1 minute (formerly cacheTime)
  },
};

// Query cache for handling query-level events
const queryCache = new QueryCache({
  onError: (error, query) => {
    // Log errors for monitoring
    console.error('Query error:', {
      queryKey: query.queryKey,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  },
  onSuccess: (data, query) => {
    // Optional: Track successful queries for analytics
    if (import.meta.env.DEV) {
      console.log('Query success:', {
        queryKey: query.queryKey,
        dataSize: JSON.stringify(data).length,
      });
    }
  },
});

// Mutation cache for handling mutation-level events
const mutationCache = new MutationCache({
  onError: (error, _variables, _context, mutation) => {
    // Log mutation errors
    console.error('Mutation error:', {
      mutationKey: mutation.options.mutationKey,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  },
  onSuccess: (_data, _variables, _context, mutation) => {
    // Optional: Track successful mutations
    if (import.meta.env.DEV) {
      console.log('Mutation success:', {
        mutationKey: mutation.options.mutationKey,
      });
    }
  },
});

// Create optimized query client
export const queryClient = new QueryClient({
  queryCache,
  mutationCache,
  defaultOptions: {
    queries: {
      // Use DYNAMIC cache times as default
      staleTime: CACHE_TIMES.DYNAMIC.staleTime,
      gcTime: CACHE_TIMES.DYNAMIC.gcTime, // React Query v5: renamed from cacheTime
      
      // Retry configuration
      retry: 2, // Retry failed requests 2 times
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      
      // Refetch configuration for better UX
      refetchOnWindowFocus: true, // Refetch when user returns to tab
      refetchOnReconnect: true, // Refetch on network reconnection
      refetchOnMount: true, // Refetch on component mount if stale
      
      // React Query v5: useErrorBoundary removed, use throwOnError instead
      // throwOnError can be set per-query if needed, default is false
      
      // Network mode
      networkMode: 'online', // Only fetch when online
      
      // Performance optimization
      structuralSharing: true, // Prevent unnecessary re-renders
      // React Query v5: keepPreviousData is now placeholderData: 'previousData'
      // or use the new placeholderData option per-query
    },
    mutations: {
      // Retry failed mutations once
      retry: 1,
      retryDelay: 1000,
      
      // Network mode
      networkMode: 'online',
      
      // React Query v5: useErrorBoundary removed
      // Use throwOnError: true if you want errors to throw to error boundaries
      // Default behavior is to not throw (same as useErrorBoundary: false)
    },
  },
});

// Query key factories for consistent cache management
export const queryKeys = {
  // User-related queries
  users: {
    all: ['users'] as const,
    list: (filters?: Record<string, unknown>) => ['users', 'list', filters] as const,
    detail: (id: number | string) => ['users', 'detail', id] as const,
    me: () => ['users', 'me'] as const,
    profile: (username: string) => ['users', 'profile', username] as const,
    followers: (userId: number | string) => ['users', 'followers', userId] as const,
    following: (userId: number | string) => ['users', 'following', userId] as const,
  },
  
  // Post-related queries
  posts: {
    all: ['posts'] as const,
    list: (filters?: Record<string, unknown>) => ['posts', 'list', filters] as const,
    detail: (id: number | string) => ['posts', 'detail', id] as const,
    user: (userId: number | string) => ['posts', 'user', userId] as const,
    feed: (page?: number) => ['posts', 'feed', page] as const,
    likes: (postId: number | string) => ['posts', 'likes', postId] as const,
    comments: (postId: number | string) => ['posts', 'comments', postId] as const,
  },
  
  // Job-related queries
  jobs: {
    all: ['jobs'] as const,
    list: (filters?: Record<string, unknown>) => ['jobs', 'list', filters] as const,
    detail: (id: number | string) => ['jobs', 'detail', id] as const,
    employer: (employerId: number | string) => ['jobs', 'employer', employerId] as const,
    search: (query: string) => ['jobs', 'search', query] as const,
  },
  
  // Message-related queries
  messages: {
    all: ['messages'] as const,
    conversations: () => ['messages', 'conversations'] as const,
    conversation: (conversationId: number | string) => ['messages', 'conversation', conversationId] as const,
    unread: () => ['messages', 'unread'] as const,
  },
  
  // Notification-related queries
  notifications: {
    all: ['notifications'] as const,
    list: (page?: number) => ['notifications', 'list', page] as const,
    unread: () => ['notifications', 'unread'] as const,
  },
};

// Cache time helpers for different data types
export const getCacheConfig = (type: keyof typeof CACHE_TIMES) => CACHE_TIMES[type];

// Prefetch helpers for better perceived performance
export const prefetchQueries = {
  // Prefetch user profile when hovering over user link
  userProfile: async (username: string) => {
    await queryClient.prefetchQuery({
      queryKey: queryKeys.users.profile(username),
      staleTime: CACHE_TIMES.SEMI_STABLE.staleTime,
    });
  },
  
  // Prefetch post details when hovering over post
  postDetail: async (postId: number | string) => {
    await queryClient.prefetchQuery({
      queryKey: queryKeys.posts.detail(postId),
      staleTime: CACHE_TIMES.DYNAMIC.staleTime,
    });
  },
  
  // Prefetch job details
  jobDetail: async (jobId: number | string) => {
    await queryClient.prefetchQuery({
      queryKey: queryKeys.jobs.detail(jobId),
      staleTime: CACHE_TIMES.SEMI_STABLE.staleTime,
    });
  },
};

// Cache invalidation helpers
export const invalidateQueries = {
  // Invalidate all user-related queries
  allUsers: () => queryClient.invalidateQueries({ queryKey: queryKeys.users.all }),
  
  // Invalidate specific user profile
  userProfile: (userId: number | string) => 
    queryClient.invalidateQueries({ queryKey: queryKeys.users.detail(userId) }),
  
  // Invalidate all posts
  allPosts: () => queryClient.invalidateQueries({ queryKey: queryKeys.posts.all }),
  
  // Invalidate user's posts
  userPosts: (userId: number | string) => 
    queryClient.invalidateQueries({ queryKey: queryKeys.posts.user(userId) }),
  
  // Invalidate feed
  feed: () => queryClient.invalidateQueries({ queryKey: queryKeys.posts.feed() }),
  
  // Invalidate all jobs
  allJobs: () => queryClient.invalidateQueries({ queryKey: queryKeys.jobs.all }),
  
  // Invalidate messages
  messages: () => queryClient.invalidateQueries({ queryKey: queryKeys.messages.all }),
  
  // Invalidate notifications
  notifications: () => queryClient.invalidateQueries({ queryKey: queryKeys.notifications.all }),
};

// Optimistic update helpers
export const optimisticUpdates = {
  // Optimistically update post likes
  likePost: (postId: number | string, userId: number | string) => {
    const queryKey = queryKeys.posts.detail(postId);
    
    queryClient.setQueryData(queryKey, (old: any) => {
      if (!old) return old;
      return {
        ...old,
        likes_count: (old.likes_count || 0) + 1,
        is_liked: true,
      };
    });
  },
  
  // Optimistically update post comments
  addComment: (postId: number | string, comment: any) => {
    const queryKey = queryKeys.posts.comments(postId);
    
    queryClient.setQueryData(queryKey, (old: any) => {
      if (!old) return [comment];
      return [comment, ...old];
    });
  },
  
  // Optimistically update follow status
  followUser: (userId: number | string) => {
    const queryKey = queryKeys.users.detail(userId);
    
    queryClient.setQueryData(queryKey, (old: any) => {
      if (!old) return old;
      return {
        ...old,
        followers_count: (old.followers_count || 0) + 1,
        is_following: true,
      };
    });
  },
};

export default queryClient;
