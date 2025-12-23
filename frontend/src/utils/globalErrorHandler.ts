/**
 * Global Error Handler
 * 
 * Catches and logs all unhandled errors and promise rejections
 * to help diagnose blank screen issues and runtime errors.
 */

import * as Sentry from '@sentry/react';

interface ErrorInfo {
  message: string;
  stack?: string;
  type: 'error' | 'unhandledRejection';
  timestamp: string;
  userAgent: string;
  url: string;
}

/**
 * Initialize global error handlers
 * Call this once at app startup
 */
export function initGlobalErrorHandler(): void {
  // Handle uncaught errors
  window.addEventListener('error', (event: ErrorEvent) => {
    const errorInfo: ErrorInfo = {
      message: event.message,
      stack: event.error?.stack,
      type: 'error',
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
    };

    logError('Uncaught Error', errorInfo, event.error);
    
    // Prevent default browser error handling
    event.preventDefault();
  });

  // Handle unhandled promise rejections
  window.addEventListener('unhandledrejection', (event: PromiseRejectionEvent) => {
    const errorInfo: ErrorInfo = {
      message: event.reason?.message || String(event.reason),
      stack: event.reason?.stack,
      type: 'unhandledRejection',
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
    };

    logError('Unhandled Promise Rejection', errorInfo, event.reason);
    
    // Prevent default browser error handling
    event.preventDefault();
  });

  // Log successful initialization
  console.log('✅ Global error handler initialized');
}

/**
 * Log error to console and send to Sentry
 */
function logError(title: string, errorInfo: ErrorInfo, originalError?: Error): void {
  // Always log to console for debugging
  console.group(`❌ ${title}`);
  console.error('Message:', errorInfo.message);
  console.error('Type:', errorInfo.type);
  console.error('Timestamp:', errorInfo.timestamp);
  console.error('URL:', errorInfo.url);
  
  if (errorInfo.stack) {
    console.error('Stack:', errorInfo.stack);
  }
  
  if (originalError) {
    console.error('Original Error:', originalError);
  }
  
  console.groupEnd();

  // Send to Sentry in production
  if (!import.meta.env.DEV) {
    Sentry.captureException(originalError || new Error(errorInfo.message), {
      contexts: {
        errorInfo: {
          ...errorInfo,
        },
      },
      tags: {
        errorType: errorInfo.type,
      },
    });
  }

  // Store error in localStorage for debugging
  storeErrorForDebugging(errorInfo);
}

/**
 * Store recent errors in localStorage for debugging
 * Keeps last 10 errors
 */
function storeErrorForDebugging(errorInfo: ErrorInfo): void {
  try {
    const storageKey = 'hiremebahamas_recent_errors';
    const existing = localStorage.getItem(storageKey);
    const errors = existing ? JSON.parse(existing) : [];
    
    // Add new error
    errors.unshift(errorInfo);
    
    // Keep only last 10 errors
    const recentErrors = errors.slice(0, 10);
    
    // Save back to localStorage
    localStorage.setItem(storageKey, JSON.stringify(recentErrors));
  } catch (error) {
    // Silently fail if localStorage is not available
    console.warn('Failed to store error in localStorage:', error);
  }
}

/**
 * Get recent errors from localStorage
 * Useful for debugging
 */
export function getRecentErrors(): ErrorInfo[] {
  try {
    const storageKey = 'hiremebahamas_recent_errors';
    const existing = localStorage.getItem(storageKey);
    return existing ? JSON.parse(existing) : [];
  } catch (error) {
    console.warn('Failed to retrieve errors from localStorage:', error);
    return [];
  }
}

/**
 * Clear stored errors
 */
export function clearStoredErrors(): void {
  try {
    const storageKey = 'hiremebahamas_recent_errors';
    localStorage.removeItem(storageKey);
    console.log('✅ Cleared stored errors');
  } catch (error) {
    console.warn('Failed to clear errors from localStorage:', error);
  }
}

/**
 * Display stored errors in console
 * Useful for debugging
 */
export function displayStoredErrors(): void {
  const errors = getRecentErrors();
  
  if (errors.length === 0) {
    console.log('ℹ️ No stored errors found');
    return;
  }

  console.group(`📋 Recent Errors (${errors.length})`);
  errors.forEach((error, index) => {
    console.group(`Error ${index + 1} - ${error.timestamp}`);
    console.log('Type:', error.type);
    console.log('Message:', error.message);
    console.log('URL:', error.url);
    if (error.stack) {
      console.log('Stack:', error.stack);
    }
    console.groupEnd();
  });
  console.groupEnd();
}

// Make debug functions available globally for debugging
if (typeof window !== 'undefined') {
  (window as any).debugErrors = {
    getRecent: getRecentErrors,
    display: displayStoredErrors,
    clear: clearStoredErrors,
  };
}
