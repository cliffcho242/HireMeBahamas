/**
 * Centralized logging utility for HireMeBahamas frontend.
 * 
 * Features:
 * - Environment-aware logging (dev vs production)
 * - Structured log format
 * - Error tracking
 * - Performance monitoring
 * - Request/Response logging
 */

// Log levels
export enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARN = 'WARN',
  ERROR = 'ERROR',
}

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  context?: Record<string, any>;
  error?: Error;
}

interface LoggerConfig {
  enabled: boolean;
  minLevel: LogLevel;
  enableConsole: boolean;
  enableStorage: boolean;
  maxStoredLogs: number;
}

class Logger {
  private config: LoggerConfig;
  private logBuffer: LogEntry[] = [];

  constructor() {
    // Detect environment
    const isDevelopment = import.meta.env.DEV || 
      (typeof window !== 'undefined' && 
       (window.location.hostname === 'localhost' || 
        window.location.hostname === '127.0.0.1'));

    // Configure logger based on environment
    this.config = {
      enabled: true,
      minLevel: isDevelopment ? LogLevel.DEBUG : LogLevel.INFO,
      enableConsole: true,
      enableStorage: isDevelopment, // Only store logs in development
      maxStoredLogs: 100,
    };
  }

  /**
   * Check if a log level should be logged
   */
  private shouldLog(level: LogLevel): boolean {
    if (!this.config.enabled) return false;

    const levels = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARN, LogLevel.ERROR];
    const minLevelIndex = levels.indexOf(this.config.minLevel);
    const currentLevelIndex = levels.indexOf(level);

    return currentLevelIndex >= minLevelIndex;
  }

  /**
   * Format a log entry
   */
  private formatLog(entry: LogEntry): string {
    const { timestamp, level, message, context } = entry;
    let formatted = `[${timestamp}] [${level}] ${message}`;

    if (context && Object.keys(context).length > 0) {
      formatted += ` ${JSON.stringify(context)}`;
    }

    return formatted;
  }

  /**
   * Store log entry in buffer
   */
  private storeLog(entry: LogEntry): void {
    if (!this.config.enableStorage) return;

    this.logBuffer.push(entry);

    // Keep buffer size under limit
    if (this.logBuffer.length > this.config.maxStoredLogs) {
      this.logBuffer.shift();
    }
  }

  /**
   * Log to console based on level
   */
  private logToConsole(entry: LogEntry): void {
    if (!this.config.enableConsole) return;

    const formatted = this.formatLog(entry);

    switch (entry.level) {
      case LogLevel.DEBUG:
        console.debug(formatted, entry.context || '');
        break;
      case LogLevel.INFO:
        console.info(formatted, entry.context || '');
        break;
      case LogLevel.WARN:
        console.warn(formatted, entry.context || '');
        break;
      case LogLevel.ERROR:
        console.error(formatted, entry.context || '', entry.error || '');
        break;
    }
  }

  /**
   * Core logging method
   */
  private log(level: LogLevel, message: string, context?: Record<string, any>, error?: Error): void {
    if (!this.shouldLog(level)) return;

    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      context,
      error,
    };

    this.storeLog(entry);
    this.logToConsole(entry);
  }

  /**
   * Log debug message
   */
  debug(message: string, context?: Record<string, any>): void {
    this.log(LogLevel.DEBUG, message, context);
  }

  /**
   * Log info message
   */
  info(message: string, context?: Record<string, any>): void {
    this.log(LogLevel.INFO, message, context);
  }

  /**
   * Log warning message
   */
  warn(message: string, context?: Record<string, any>): void {
    this.log(LogLevel.WARN, message, context);
  }

  /**
   * Log error message
   */
  error(message: string, error?: Error, context?: Record<string, any>): void {
    this.log(LogLevel.ERROR, message, { ...context }, error);
  }

  /**
   * Log API request
   */
  logRequest(method: string, url: string, data?: any): void {
    this.debug(`API Request: ${method} ${url}`, { method, url, data });
  }

  /**
   * Log API response
   */
  logResponse(method: string, url: string, status: number, duration?: number): void {
    const context: Record<string, any> = { method, url, status };
    if (duration !== undefined) {
      context.duration = `${duration}ms`;
    }

    if (status >= 400) {
      this.warn(`API Response: ${method} ${url} ${status}`, context);
    } else {
      this.debug(`API Response: ${method} ${url} ${status}`, context);
    }
  }

  /**
   * Log API error
   */
  logApiError(method: string, url: string, error: any): void {
    const context: Record<string, any> = { 
      method, 
      url,
      status: error?.response?.status,
      statusText: error?.response?.statusText,
    };

    this.error(
      `API Error: ${method} ${url}`,
      error instanceof Error ? error : new Error(String(error)),
      context
    );
  }

  /**
   * Log performance metric
   */
  logPerformance(operation: string, duration: number, threshold?: number): void {
    const context = { operation, duration: `${duration}ms` };

    if (threshold && duration > threshold) {
      this.warn(`Performance: ${operation} took ${duration}ms (threshold: ${threshold}ms)`, context);
    } else {
      this.debug(`Performance: ${operation} took ${duration}ms`, context);
    }
  }

  /**
   * Get stored logs
   */
  getLogs(): LogEntry[] {
    return [...this.logBuffer];
  }

  /**
   * Clear stored logs
   */
  clearLogs(): void {
    this.logBuffer = [];
  }

  /**
   * Export logs as JSON
   */
  exportLogs(): string {
    return JSON.stringify(this.logBuffer, null, 2);
  }

  /**
   * Configure logger
   */
  configure(config: Partial<LoggerConfig>): void {
    this.config = { ...this.config, ...config };
  }
}

// Global logger instance
const logger = new Logger();

// Export logger instance and types
export { logger, Logger };
export type { LogEntry, LoggerConfig };

// Convenience exports
export const logRequest = logger.logRequest.bind(logger);
export const logResponse = logger.logResponse.bind(logger);
export const logApiError = logger.logApiError.bind(logger);
export const logPerformance = logger.logPerformance.bind(logger);

// Default export
export default logger;
