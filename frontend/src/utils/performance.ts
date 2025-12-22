/**
 * Performance Monitoring and Optimization Utilities
 * 
 * Tracks and optimizes:
 * - Core Web Vitals (LCP, FID, CLS)
 * - Time to Interactive (TTI)
 * - First Contentful Paint (FCP)
 * - API response times
 * - Cache hit rates
 */

import { apiUrl } from '@/lib/api';

interface PerformanceMetric {
  name: string;
  value: number;
  rating: 'good' | 'needs-improvement' | 'poor';
  timestamp: number;
}

interface PerformanceReport {
  metrics: PerformanceMetric[];
  navigationTiming: {
    dns: number;
    tcp: number;
    request: number;
    response: number;
    domProcessing: number;
    onLoad: number;
    total: number;
  };
  resources: {
    scripts: number;
    stylesheets: number;
    images: number;
    fonts: number;
    total: number;
  };
  cacheStats: {
    hits: number;
    misses: number;
    hitRate: number;
  };
}

// Thresholds for Core Web Vitals (based on Google's recommendations)
const THRESHOLDS = {
  LCP: { good: 2500, poor: 4000 }, // Largest Contentful Paint
  FID: { good: 100, poor: 300 },   // First Input Delay
  CLS: { good: 0.1, poor: 0.25 },   // Cumulative Layout Shift
  FCP: { good: 1800, poor: 3000 },  // First Contentful Paint
  TTFB: { good: 800, poor: 1800 },  // Time to First Byte
  TTI: { good: 3800, poor: 7300 },  // Time to Interactive
};

/**
 * Get performance rating based on value and thresholds
 */
function getRating(value: number, thresholds: { good: number; poor: number }): 'good' | 'needs-improvement' | 'poor' {
  if (value <= thresholds.good) return 'good';
  if (value <= thresholds.poor) return 'needs-improvement';
  return 'poor';
}

/**
 * Measure Largest Contentful Paint (LCP)
 */
export function measureLCP(callback: (metric: PerformanceMetric) => void) {
  if (!('PerformanceObserver' in window)) return;

  try {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const lastEntry = entries[entries.length - 1] as any;

      const value = lastEntry.renderTime || lastEntry.loadTime;
      
      callback({
        name: 'LCP',
        value,
        rating: getRating(value, THRESHOLDS.LCP),
        timestamp: Date.now(),
      });
    });

    observer.observe({ type: 'largest-contentful-paint', buffered: true });
  } catch (e) {
    console.warn('LCP measurement failed:', e);
  }
}

/**
 * Measure First Input Delay (FID)
 */
export function measureFID(callback: (metric: PerformanceMetric) => void) {
  if (!('PerformanceObserver' in window)) return;

  try {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      
      entries.forEach((entry: any) => {
        callback({
          name: 'FID',
          value: entry.processingStart - entry.startTime,
          rating: getRating(entry.processingStart - entry.startTime, THRESHOLDS.FID),
          timestamp: Date.now(),
        });
      });
    });

    observer.observe({ type: 'first-input', buffered: true });
  } catch (e) {
    console.warn('FID measurement failed:', e);
  }
}

/**
 * Measure Cumulative Layout Shift (CLS)
 */
export function measureCLS(callback: (metric: PerformanceMetric) => void) {
  if (!('PerformanceObserver' in window)) return;

  let clsValue = 0;

  try {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      
      entries.forEach((entry: any) => {
        if (!entry.hadRecentInput) {
          clsValue += entry.value;
        }
      });

      callback({
        name: 'CLS',
        value: clsValue,
        rating: getRating(clsValue, THRESHOLDS.CLS),
        timestamp: Date.now(),
      });
    });

    observer.observe({ type: 'layout-shift', buffered: true });
  } catch (e) {
    console.warn('CLS measurement failed:', e);
  }
}

/**
 * Measure First Contentful Paint (FCP)
 */
export function measureFCP(callback: (metric: PerformanceMetric) => void) {
  if (!('PerformanceObserver' in window)) return;

  try {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      
      entries.forEach((entry: any) => {
        if (entry.name === 'first-contentful-paint') {
          callback({
            name: 'FCP',
            value: entry.startTime,
            rating: getRating(entry.startTime, THRESHOLDS.FCP),
            timestamp: Date.now(),
          });
        }
      });
    });

    observer.observe({ type: 'paint', buffered: true });
  } catch (e) {
    console.warn('FCP measurement failed:', e);
  }
}

/**
 * Get Navigation Timing metrics
 */
export function getNavigationTiming() {
  const timing = performance.timing;
  
  return {
    dns: timing.domainLookupEnd - timing.domainLookupStart,
    tcp: timing.connectEnd - timing.connectStart,
    request: timing.responseStart - timing.requestStart,
    response: timing.responseEnd - timing.responseStart,
    domProcessing: timing.domComplete - timing.domLoading,
    onLoad: timing.loadEventEnd - timing.loadEventStart,
    total: timing.loadEventEnd - timing.navigationStart,
  };
}

