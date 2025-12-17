/**
 * Sentry Error Monitoring Configuration
 * 
 * Production error monitoring for HireMeBahamas
 * Tracks errors, performance, and user feedback
 */
import * as Sentry from '@sentry/react';

// Only initialize Sentry in production
const isProduction = import.meta.env.PROD;
const sentryDsn = import.meta.env.VITE_SENTRY_DSN;

export function initSentry() {
  // Only initialize if we have a DSN and are in production
  if (isProduction && sentryDsn) {
    Sentry.init({
      dsn: sentryDsn,
      
      // Set environment
      environment: import.meta.env.MODE,
      
      // Performance monitoring - sample 10% of transactions
      integrations: [
        Sentry.browserTracingIntegration(),
        Sentry.replayIntegration({
          // Capture 10% of all sessions
          maskAllText: true,
          blockAllMedia: true,
        }),
      ],
      
      // Configure trace propagation
      tracePropagationTargets: ['localhost', /^https:\/\/.*\.vercel\.app/, /^https:\/\/hiremebahamas\.com/],
      
      // Performance monitoring sample rate
      tracesSampleRate: 0.1,
      
      // Replay sample rates
      replaysSessionSampleRate: 0.1,  // 10% of sessions
      replaysOnErrorSampleRate: 1.0,  // 100% of error sessions
      
      // Send default PII (personally identifiable information)
      sendDefaultPii: false,
      
      // Maximum breadcrumbs
      maxBreadcrumbs: 50,
      
      // Before send hook - filter sensitive data
      beforeSend(event) {
        // Don't send errors in development
        if (!isProduction) {
          return null;
        }
        
        // Filter out localhost errors
        if (event.request?.url?.includes('localhost')) {
          return null;
        }
        
        // Remove sensitive data from event
        if (event.request) {
          delete event.request.cookies;
        }
        
        return event;
      },
      
      // Ignore certain errors
      ignoreErrors: [
        // Browser extensions
        'top.GLOBALS',
        // Random plugins/extensions
        'originalCreateNotification',
        'canvas.contentDocument',
        'MyApp_RemoveAllHighlights',
        // Facebook quirks
        'fb_xd_fragment',
        // Network errors
        'NetworkError',
        'Network request failed',
        // Common non-critical errors
        'ResizeObserver loop limit exceeded',
        'ResizeObserver loop completed with undelivered notifications',
        // Aborted requests
        'AbortError',
        'The user aborted a request',
      ],
      
      // Ignore certain URLs
      denyUrls: [
        // Browser extensions
        /extensions\//i,
        /^chrome:\/\//i,
        /^chrome-extension:\/\//i,
        /^moz-extension:\/\//i,
      ],
    });
    
    console.log('✅ Sentry initialized for production error monitoring');
  } else if (!sentryDsn) {
    console.log('ℹ️ Sentry DSN not configured - error monitoring disabled');
  } else {
    console.log('ℹ️ Sentry disabled in development');
  }
}

// Export Sentry for use in error boundaries
export { Sentry };
