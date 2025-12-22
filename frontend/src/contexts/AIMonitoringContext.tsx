/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable react-hooks/exhaustive-deps */
/* eslint-disable react-refresh/only-export-components */
// AI Monitoring uses dynamic window object access and complex hook dependencies
import { ReactNode, createContext, useCallback, useContext, useEffect, useState } from 'react';
import { API_BASE_URL, apiUrl } from '../lib/api';
interface SystemHealth {
  frontend: boolean;
  backend: boolean;
  network: boolean;
  memory: boolean;
  lastCheck: Date;
  errors: string[];
  recoveryAttempts: number;
}

interface AIMonitoringContextType {
  health: SystemHealth;
  isMonitoring: boolean;
  lastError: string | null;
  performHealthCheck: () => Promise<void>;
  reportError: (error: Error, context?: string) => void;
  attemptRecovery: () => Promise<boolean>;
  getSystemStatus: () => 'healthy' | 'degraded' | 'critical' | 'offline';
}

const AIMonitoringContext = createContext<AIMonitoringContextType | undefined>(undefined);

export const useAIMonitoring = () => {
  const context = useContext(AIMonitoringContext);
  if (!context) {
    throw new Error('useAIMonitoring must be used within AIMonitoringProvider');
  }
  return context;
};

interface AIMonitoringProviderProps {
  children: ReactNode;
  backendUrl?: string;
  checkInterval?: number; // in milliseconds
  maxRecoveryAttempts?: number;
}

