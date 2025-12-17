/**
 * Centralized Cache Configuration
 * 
 * This file defines all cache-related constants used across the application
 * for consistency and easier maintenance.
 */

/**
 * Cache durations in milliseconds
 */
export const CACHE_TIMES = {
  /** Data is fresh for 30 seconds - matches middleware cache time */
  STALE_TIME: 30_000,
  
  /** Cache garbage collection after 60 seconds */
  GC_TIME: 60_000,
  
  /** Static assets cache for 1 year */
  STATIC_MAX_AGE: 31536000,
  
  /** API routes cache for 60 seconds */
  API_MAX_AGE: 60,
  
  /** Health check cache for 30 seconds */
  HEALTH_MAX_AGE: 30,
} as const;

/**
 * Cache Control header values
 */
export const CACHE_HEADERS = {
  /** General pages cache - 30s fresh, 60s stale-while-revalidate */
  GENERAL: "public, max-age=30, stale-while-revalidate=60",
  
  /** Static assets - 1 year immutable */
  STATIC: "public, max-age=31536000, immutable",
  
  /** API jobs endpoint - optimized for high-traffic scenarios (e.g., social media referrals)
   * Longer CDN cache (60s) and extended stale-while-revalidate (300s) to handle traffic spikes
   * without overwhelming the database
   */
  API_JOBS: "public, s-maxage=60, stale-while-revalidate=300",
  
  /** Health endpoint - balanced caching */
  HEALTH: "public, s-maxage=30, stale-while-revalidate=60",
} as const;
