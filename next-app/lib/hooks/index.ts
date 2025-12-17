/**
 * React Query Hooks
 * 
 * This module provides React Query hooks for data fetching with:
 * - Automatic request deduplication
 * - Smart caching (30s stale time)
 * - Background revalidation
 * - Optimistic updates support
 */

export { useJobs, useJob } from "./use-jobs";
export { useFeed } from "./use-feed";
