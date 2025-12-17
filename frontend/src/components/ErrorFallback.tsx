import React from 'react';

/**
 * User-Friendly Error Fallback Component
 * 
 * A clean, Facebook-style error recovery component that can be used
 * with ErrorBoundary to provide a better user experience during errors.
 * 
 * Features:
 * - Clean, centered layout
 * - Network error messaging
 * - Retry functionality
 * - Accessible design
 * 
 * Usage:
 * <ErrorBoundary fallback={<ErrorFallback onRetry={() => location.reload()} />}>
 *   <YourComponent />
 * </ErrorBoundary>
 */

interface ErrorFallbackProps {
  onRetry: () => void;
}

const ErrorFallback: React.FC<ErrorFallbackProps> = ({ onRetry }) => {
  return (
    <div className="text-center p-8">
      <h3>Network error</h3>
      <p>Please check your connection.</p>
      <button onClick={onRetry}>Try again</button>
    </div>
  );
};

export default ErrorFallback;