export const AIMonitoringProvider = ({
  children,
  backendUrl = API_BASE_URL,
  checkInterval = 30000, // 30 seconds
  maxRecoveryAttempts = 3
}: AIMonitoringProviderProps) => {
  const [health, setHealth] = useState<SystemHealth>({
    frontend: true,
    backend: false,
    network: navigator.onLine,
    memory: true,
    lastCheck: new Date(),
    errors: [],
    recoveryAttempts: 0
  });

  const [isMonitoring] = useState(true);
  const [lastError, setLastError] = useState<string | null>(null);

  // AI-powered health check with intelligent analysis
  const performHealthCheck = useCallback(async () => {
    const startTime = Date.now();
    const newHealth = { ...health };

    try {
      // Check frontend (self-check)
      newHealth.frontend = true;

      // Check backend connectivity
      try {
        const healthUrl = apiUrl('/health');
        const backendResponse = await fetch(healthUrl, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
          signal: AbortSignal.timeout(5000) // 5 second timeout
        });

        newHealth.backend = backendResponse.ok;
        if (!backendResponse.ok) {
          throw new Error(`Backend returned ${backendResponse.status}`);
        }
      } catch (error) {
        newHealth.backend = false;
        newHealth.errors.push(`Backend check failed: ${(error as Error).message}`);
      }

      // Check network connectivity
      newHealth.network = navigator.onLine;

      // Check memory usage (basic)
      const memoryInfo = (performance as any).memory;
      if (memoryInfo) {
        const memoryUsagePercent = (memoryInfo.usedJSHeapSize / memoryInfo.totalJSHeapSize) * 100;
        newHealth.memory = memoryUsagePercent < 90; // Consider unhealthy if >90% memory usage
        if (memoryUsagePercent > 80) {
          newHealth.errors.push(`High memory usage: ${memoryUsagePercent.toFixed(1)}%`);
        }
      }

      newHealth.lastCheck = new Date();

      // AI analysis: Determine if system needs attention
      const criticalErrors = newHealth.errors.filter(error =>
        error.includes('Backend') || error.includes('network') || error.includes('memory')
      );

      if (criticalErrors.length > 0 && newHealth.recoveryAttempts < maxRecoveryAttempts) {
        const recovered = await attemptRecovery();
        if (recovered) {
          newHealth.errors = newHealth.errors.filter(error => !criticalErrors.includes(error));
          // AI system recovery successful - working silently in background
          console.log('🤖 AI System: Auto-recovery successful (silent mode)');
        }
      }

      setHealth(newHealth);
      setLastError(null);

    } catch (error) {
      const errorMessage = `Health check failed: ${(error as Error).message}`;
      setLastError(errorMessage);
      newHealth.errors.push(errorMessage);
      setHealth(newHealth);

      // AI decision: Attempt recovery if this is a persistent issue
      if (newHealth.errors.length > 3) {
        // AI system initiating recovery - working silently in background
        console.log('🤖 AI System: Multiple failures detected. Initiating recovery protocol (silent mode)...');
        attemptRecovery();
      }
    }

    const checkDuration = Date.now() - startTime;
    if (checkDuration > 5000) {
      console.warn(`🤖 AI Monitor: Health check took ${checkDuration}ms - potential performance issue`);
    }
  }, [health, backendUrl, maxRecoveryAttempts]);

  // AI-powered error reporting with context analysis
  const reportError = useCallback((error: Error, context?: string) => {
    const errorInfo = {
      message: error.message,
      stack: error.stack,
      context: context || 'unknown',
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    };

    console.error('🤖 AI Error Report:', errorInfo);

    // AI analysis: Categorize error severity
    let severity: 'low' | 'medium' | 'high' | 'critical' = 'medium';

    if (error.message.includes('network') || error.message.includes('fetch')) {
      severity = 'high';
    } else if (error.message.includes('auth') || error.message.includes('token')) {
      severity = 'high';
    } else if (error.stack?.includes('TypeError') || error.stack?.includes('ReferenceError')) {
      severity = 'critical';
    }

    // AI decision: Show appropriate user notification
    switch (severity) {
      case 'critical':
        console.log(`AI System: Critical Error - ${error.message}. Attempting auto-fix...`);
        attemptRecovery();
        break;
      case 'high':
        console.log(`AI System: System Error - ${error.message}. Monitoring closely...`);
        break;
      case 'medium':
        console.log(`AI System: Notice - ${error.message}`);
        break;
      default:
        console.log(`AI System: Log - ${error.message}`);
    }

    // Update health status
    setHealth(prev => ({
      ...prev,
      errors: [...prev.errors.slice(-9), `${severity}: ${error.message}`] // Keep last 10 errors
    }));

  }, []);

  // AI-powered recovery system
  const attemptRecovery = useCallback(async (): Promise<boolean> => {
    console.log('🤖 AI Recovery: Initiating system recovery protocol...');

    setHealth(prev => ({ ...prev, recoveryAttempts: prev.recoveryAttempts + 1 }));

    try {
      // Recovery Strategy 1: Clear local storage issues
      if (health.errors.some(e => e.includes('auth') || e.includes('token'))) {
        localStorage.removeItem('token');
        console.log('🤖 AI Recovery: Cleared invalid auth tokens');
      }

      // Recovery Strategy 2: Force refresh backend connection
      if (!health.backend) {
        console.log('🤖 AI Recovery: Testing backend connectivity...');
        try {
          const healthUrl = apiUrl('/health');
          const response = await fetch(healthUrl, {
            method: 'GET',
            cache: 'no-cache'
          });
          if (response.ok) {
            setHealth(prev => ({ ...prev, backend: true }));
            console.log('🤖 AI Recovery: Backend connection restored');
          }
        } catch {
          console.log('🤖 AI Recovery: Backend still unreachable');
        }
      }

      // Recovery Strategy 3: Memory cleanup
      if (!health.memory) {
        console.log('🤖 AI Recovery: Performing memory cleanup...');
        // Force garbage collection if available
        if ((window as any).gc) {
          (window as any).gc();
        }
        // Clear any cached data
        localStorage.removeItem('temp_data');
        sessionStorage.clear();
      }

      // Recovery Strategy 4: Network recovery
      if (!health.network) {
        console.log('🤖 AI Recovery: Checking network status...');
        // This will be updated by the network event listeners
      }

      // AI decision: If recovery successful, reset error count
      const isHealthy = health.frontend && health.backend && health.network && health.memory;

      if (isHealthy) {
        setHealth(prev => ({ ...prev, errors: [], recoveryAttempts: 0 }));
        return true;
      }

      return false;

    } catch (error) {
      console.error('🤖 AI Recovery: Recovery attempt failed:', error);
      return false;
    }
  }, [health, backendUrl, performHealthCheck]);

  // Get overall system status with AI analysis
  const getSystemStatus = useCallback((): 'healthy' | 'degraded' | 'critical' | 'offline' => {
    const criticalCount = [
      !health.frontend,
      !health.backend,
      !health.network,
      !health.memory
    ].filter(Boolean).length;

    const errorCount = health.errors.length;

    if (!health.network) return 'offline';
    if (criticalCount > 1 || errorCount > 5) return 'critical';
    if (criticalCount > 0 || errorCount > 2) return 'degraded';
    return 'healthy';
  }, [health]);

  // Set up monitoring intervals and event listeners
  useEffect(() => {
    if (!isMonitoring) return;

    // Regular health checks
    const interval = setInterval(performHealthCheck, checkInterval);

    // Network status monitoring
    const handleOnline = () => {
      setHealth(prev => ({ ...prev, network: true }));
      console.log('AI System: Network connection restored');
      performHealthCheck();
    };

    const handleOffline = () => {
      setHealth(prev => ({ ...prev, network: false }));
      console.log('AI System: Network connection lost');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Global error handling
    const handleGlobalError = (event: ErrorEvent) => {
      reportError(new Error(event.message), 'global');
    };

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      reportError(new Error(`Unhandled promise rejection: ${event.reason}`), 'promise');
    };

    window.addEventListener('error', handleGlobalError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    // Initial health check
    performHealthCheck();

    return () => {
      clearInterval(interval);
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      window.removeEventListener('error', handleGlobalError);
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, [isMonitoring, checkInterval, performHealthCheck, reportError]);

  const value: AIMonitoringContextType = {
    health,
    isMonitoring,
    lastError,
    performHealthCheck,
    reportError,
    attemptRecovery,
    getSystemStatus
  };

  return (
    <AIMonitoringContext.Provider value={value}>
      {children}
    </AIMonitoringContext.Provider>
  );
};
