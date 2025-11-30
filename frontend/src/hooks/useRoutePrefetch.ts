/**
 * Route Prefetching Hook
 * 
 * Meta-inspired prefetching strategy for instant page transitions.
 * Prefetches route chunks on hover/focus for <50ms perceived load times.
 * 
 * Usage:
 *   const prefetch = useRoutePrefetch();
 *   <Link to="/jobs" onMouseEnter={() => prefetch('/jobs')}>Jobs</Link>
 */
import { useCallback, useRef } from 'react';

// Route to chunk mapping (matches manualChunks in vite.config.ts)
const ROUTE_CHUNKS: Record<string, () => Promise<unknown>> = {
  '/': () => import('../pages/Home'),
  '/jobs': () => import('../pages/Jobs'),
  '/messages': () => import('../pages/Messages'),
  '/profile': () => import('../pages/Profile'),
  '/post-job': () => import('../pages/PostJob'),
  '/hireme': () => import('../pages/HireMe'),
  '/friends': () => import('../pages/Users'),
  '/dashboard': () => import('../pages/Dashboard'),
};

// Track prefetched routes to avoid duplicate fetches
const prefetchedRoutes = new Set<string>();

/**
 * Hook for prefetching route chunks on hover/focus
 */
export function useRoutePrefetch() {
  const prefetchTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const prefetch = useCallback((route: string) => {
    // Skip if already prefetched
    if (prefetchedRoutes.has(route)) return;

    // Get the chunk loader for this route
    const chunkLoader = ROUTE_CHUNKS[route];
    if (!chunkLoader) return;

    // Debounce prefetch to avoid unnecessary loads on quick mouse movements
    if (prefetchTimeoutRef.current) {
      clearTimeout(prefetchTimeoutRef.current);
    }

    prefetchTimeoutRef.current = setTimeout(() => {
      // Mark as prefetched immediately to prevent duplicate loads
      prefetchedRoutes.add(route);
      
      // Prefetch during idle time
      if ('requestIdleCallback' in window) {
        (window as Window & { requestIdleCallback: (cb: () => void) => void }).requestIdleCallback(() => {
          chunkLoader().catch(() => {
            // Remove from prefetched if failed so it can retry
            prefetchedRoutes.delete(route);
          });
        });
      } else {
        // Fallback for browsers without requestIdleCallback
        setTimeout(() => {
          chunkLoader().catch(() => {
            prefetchedRoutes.delete(route);
          });
        }, 0);
      }
    }, 100); // 100ms debounce
  }, []);

  const cancelPrefetch = useCallback(() => {
    if (prefetchTimeoutRef.current) {
      clearTimeout(prefetchTimeoutRef.current);
      prefetchTimeoutRef.current = null;
    }
  }, []);

  return { prefetch, cancelPrefetch };
}

/**
 * Prefetch all main navigation routes on app mount
 * Called once during initial load for instant navigation
 */
export function prefetchMainRoutes() {
  const mainRoutes = ['/jobs', '/messages', '/profile'];
  
  // Use intersection observer pattern for intelligent prefetching
  if ('requestIdleCallback' in window) {
    (window as Window & { requestIdleCallback: (cb: () => void, opts?: { timeout: number }) => void }).requestIdleCallback(() => {
      mainRoutes.forEach((route, index) => {
        // Stagger prefetches to avoid network congestion
        setTimeout(() => {
          const chunkLoader = ROUTE_CHUNKS[route];
          if (chunkLoader && !prefetchedRoutes.has(route)) {
            prefetchedRoutes.add(route);
            chunkLoader().catch(() => {
              prefetchedRoutes.delete(route);
            });
          }
        }, index * 500); // 500ms between each prefetch
      });
    }, { timeout: 3000 }); // Timeout after 3s if idle never called
  }
}

/**
 * Get prefetch status for debugging
 */
export function getPrefetchedRoutes(): string[] {
  return Array.from(prefetchedRoutes);
}

export default useRoutePrefetch;
