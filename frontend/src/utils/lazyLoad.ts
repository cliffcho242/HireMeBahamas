/**
 * Lazy Loading Utilities for Code Splitting
 * 
 * Implements intelligent code splitting:
 * - Route-based code splitting
 * - Component lazy loading
 * - Prefetching for likely navigations
 * - Error boundaries for failed chunks
 */
import { lazy, ComponentType, LazyExoticComponent } from 'react';

// Retry configuration for failed chunk loads
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

/**
 * Enhanced lazy loading with retry logic
 */
export function lazyWithRetry<T extends ComponentType<any>>(
  componentImport: () => Promise<{ default: T }>,
  retries = MAX_RETRIES
): LazyExoticComponent<T> {
  return lazy(async () => {
    const attemptLoad = async (retriesLeft: number): Promise<{ default: T }> => {
      try {
        return await componentImport();
      } catch (error) {
        // If retries left, wait and try again
        if (retriesLeft > 0) {
          console.warn(`Chunk load failed, retrying... (${retriesLeft} retries left)`);
          await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
          return attemptLoad(retriesLeft - 1);
        }
        
        // No retries left, throw error
        console.error('Chunk load failed after retries:', error);
        throw error;
      }
    };
    
    return attemptLoad(retries);
  });
}

/**
 * Preload a lazy component
 * Call this when user hovers over a link to prefetch the component
 */
export function preloadComponent(
  componentImport: () => Promise<{ default: ComponentType<any> }>
): Promise<{ default: ComponentType<any> }> {
  return componentImport();
}

/**
 * Lazy load route components with retry
 * Using barrel exports for case-safe, cleaner imports
 */
export const LazyRoutes = {
  // Authentication pages
  Login: lazyWithRetry(() => import('../pages').then(m => ({ default: m.Login }))),
  Register: lazyWithRetry(() => import('../pages').then(m => ({ default: m.Register }))),
  
  // Main pages
  Home: lazyWithRetry(() => import('../pages').then(m => ({ default: m.Home }))),
  Feed: lazyWithRetry(() => import('../pages').then(m => ({ default: m.Feed }))),
  Profile: lazyWithRetry(() => import('../pages').then(m => ({ default: m.Profile }))),
  
  // Job pages
  Jobs: lazyWithRetry(() => import('../pages').then(m => ({ default: m.Jobs }))),
  JobDetail: lazyWithRetry(() => import('../pages').then(m => ({ default: m.JobDetail }))),
  JobPost: lazyWithRetry(() => import('../pages').then(m => ({ default: m.JobPost }))),
  
  // Social features
  Messages: lazyWithRetry(() => import('../pages').then(m => ({ default: m.Messages }))),
  // Notifications is a component, not a page - map to Home for now
  Notifications: lazyWithRetry(() => import('../pages').then(m => ({ default: m.Home }))),
  
  // User pages
  UserProfile: lazyWithRetry(() => import('../pages').then(m => ({ default: m.UserProfile }))),
  // Settings doesn't exist yet - map to Profile for now
  Settings: lazyWithRetry(() => import('../pages').then(m => ({ default: m.Profile }))),
  
  // Other pages
  // About doesn't exist yet - map to Home for now
  About: lazyWithRetry(() => import('../pages').then(m => ({ default: m.Home }))),
  NotFound: lazyWithRetry(() => import('../pages').then(m => ({ default: m.NotFound }))),
};

/**
 * Prefetch routes based on user behavior
 * Using barrel exports for case-safe, cleaner imports
 */
export const prefetchRoutes = {
  // Prefetch likely next pages
  prefetchAuthPages: () => {
    preloadComponent(() => import('../pages').then(m => ({ default: m.Login })));
    preloadComponent(() => import('../pages').then(m => ({ default: m.Register })));
  },
  
  prefetchMainPages: () => {
    preloadComponent(() => import('../pages').then(m => ({ default: m.Feed })));
    preloadComponent(() => import('../pages').then(m => ({ default: m.Jobs })));
    preloadComponent(() => import('../pages').then(m => ({ default: m.Messages })));
  },
  
  prefetchSocialPages: () => {
    preloadComponent(() => import('../pages').then(m => ({ default: m.Profile })));
    preloadComponent(() => import('../pages').then(m => ({ default: m.Home })));
  },
};

/**
 * Prefetch on link hover
 */
export function usePrefetchOnHover(
  componentImport: () => Promise<{ default: ComponentType<any> }>
) {
  let prefetched = false;
  
  const handleMouseEnter = () => {
    if (!prefetched) {
      prefetched = true;
      preloadComponent(componentImport).catch(() => {
        // Reset on error so it can be retried
        prefetched = false;
      });
    }
  };
  
  return { onMouseEnter: handleMouseEnter };
}

/**
 * Lazy load heavy components that aren't needed immediately
 * Using barrel exports for case-safe, cleaner imports
 */
export const LazyComponents = {
  // Charts/analytics - map to existing AIDashboard
  AnalyticsDashboard: lazyWithRetry(() => import('../components').then(m => ({ 
    default: m.AnalyticsDashboard 
  }))),
};

/**
 * Get chunk loading stats for monitoring
 */
export function getChunkLoadStats() {
  const performance = window.performance;
  const entries = performance.getEntriesByType('resource');
  
  const chunkLoads = entries.filter((entry: any) => 
    entry.name.includes('chunk') || entry.name.includes('assets')
  );
  
  const stats = {
    totalChunks: chunkLoads.length,
    avgLoadTime: chunkLoads.reduce((sum: number, entry: any) => 
      sum + entry.duration, 0) / chunkLoads.length || 0,
    slowestChunk: chunkLoads.reduce((slowest: any, entry: any) => 
      entry.duration > (slowest?.duration || 0) ? entry : slowest, null),
  };
  
  return stats;
}

/**
 * Prefetch chunks based on connection speed
 */
export function prefetchBasedOnConnection() {
  // @ts-expect-error - navigator.connection is not in TypeScript types yet
  const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
  
  if (!connection) {
    // If no connection API, prefetch on fast connections (assume good connection)
    prefetchRoutes.prefetchMainPages();
    return;
  }
  
  // Effective connection type: 'slow-2g', '2g', '3g', or '4g'
  const effectiveType = connection.effectiveType;
  
  if (effectiveType === '4g' || effectiveType === '3g') {
    // Fast connection, prefetch everything
    prefetchRoutes.prefetchMainPages();
    prefetchRoutes.prefetchSocialPages();
  } else if (effectiveType === '2g') {
    // Slow connection, only prefetch critical pages
    prefetchRoutes.prefetchMainPages();
  }
  // On slow-2g, don't prefetch anything
}

export default {
  lazyWithRetry,
  preloadComponent,
  LazyRoutes,
  LazyComponents,
  prefetchRoutes,
  usePrefetchOnHover,
  getChunkLoadStats,
  prefetchBasedOnConnection,
};
