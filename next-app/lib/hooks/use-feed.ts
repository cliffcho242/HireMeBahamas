"use client";

import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";
import { CACHE_TIMES } from "@/lib/cache-config";

/**
 * Type for feed post items
 */
export interface FeedPost {
  id: number;
  content: string;
  author: {
    id: number;
    name: string;
    avatar?: string;
  };
  created_at: string;
  likes_count: number;
  comments_count: number;
}

/**
 * Hook to fetch feed data with React Query
 * 
 * Features:
 * - Automatic caching with 30s stale time
 * - Prevents duplicate fetches
 * - Automatic background refetch when data becomes stale
 * - Less DB load and faster UI
 * 
 * @returns React Query result with feed data
 */
export function useFeed() {
  return useQuery({
    queryKey: ["feed"],
    queryFn: () => apiGet<{ success: boolean; posts: FeedPost[] }>("/api/feed"),
    staleTime: CACHE_TIMES.STALE_TIME, // Matches the middleware cache time
    select: (data) => data.posts,
  });
}
