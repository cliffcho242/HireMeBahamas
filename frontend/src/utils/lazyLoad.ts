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
 */
export const LazyRoutes = {
  // Authentication pages
  Login: lazyWithRetry(() => import('../pages/Login')),
  Register: lazyWithRetry(() => import('../pages/Register')),
  
  // Main pages
  Home: lazyWithRetry(() => import('../pages/Home')),
  Feed: lazyWithRetry(() => import('../pages/Feed')),
  Profile: lazyWithRetry(() => import('../pages/Profile')),
  
  // Job pages
  Jobs: lazyWithRetry(() => import('../pages/Jobs')),
  JobDetail: lazyWithRetry(() => import('../pages/JobDetail')),
  JobPost: lazyWithRetry(() => import('../pages/JobPost')),
  
  // Social features
  Messages: lazyWithRetry(() => import('../pages/Messages')),
  Notifications: lazyWithRetry(() => import('../pages/Notifications')),
  
  // User pages
  UserProfile: lazyWithRetry(() => import('../pages/UserProfile')),
  Settings: lazyWithRetry(() => import('../pages/Settings')),
  
  // Other pages
  About: lazyWithRetry(() => import('../pages/About')),
  NotFound: lazyWithRetry(() => import('../pages/NotFound')),
};

/**
 * Prefetch routes based on user behavior
 */
export const prefetchRoutes = {
  // Prefetch likely next pages
  prefetchAuthPages: () => {
    preloadComponent(() => import('../pages/Login'));
    preloadComponent(() => import('../pages/Register'));
  },
  
  prefetchMainPages: () => {
    preloadComponent(() => import('../pages/Feed'));
    preloadComponent(() => import('../pages/Jobs'));
    preloadComponent(() => import('../pages/Messages'));
  },
  
  prefetchSocialPages: () => {
    preloadComponent(() => import('../pages/Profile'));
    preloadComponent(() => import('../pages/Notifications'));
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
 */
export const LazyComponents = {
  // Image editor (if exists)
  ImageEditor: lazyWithRetry(() => import('../components/ImageEditor').catch(() => ({
    default: () => null // Fallback if component doesn't exist
  }))),
  
  // Rich text editor
  RichTextEditor: lazyWithRetry(() => import('../components/RichTextEditor').catch(() => ({
    default: () => null
  }))),
  
  // Video player
  VideoPlayer: lazyWithRetry(() => import('../components/VideoPlayer').catch(() => ({
    default: () => null
  }))),
  
  // Charts/analytics
  AnalyticsDashboard: lazyWithRetry(() => import('../components/AnalyticsDashboard').catch(() => ({
    default: () => null
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
  // @ts-ignore - navigator.connection is not in TypeScript types yet
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