/**
 * Get Resource Loading metrics
 */
export function getResourceMetrics() {
  const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
  
  const metrics = {
    scripts: 0,
    stylesheets: 0,
    images: 0,
    fonts: 0,
    total: resources.length,
  };

  resources.forEach((resource) => {
    if (resource.initiatorType === 'script') metrics.scripts++;
    else if (resource.initiatorType === 'css' || resource.initiatorType === 'link') metrics.stylesheets++;
    else if (resource.initiatorType === 'img') metrics.images++;
    else if (resource.initiatorType === 'font') metrics.fonts++;
  });

  return metrics;
}

/**
 * Initialize performance monitoring
 */
export function initPerformanceMonitoring(
  onMetric?: (metric: PerformanceMetric) => void
) {
  const handleMetric = (metric: PerformanceMetric) => {
    // Log in development
    if (import.meta.env.DEV) {
      console.log(`[Performance] ${metric.name}: ${metric.value.toFixed(2)}ms (${metric.rating})`);
    }

    // Send to analytics service
    onMetric?.(metric);

    // Send to backend analytics endpoint (if needed)
    if (metric.rating === 'poor') {
      // Only send poor metrics to reduce server load
      sendPerformanceMetric(metric);
    }
  };

  // Measure Core Web Vitals
  measureLCP(handleMetric);
  measureFID(handleMetric);
  measureCLS(handleMetric);
  measureFCP(handleMetric);
}

/**
 * Send performance metric to backend
 */
async function sendPerformanceMetric(metric: PerformanceMetric) {
  try {
    const data = JSON.stringify({
      ...metric,
      url: window.location.href,
      userAgent: navigator.userAgent,
    });
    
    // Use sendBeacon for reliable delivery even during page unload
    if ('sendBeacon' in navigator) {
      const success = navigator.sendBeacon(apiUrl('/api/analytics/performance'), data);
      
      // Fallback to fetch if sendBeacon fails
      if (!success) {
        fetch(apiUrl('/api/analytics/performance'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: data,
          keepalive: true,
        }).catch(() => {
          // Silently fail - analytics shouldn't break the app
        });
      }
    } else {
      // Fallback for browsers without sendBeacon
      fetch(apiUrl('/api/analytics/performance'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: data,
        keepalive: true,
      }).catch(() => {
        // Silently fail - analytics shouldn't break the app
      });
    }
  } catch (e) {
    // Ignore errors to not affect user experience
    console.debug('Failed to send performance metric:', e);
  }
}

/**
 * Get comprehensive performance report
 */
export function getPerformanceReport(): PerformanceReport {
  const metrics: PerformanceMetric[] = [];
  
  // Add timing metrics
  const timing = getNavigationTiming();
  metrics.push({
    name: 'TTFB',
    value: timing.request,
    rating: getRating(timing.request, THRESHOLDS.TTFB),
    timestamp: Date.now(),
  });

  return {
    metrics,
    navigationTiming: timing,
    resources: getResourceMetrics(),
    cacheStats: getCacheStats(),
  };
}

/**
 * Track cache statistics
 */
let cacheHits = 0;
let cacheMisses = 0;

export function trackCacheHit() {
  cacheHits++;
}

export function trackCacheMiss() {
  cacheMisses++;
}

export function getCacheStats() {
  const total = cacheHits + cacheMisses;
  return {
    hits: cacheHits,
    misses: cacheMisses,
    hitRate: total > 0 ? (cacheHits / total) * 100 : 0,
  };
}

/**
 * Mark custom performance milestones
 */
export function markPerformance(name: string) {
  if ('performance' in window && 'mark' in performance) {
    performance.mark(name);
  }
}

export function measurePerformance(name: string, startMark: string, endMark: string) {
  if ('performance' in window && 'measure' in performance) {
    try {
      performance.measure(name, startMark, endMark);
      
      const measure = performance.getEntriesByName(name)[0];
      if (measure && import.meta.env.DEV) {
        console.log(`[Performance] ${name}: ${measure.duration.toFixed(2)}ms`);
      }
      
      return measure?.duration;
    } catch (e) {
      console.debug('Performance measurement failed:', e);
      return 0;
    }
  }
  return 0;
}

/**
 * Debounce function for performance optimization
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      func(...args);
    };

    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(later, wait);
  };
}

/**
 * Throttle function for performance optimization
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;

  return function executedFunction(...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

export default {
  initPerformanceMonitoring,
  getPerformanceReport,
  measureLCP,
  measureFID,
  measureCLS,
  measureFCP,
  getNavigationTiming,
  getResourceMetrics,
  getCacheStats,
  trackCacheHit,
  trackCacheMiss,
  markPerformance,
  measurePerformance,
  debounce,
  throttle,
};
