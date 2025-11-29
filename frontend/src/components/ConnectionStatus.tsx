import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useBackendHealth } from '../hooks/useBackendHealth';

interface ConnectionStatusProps {
  /** Whether to show the status bar (e.g., hide on login page) */
  show?: boolean;
}

/**
 * ConnectionStatus component displays a banner when the backend is slow or unavailable.
 * This helps users understand that the app is still working during cold starts
 * (common with Render.com free tier) or network issues.
 */
const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ show = true }) => {
  const health = useBackendHealth();
  const [dismissed, setDismissed] = useState(false);
  const [progress, setProgress] = useState(0);

  // Determine if we should show the banner based on health status
  const shouldShowBanner = !health.isHealthy || health.isWaking;

  // Reset dismissed state when backend becomes unhealthy/waking after being healthy
  // This is triggered asynchronously via the effect cleanup to avoid lint warnings
  useEffect(() => {
    if (shouldShowBanner) {
      // When we need to show banner, reset dismissed after a microtask
      // to ensure we show the banner again for new issues
      const timeout = setTimeout(() => {
        setDismissed(false);
        setProgress(0);
      }, 0);
      return () => clearTimeout(timeout);
    }
  }, [shouldShowBanner]);

  // Simulate progress during wake-up (max ~60 seconds for cold start)
  useEffect(() => {
    if (!health.isWaking) {
      return;
    }

    const startTime = Date.now();
    const maxDuration = 60000; // 60 seconds max

    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      // Use easing function for more realistic progress
      // Progress slows down as it approaches 100%
      const rawProgress = Math.min(elapsed / maxDuration, 0.95);
      const easedProgress = 1 - Math.pow(1 - rawProgress, 3); // Ease out cubic
      setProgress(Math.round(easedProgress * 100));
    }, 200);

    return () => clearInterval(interval);
  }, [health.isWaking]);

  // Don't render if not showing, dismissed, or healthy
  if (!show || dismissed || !shouldShowBanner) {
    return null;
  }

  const handleDismiss = () => {
    setDismissed(true);
  };

  return (
    <AnimatePresence>
      {(health.isWaking || !health.isHealthy) && !dismissed && (
        <motion.div
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -50 }}
          transition={{ duration: 0.3 }}
          className="fixed top-0 left-0 right-0 z-50"
        >
          <div
            className={`px-4 py-3 ${
              health.isWaking
                ? 'bg-gradient-to-r from-amber-500 to-orange-500'
                : 'bg-gradient-to-r from-red-500 to-red-600'
            } text-white shadow-lg`}
          >
            <div className="container mx-auto max-w-4xl">
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-3 flex-1">
                  {health.isWaking ? (
                    <>
                      {/* Animated spinner */}
                      <div className="relative">
                        <svg
                          className="animate-spin h-5 w-5 text-white"
                          xmlns="http://www.w3.org/2000/svg"
                          fill="none"
                          viewBox="0 0 24 24"
                        >
                          <circle
                            className="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            strokeWidth="4"
                          />
                          <path
                            className="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                          />
                        </svg>
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-sm sm:text-base">
                          Connecting to server...
                        </p>
                        <p className="text-xs sm:text-sm opacity-90">
                          {health.message || 'The server may take up to 60 seconds to wake up.'}
                        </p>
                      </div>
                    </>
                  ) : (
                    <>
                      {/* Error icon */}
                      <svg
                        className="h-5 w-5 text-white flex-shrink-0"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                        />
                      </svg>
                      <div className="flex-1">
                        <p className="font-medium text-sm sm:text-base">
                          Connection issue
                        </p>
                        <p className="text-xs sm:text-sm opacity-90">
                          {health.message || 'Unable to connect to server. Please check your connection.'}
                        </p>
                      </div>
                    </>
                  )}
                </div>

                {/* Dismiss button */}
                <button
                  onClick={handleDismiss}
                  className="p-1 hover:bg-white/20 rounded-full transition-colors flex-shrink-0"
                  aria-label="Dismiss"
                >
                  <svg
                    className="h-5 w-5"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>

              {/* Progress bar for waking state */}
              {health.isWaking && (
                <div className="mt-2">
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span>Establishing connection...</span>
                    <span>{progress}%</span>
                  </div>
                  <div className="h-1.5 bg-white/30 rounded-full overflow-hidden">
                    <motion.div
                      className="h-full bg-white rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${progress}%` }}
                      transition={{ duration: 0.2 }}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default ConnectionStatus;
