/**
 * ErrorFallback - Reusable Error Fallback Component
 * 
 * A user-friendly error recovery component that can be used by error boundaries
 * to provide consistent error handling across the application.
 * 
 * Features:
 * - User-friendly error messages
 * - Multiple recovery actions (retry, go home, reload)
 * - Error details in development mode
 * - Accessibility support (ARIA labels, keyboard navigation)
 * - Responsive design
 * - Customizable appearance and actions
 */

import React from 'react';

export interface ErrorFallbackProps {
  /** The error that was caught */
  error: Error | null;
  
  /** Optional error ID for tracking */
  errorId?: string | null;
  
  /** Callback to reset the error boundary and retry */
  onReset?: () => void;
  
  /** Callback to navigate to home page */
  onGoHome?: () => void;
  
  /** Custom title for the error */
  title?: string;
  
  /** Custom message for the error */
  message?: string;
  
  /** Whether to show error details in development */
  showDetails?: boolean;
  
  /** Additional CSS classes */
  className?: string;
  
  /** Icon variant */
  iconVariant?: 'warning' | 'error' | 'info';
}

const ErrorFallback: React.FC<ErrorFallbackProps> = ({
  error,
  errorId,
  onReset,
  onGoHome,
  title = 'Oops! Something went wrong',
  message = 'We encountered an unexpected error. Please try again or refresh the page.',
  showDetails = true,
  className = '',
  iconVariant = 'error',
}) => {
  const handleReload = () => {
    window.location.reload();
  };

  const handleGoHome = () => {
    if (onGoHome) {
      onGoHome();
    } else {
      // Default: Use History API to navigate without full reload
      window.history.pushState({}, '', '/');
      window.dispatchEvent(new PopStateEvent('popstate'));
    }
  };

  // Icon colors based on variant
  const iconColors = {
    error: 'bg-red-100 text-red-600',
    warning: 'bg-orange-100 text-orange-600',
    info: 'bg-blue-100 text-blue-600',
  };

  return (
    <div 
      className={`min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 flex items-center justify-center p-4 ${className}`}
      role="alert"
      aria-live="assertive"
    >
      <div className="max-w-md w-full bg-white rounded-xl shadow-2xl p-8">
        <div className="text-center">
          {/* Error Icon */}
          <div 
            className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 ${iconColors[iconVariant]}`}
            aria-hidden="true"
          >
            <svg
              className="w-8 h-8"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
          </div>

          {/* Error Title */}
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            {title}
          </h2>

          {/* Error Message */}
          <p className="text-gray-600 mb-6">
            {message}
          </p>

          {/* Error Details (only in development) */}
          {showDetails && import.meta.env.DEV && error && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg text-left">
              <p className="text-xs font-semibold text-gray-700 mb-2">
                Error Details (Development Only):
              </p>
              <pre className="text-xs text-red-600 overflow-auto max-h-40 whitespace-pre-wrap break-words">
                {error.message}
              </pre>
              {error.stack && (
                <details className="mt-2">
                  <summary className="text-xs text-gray-600 cursor-pointer hover:text-gray-800">
                    Stack Trace
                  </summary>
                  <pre className="text-xs text-gray-500 overflow-auto max-h-40 mt-2 whitespace-pre-wrap break-words">
                    {error.stack}
                  </pre>
                </details>
              )}
            </div>
          )}

          {/* Error ID */}
          {errorId && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <p className="text-xs text-gray-500 mb-2">Error ID for Support:</p>
              <p className="text-xs font-mono text-gray-700 break-all select-all">
                {errorId}
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="space-y-3">
            {onReset && (
              <button
                onClick={onReset}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 shadow-sm"
                aria-label="Try again"
              >
                🔄 Try Again
              </button>
            )}

            <button
              onClick={handleReload}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-3 px-6 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 shadow-sm"
              aria-label="Refresh page"
            >
              ↻ Refresh Page
            </button>

            <button
              onClick={handleGoHome}
              className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-3 px-6 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
              aria-label="Go to home page"
            >
              🏠 Go to Home
            </button>
          </div>

          {/* Help Text */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-500 mb-2">
              If the problem persists, please:
            </p>
            <ul className="text-sm text-gray-500 space-y-1 text-left">
              <li>• Clear your browser cache</li>
              <li>• Try a different browser</li>
              <li>• Contact support if needed</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ErrorFallback;
