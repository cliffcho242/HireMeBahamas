/**
 * Debug logger utility that only logs in development mode.
 * 
 * This logger prevents sensitive information from being logged in production
 * while still providing useful debugging information during development.
 */

// Check if we're in development mode
const isDevelopment = import.meta.env.DEV || 
  (typeof window !== 'undefined' && 
   (window.location.hostname === 'localhost' || 
    window.location.hostname === '127.0.0.1'));

/**
 * Debug logger that only logs in development mode.
 * Use this instead of console.log for debugging statements.
 */
export const debugLog = {
  /**
   * Log debug information (only in development)
   */
  log: (...args: unknown[]) => {
    if (isDevelopment) {
      console.log(...args);
    }
  },
  
  /**
   * Log warning information (only in development)
   */
  warn: (...args: unknown[]) => {
    if (isDevelopment) {
      console.warn(...args);
    }
  },
  
  /**
   * Log error information (only in development)
   * This function only logs in development mode for privacy/security.
   */
  error: (...args: unknown[]) => {
    if (isDevelopment) {
      console.error(...args);
    }
  },
  
  /**
   * Check if debug logging is enabled
   */
  isEnabled: () => isDevelopment,
};

export default debugLog;
