import { useEffect, useState } from 'react';
import api from '../services/api';

interface HealthStatus {
  isHealthy: boolean;
  isWaking: boolean;
  message: string;
  lastCheck: Date | null;
}

export const useBackendHealth = () => {
  const [health, setHealth] = useState<HealthStatus>({
    isHealthy: true,
    isWaking: false,
    message: '',
    lastCheck: null,
  });

  useEffect(() => {
    let isChecking = false;

    const checkHealth = async () => {
      if (isChecking) return;
      isChecking = true;

      try {
        const response = await api.get('/health', { timeout: 10000 });
        
        if (response.status === 200 && response.data.status === 'healthy') {
          setHealth({
            isHealthy: true,
            isWaking: false,
            message: 'Connected',
            lastCheck: new Date(),
          });
        }
      } catch (error: any) {
        console.warn('Backend health check failed:', error.message);
        
        // Backend might be sleeping (Render.com free tier)
        if (error.code === 'ECONNABORTED' || error.code === 'ERR_NETWORK') {
          setHealth({
            isHealthy: false,
            isWaking: true,
            message: 'Server is waking up... Please wait 30 seconds.',
            lastCheck: new Date(),
          });
          
          // Try to wake it up
          setTimeout(() => checkHealth(), 5000);
        } else {
          setHealth({
            isHealthy: false,
            isWaking: false,
            message: 'Server connection issue',
            lastCheck: new Date(),
          });
        }
      } finally {
        isChecking = false;
      }
    };

    // Check on mount
    checkHealth();

    // Check every 5 minutes
    const checkInterval = setInterval(checkHealth, 5 * 60 * 1000);

    return () => {
      if (checkInterval) clearInterval(checkInterval);
    };
  }, []);

  return health;
};
