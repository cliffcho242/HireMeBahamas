import { useEffect, useState, useCallback, useRef } from 'react';
import api from '../services/api';

interface HealthStatus {
  isHealthy: boolean;
  isWaking: boolean;
  message: string;
  lastCheck: Date | null;
  retryCount: number;
  maxRetries: number;
}

// Configuration for health check retries
const HEALTH_CHECK_CONFIG = {
  pingTimeout: 5000,          // 5 seconds for quick ping
  initialTimeout: 10000,      // 10 seconds for first full check
  wakeUpTimeout: 30000,       // 30 seconds for wake-up retries
  retryDelays: [2000, 4000, 6000, 10000], // Progressive delays: 2s, 4s, 6s, 10s
  maxRetries: 4,
};

// Retry messages shown during wake-up
const RETRY_MESSAGES = [
  'Server is starting up...',
  'Still connecting, please wait...',
  'Almost there, hang tight...',
  'Final attempt, one moment...',
];

// Standalone async function for health check (outside component)
async function checkServerHealth(retryAttempt: number): Promise<{
  isHealthy: boolean;
  isWaking: boolean;
  message: string;
  retryCount: number;
  shouldScheduleRetry: boolean;
  retryDelay: number;
}> {
  const isRetry = retryAttempt > 0;

  try {
    // First, try the ultra-fast ping endpoint (no database dependency)
    if (!isRetry) {
      try {
        const pingResponse = await api.get('/health/ping', { 
          timeout: HEALTH_CHECK_CONFIG.pingTimeout 
        });
        // Accept any 200 response - backend may return "pong" (text) or {"status": "ok"} (JSON)
        if (pingResponse.status === 200) {
          return {
            isHealthy: true,
            isWaking: false,
            message: 'Connected',
            retryCount: 0,
            shouldScheduleRetry: false,
            retryDelay: 0,
          };
        }
      } catch {
        // Ping failed, continue to full health check
        console.log('Quick ping failed, trying full health check...');
      }
    }

    // Full health check with database validation
    const timeout = isRetry ? HEALTH_CHECK_CONFIG.wakeUpTimeout : HEALTH_CHECK_CONFIG.initialTimeout;
    const response = await api.get('/health', { timeout });
    
    // Accept various healthy status responses from the backend
    // Backend may return "healthy", "degraded", "alive", or "ok"
    const status = response.data?.status;
    const isHealthyStatus = status === 'healthy' || status === 'degraded' || status === 'alive' || status === 'ok';
    
    if (response.status === 200 && isHealthyStatus) {
      return {
        isHealthy: true,
        isWaking: false,
        message: 'Connected',
        retryCount: 0,
        shouldScheduleRetry: false,
        retryDelay: 0,
      };
    }
  } catch (error: unknown) {
    const apiError = error as { message?: string; code?: string; response?: { status?: number } };
    console.warn(`Backend health check failed (attempt ${retryAttempt + 1}):`, apiError.message);
    
    // Determine if this is a recoverable error (server sleeping/starting)
    const isRecoverable = 
      apiError.code === 'ECONNABORTED' || 
      apiError.code === 'ERR_NETWORK' ||
      apiError.code === 'ECONNREFUSED' ||
      apiError.response?.status === 503 ||
      apiError.response?.status === 502;

    if (isRecoverable && retryAttempt < HEALTH_CHECK_CONFIG.maxRetries) {
      const delay = HEALTH_CHECK_CONFIG.retryDelays[Math.min(retryAttempt, HEALTH_CHECK_CONFIG.retryDelays.length - 1)];
      return {
        isHealthy: false,
        isWaking: true,
        message: RETRY_MESSAGES[Math.min(retryAttempt, RETRY_MESSAGES.length - 1)],
        retryCount: retryAttempt + 1,
        shouldScheduleRetry: true,
        retryDelay: delay,
      };
    }
    
    return {
      isHealthy: false,
      isWaking: false,
      message: retryAttempt > 0 
        ? 'Server is taking longer than expected. Please refresh the page.'
        : 'Unable to connect to server. Please check your internet connection.',
      retryCount: retryAttempt,
      shouldScheduleRetry: false,
      retryDelay: 0,
    };
  }
  
  return {
    isHealthy: false,
    isWaking: false,
    message: 'Unexpected response from server',
    retryCount: retryAttempt,
    shouldScheduleRetry: false,
    retryDelay: 0,
  };
}

export const useBackendHealth = () => {
  const [health, setHealth] = useState<HealthStatus>({
    isHealthy: true,
    isWaking: false,
    message: '',
    lastCheck: null,
    retryCount: 0,
    maxRetries: HEALTH_CHECK_CONFIG.maxRetries,
  });

  // Use refs to track mounted state and pending timeouts
  const isMountedRef = useRef(true);
  const retryTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const checkInProgressRef = useRef(false);

  // Main check function
  const performCheck = useCallback(async (retryAttempt: number) => {
    if (!isMountedRef.current || checkInProgressRef.current) return;
    checkInProgressRef.current = true;

    try {
      const result = await checkServerHealth(retryAttempt);
      
      if (!isMountedRef.current) return;

      setHealth({
        isHealthy: result.isHealthy,
        isWaking: result.isWaking,
        message: result.message,
        lastCheck: new Date(),
        retryCount: result.retryCount,
        maxRetries: HEALTH_CHECK_CONFIG.maxRetries,
      });

      // Schedule retry if needed
      if (result.shouldScheduleRetry && isMountedRef.current) {
        retryTimeoutRef.current = setTimeout(() => {
          performCheck(result.retryCount);
        }, result.retryDelay);
      }
    } finally {
      checkInProgressRef.current = false;
    }
  }, []);

  // Initial check and periodic interval
  useEffect(() => {
    isMountedRef.current = true;
    
    // Initial check
    performCheck(0);

    // Periodic check every 5 minutes
    const intervalId = setInterval(() => {
      if (isMountedRef.current) {
        performCheck(0);
      }
    }, 5 * 60 * 1000);

    return () => {
      isMountedRef.current = false;
      clearInterval(intervalId);
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }
    };
  }, [performCheck]);

  // Manual retry function
  const retry = useCallback(() => {
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
      retryTimeoutRef.current = null;
    }
    performCheck(0);
  }, [performCheck]);

  return { ...health, retry };
};
