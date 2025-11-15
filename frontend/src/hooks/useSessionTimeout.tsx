import { useEffect, useState, useCallback } from 'react';
import { sessionManager } from '../services/sessionManager';
import toast from 'react-hot-toast';

interface UseSessionTimeoutOptions {
  onExpiring?: () => void;
  onExpired?: () => void;
  showWarning?: boolean;
}

export const useSessionTimeout = (options: UseSessionTimeoutOptions = {}) => {
  const { onExpiring, onExpired, showWarning = true } = options;
  const [timeRemaining, setTimeRemaining] = useState<number>(0);
  const [isExpiring, setIsExpiring] = useState(false);

  // Update remaining time periodically
  useEffect(() => {
    const updateTime = () => {
      const remaining = sessionManager.getRemainingTime();
      setTimeRemaining(remaining);
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);

    return () => clearInterval(interval);
  }, []);

  // Handle session expiring warning
  const handleExpiring = useCallback(() => {
    setIsExpiring(true);
    
    if (showWarning) {
      toast(
        (t) => (
          <div className="flex flex-col space-y-2">
            <p className="font-medium">Session Expiring Soon</p>
            <p className="text-sm text-gray-600">
              Your session will expire in 5 minutes due to inactivity.
            </p>
            <div className="flex space-x-2">
              <button
                onClick={() => {
                  sessionManager.extendSession();
                  setIsExpiring(false);
                  toast.dismiss(t.id);
                  toast.success('Session extended!');
                }}
                className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
              >
                Stay Logged In
              </button>
              <button
                onClick={() => toast.dismiss(t.id)}
                className="px-3 py-1 bg-gray-200 text-gray-800 rounded text-sm hover:bg-gray-300"
              >
                Dismiss
              </button>
            </div>
          </div>
        ),
        {
          duration: Infinity,
          icon: '⏰',
        }
      );
    }

    if (onExpiring) {
      onExpiring();
    }
  }, [showWarning, onExpiring]);

  // Handle session expired
  const handleExpired = useCallback(() => {
    setIsExpiring(false);
    
    if (showWarning) {
      toast.error('Your session has expired. Please log in again.', {
        duration: 5000,
      });
    }

    if (onExpired) {
      onExpired();
    }
  }, [showWarning, onExpired]);

  // Register callbacks with session manager
  useEffect(() => {
    sessionManager.onExpiring(handleExpiring);
    sessionManager.onExpired(handleExpired);
  }, [handleExpiring, handleExpired]);

  // Extend session manually
  const extendSession = useCallback(() => {
    sessionManager.extendSession();
    setIsExpiring(false);
  }, []);

  // Format time remaining
  const formatTimeRemaining = useCallback((ms: number): string => {
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  }, []);

  return {
    timeRemaining,
    isExpiring,
    extendSession,
    formatTimeRemaining,
    formattedTime: formatTimeRemaining(timeRemaining),
  };
};
