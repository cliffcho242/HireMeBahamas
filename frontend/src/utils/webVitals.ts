/**
 * Web Vitals Performance Monitoring
 * 
 * Tracks Core Web Vitals and reports them to Sentry for performance monitoring.
 * This helps ensure we maintain Lighthouse 90+ performance scores.
 */

import * as Sentry from '@sentry/react';

// Type definitions for Web Vitals metrics
interface Metric {
  name: string;
  value: number;
  rating: 'good' | 'needs-improvement' | 'poor';
  delta: number;
  id: string;
}

/**
 * Report Web Vitals to Sentry
 * Automatically captures FCP, LCP, CLS, FID, and TTFB
 */
export function reportWebVitals(): void {
  // Only run in browser environment
  if (typeof window === 'undefined') {
    return;
  }

  // Use the web-vitals library if available, otherwise use Performance Observer API
  if ('PerformanceObserver' in window) {
    // Observe Largest Contentful Paint (LCP)
    observeLCP();
    
    // Observe First Input Delay (FID)
    observeFID();
    
    // Observe Cumulative Layout Shift (CLS)
    observeCLS();
    
    // Get First Contentful Paint (FCP) from Navigation Timing
    observeFCP();
    
    // Get Time to First Byte (TTFB)
    observeTTFB();
  }
}

/**
 * Report metric to Sentry
 */
function reportToSentry(metric: Metric): void {
  // Only report in production
  if (import.meta.env.DEV) {
    console.log('Web Vital:', metric);
    return;
  }

  // Send to Sentry as a measurement
  Sentry.setMeasurement(metric.name, metric.value, 'millisecond');
  
  // Add context
  Sentry.setContext('web-vitals', {
    [metric.name]: {
      value: metric.value,
      rating: metric.rating,
      id: metric.id,
    },
  });

  // If the metric is poor, send as a warning
  if (metric.rating === 'poor') {
    Sentry.captureMessage(`Poor ${metric.name}: ${metric.value}`, {
      level: 'warning',
      tags: {
        metric: metric.name,
        rating: metric.rating,
      },
    });
  }
}

/**
 * Observe Largest Contentful Paint (LCP)
 * Target: < 2.5s (good), < 4s (needs improvement), >= 4s (poor)
 */
function observeLCP(): void {
  try {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const lastEntry = entries[entries.length - 1] as PerformanceEntry & { renderTime?: number; loadTime?: number };
      
      const value = lastEntry.renderTime || lastEntry.loadTime || 0;
      const rating = value <= 2500 ? 'good' : value <= 4000 ? 'needs-improvement' : 'poor';
      
      reportToSentry({
        name: 'LCP',
        value,
        rating,
        delta: value,
        id: lastEntry.entryType,
      });
    });

    observer.observe({ type: 'largest-contentful-paint', buffered: true });
  } catch (error) {
    console.error('Error observing LCP:', error);
  }
}

/**
 * Observe First Input Delay (FID)
 * Target: < 100ms (good), < 300ms (needs improvement), >= 300ms (poor)
 */
function observeFID(): void {
  try {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach((entry: PerformanceEntry & { processingStart?: number }) => {
        const value = entry.processingStart ? entry.processingStart - entry.startTime : 0;
        const rating = value <= 100 ? 'good' : value <= 300 ? 'needs-improvement' : 'poor';
        
        reportToSentry({
          name: 'FID',
          value,
          rating,
          delta: value,
          id: entry.entryType,
        });
      });
    });

    observer.observe({ type: 'first-input', buffered: true });
  } catch (error) {
    console.error('Error observing FID:', error);
  }
}

/**
 * Observe Cumulative Layout Shift (CLS)
 * Target: < 0.1 (good), < 0.25 (needs improvement), >= 0.25 (poor)
 */
function observeCLS(): void {
  try {
    let clsValue = 0;
    let clsEntries: PerformanceEntry[] = [];

    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach((entry: PerformanceEntry & { value?: number; hadRecentInput?: boolean }) => {
        // Only count layout shifts without recent user input
        if (!entry.hadRecentInput) {
          clsValue += entry.value || 0;
          clsEntries.push(entry);
        }
      });

      const rating = clsValue <= 0.1 ? 'good' : clsValue <= 0.25 ? 'needs-improvement' : 'poor';
      
      reportToSentry({
        name: 'CLS',
        value: clsValue,
        rating,
        delta: clsValue,
        id: 'cls',
      });
    });

    observer.observe({ type: 'layout-shift', buffered: true });
  } catch (error) {
    console.error('Error observing CLS:', error);
  }
}

/**
 * Observe First Contentful Paint (FCP)
 * Target: < 1.8s (good), < 3s (needs improvement), >= 3s (poor)
 */
function observeFCP(): void {
  try {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach((entry) => {
        const value = entry.startTime;
        const rating = value <= 1800 ? 'good' : value <= 3000 ? 'needs-improvement' : 'poor';
        
        reportToSentry({
          name: 'FCP',
          value,
          rating,
          delta: value,
          id: entry.entryType,
        });
      });
    });

    observer.observe({ type: 'paint', buffered: true });
  } catch (error) {
    console.error('Error observing FCP:', error);
  }
}

/**
 * Observe Time to First Byte (TTFB)
 * Target: < 800ms (good), < 1800ms (needs improvement), >= 1800ms (poor)
 */
function observeTTFB(): void {
  try {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach((entry: PerformanceEntry & { responseStart?: number }) => {
        const value = entry.responseStart || 0;
        const rating = value <= 800 ? 'good' : value <= 1800 ? 'needs-improvement' : 'poor';
        
        reportToSentry({
          name: 'TTFB',
          value,
          rating,
          delta: value,
          id: entry.entryType,
        });
      });
    });

    observer.observe({ type: 'navigation', buffered: true });
  } catch (error) {
    console.error('Error observing TTFB:', error);
  }
}

/**
 * Get performance metrics summary
 * Useful for debugging and monitoring
 */
export function getPerformanceMetrics(): Record<string, number> {
  if (typeof window === 'undefined' || !window.performance) {
    return {};
  }

  const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
  const paint = performance.getEntriesByType('paint');

  return {
    // Navigation timing
    dns: navigation ? navigation.domainLookupEnd - navigation.domainLookupStart : 0,
    tcp: navigation ? navigation.connectEnd - navigation.connectStart : 0,
    ttfb: navigation ? navigation.responseStart - navigation.requestStart : 0,
    download: navigation ? navigation.responseEnd - navigation.responseStart : 0,
    domInteractive: navigation ? navigation.domInteractive - navigation.fetchStart : 0,
    domComplete: navigation ? navigation.domComplete - navigation.fetchStart : 0,
    loadComplete: navigation ? navigation.loadEventEnd - navigation.fetchStart : 0,
    
    // Paint timing
    fcp: paint.find((entry) => entry.name === 'first-contentful-paint')?.startTime || 0,
  };
}
