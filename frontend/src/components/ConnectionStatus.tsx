import { useCallback, useEffect, useMemo, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useBackendHealth } from '../hooks/useBackendHealth';

interface ConnectionStatusProps {
  /** Whether to show the status bar (e.g., hide on login page) */
  show?: boolean;
}

/**
 * Maximum expected connection timeout in milliseconds.
 * Backend is always on, so this covers network delays only.
 */
const CONNECTION_TIMEOUT_MS = 10000;

/**
 * Tips to show while the server is waking up
 */
const WAKE_UP_TIPS = [
  "☕ Server is brewing... almost ready!",
  "🌅 Waking up from sleep mode...",
  "⚡ Initializing services...",
  "🔄 Loading your experience...",
  "🚀 Preparing for launch...",
];

/**
 * Internal banner component that handles its own dismissed state.
 * Using a separate component with key prop allows resetting state on health changes.
 */
interface BannerContentProps {
  isWaking: boolean;
  message: string;
  onDismiss: () => void;
  onRetry?: () => void;
  retryCount: number;
  maxRetries: number;
}

const BannerContent = ({
  isWaking,
  message,
  onDismiss,
  onRetry,
  retryCount,
  maxRetries,
}: BannerContentProps) => {
  const [progress, setProgress] = useState(0);
  const [tipIndex, setTipIndex] = useState(0);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  // Simulate progress during wake-up
  useEffect(() => {
    if (!isWaking) {
      return;
    }

    const startTime = Date.now();

    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      // Use easing function for more realistic progress
      // Progress slows down as it approaches 100%
      const rawProgress = Math.min(elapsed / COLD_START_DURATION_MS, 0.95);
      const easedProgress = 1 - Math.pow(1 - rawProgress, 3); // Ease out cubic
      setProgress(Math.round(easedProgress * 100));
      setElapsedSeconds(Math.floor(elapsed / 1000));
    }, 200);

    return () => clearInterval(interval);
  }, [isWaking]);

  // Rotate tips every 8 seconds
  useEffect(() => {
    if (!isWaking) {
      return;
    }

    const tipInterval = setInterval(() => {
      setTipIndex((prev) => (prev + 1) % WAKE_UP_TIPS.length);
    }, 8000);

    return () => clearInterval(tipInterval);
  }, [isWaking]);

  // Calculate estimated remaining time
  const getEstimatedTime = () => {
    if (elapsedSeconds < 10) return "Less than a minute";
    if (elapsedSeconds < 30) return "About 30 seconds";
    if (elapsedSeconds < 45) return "Almost there...";
    return "Just a moment...";
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -50 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -50 }}
      transition={{ duration: 0.3 }}
      className="fixed top-0 left-0 right-0 z-50"
    >
      <div
        className={`px-4 py-3 ${
          isWaking
            ? 'bg-gradient-to-r from-blue-500 to-indigo-600'
            : 'bg-gradient-to-r from-red-500 to-red-600'
        } text-white shadow-lg`}
      >
        <div className="container mx-auto max-w-4xl">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-3 flex-1">
              {isWaking ? (
                <>
                  {/* Animated pulse icon */}
                  <div className="relative flex-shrink-0">
                    <motion.div
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                      className="text-2xl"
                    >
                      🌐
                    </motion.div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm sm:text-base">
                      {WAKE_UP_TIPS[tipIndex]}
                    </p>
                    <p className="text-xs sm:text-sm opacity-90 truncate">
                      {message || `${getEstimatedTime()} • Attempt ${Math.max(1, retryCount)}/${maxRetries}`}
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
                      {message || 'Unable to connect to server. Please check your connection.'}
                    </p>
                  </div>
                  {/* Retry button for error state */}
                  {onRetry && (
                    <button
                      onClick={onRetry}
                      className="px-3 py-1 bg-white/20 hover:bg-white/30 rounded-md transition-colors text-sm font-medium flex-shrink-0"
                    >
                      Retry
                    </button>
                  )}
                </>
              )}
            </div>

            {/* Dismiss button */}
            <button
              onClick={onDismiss}
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
          {isWaking && (
            <div className="mt-2">
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="flex items-center gap-1">
                  <motion.span
                    animate={{ opacity: [1, 0.5, 1] }}
                    transition={{ duration: 1, repeat: Infinity }}
                  >
                    ●
                  </motion.span>
                  Connecting...
                </span>
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
  );
};

/**
 * ConnectionStatus component displays a banner when the backend is slow or unavailable.
 * This helps users understand that the app is still working during connection attempts
 * (common with Render.com free tier) or network issues.
 */
const ConnectionStatus = ({ show = true }: ConnectionStatusProps) => {
  const health = useBackendHealth();
  const [dismissed, setDismissed] = useState(false);

  // Determine if we should show the banner based on health status
  const shouldShowBanner = !health.isHealthy || health.isWaking;

  // Handle dismiss button click
  const handleDismiss = useCallback(() => {
    setDismissed(true);
  }, []);

  // Create a unique key that changes when health status transitions to unhealthy
  // This causes the BannerContent to remount, resetting its state
  const bannerKey = useMemo(() => {
    // Only change key when we transition to unhealthy state
    if (shouldShowBanner && !dismissed) {
      return `banner-${health.lastCheck?.getTime() || 'initial'}`;
    }
    return 'hidden';
  }, [shouldShowBanner, dismissed, health.lastCheck]);

  // Reset dismissed when health becomes good (so banner shows on next issue)
  const isVisible = shouldShowBanner && !dismissed;
  
  // If health becomes good while banner is dismissed, reset dismissed for next time
  // We do this check during render to derive state rather than use an effect
  if (!shouldShowBanner && dismissed) {
    // Schedule state update for next render cycle
    setTimeout(() => setDismissed(false), 0);
  }

  // Don't render if not showing or healthy
  if (!show || !isVisible) {
    return null;
  }

  return (
    <AnimatePresence>
      <BannerContent
        key={bannerKey}
        isWaking={health.isWaking}
        message={health.message}
        onDismiss={handleDismiss}
        onRetry={health.retry}
        retryCount={health.retryCount}
        maxRetries={health.maxRetries}
      />
    </AnimatePresence>
  );
};

export default ConnectionStatus;
