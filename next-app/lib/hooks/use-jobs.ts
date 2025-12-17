"use client";

import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";
import { CACHE_TIMES } from "@/lib/cache-config";
import type { Job } from "@/lib/db";

/**
 * Hook to fetch jobs list with React Query
 * 
 * Features:
 * - Automatic caching with 30s stale time
 * - Prevents duplicate fetches
 * - Automatic background refetch when data becomes stale
 * 
 * @param options Query options
 * @returns React Query result with jobs data
 */
export function useJobs(options?: { limit?: number }) {
  return useQuery({
    queryKey: ["jobs", options?.limit], // Cache key includes limit for proper cache separation
    queryFn: () => {
      const endpoint = options?.limit
        ? `/api/jobs?limit=${options.limit}`
        : "/api/jobs";
      return apiGet<{ success: boolean; jobs: Job[] }>(endpoint);
    },
    staleTime: CACHE_TIMES.STALE_TIME, // Matches the middleware cache time
    select: (data) => data.jobs, // Extract just the jobs array from the response
  });
}

/**
 * Hook to fetch a single job by ID
 * 
 * @param jobId Job ID
 * @returns React Query result with job data
 */
export function useJob(jobId: string | number | undefined) {
  return useQuery({
    queryKey: ["job", jobId],
    queryFn: () => apiGet<{ success: boolean; job: Job }>(`/api/jobs/${jobId}`),
    enabled: !!jobId, // Only fetch when jobId is defined
    staleTime: CACHE_TIMES.STALE_TIME,
    select: (data) => data.job,
  });
}
