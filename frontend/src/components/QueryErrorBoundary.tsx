/**
 * QueryErrorBoundary - Error Boundary for React Query v5
 * 
 * This component wraps the QueryClientProvider to catch and handle
 * React Query errors properly with v5 API changes.
 * 
 * Features:
 * - React Query v5 compatible (throwOnError instead of useErrorBoundary)
 * - Edge Runtime compatible (no Node.js APIs)
 * - Graceful error recovery
 * - User-friendly error UI using ErrorFallback component
 */

import { Component, ErrorInfo, ReactNode } from 'react';
import ErrorFallback from './ErrorFallback';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onReset?: () => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class QueryErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to console for debugging
    console.error('QueryErrorBoundary caught an error:', error, errorInfo);

    // Update state with error info
    this.setState({
      error,
      errorInfo,
    });

    // You could also log the error to an error reporting service here
    // Example: logErrorToService(error, errorInfo);
  }

  handleReset = () => {
    // Call optional onReset callback
    if (this.props.onReset) {
      this.props.onReset();
    }

    // Reset the error boundary state
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI using ErrorFallback component
      return (
        <ErrorFallback
          error={this.state.error}
          onReset={this.handleReset}
          onGoHome={() => {
            // Reset error state first
            this.handleReset();
            // Use History API to navigate without full reload
            window.history.pushState({}, '', '/');
            // Trigger popstate event for React Router to detect navigation
            window.dispatchEvent(new PopStateEvent('popstate'));
          }}
          title="Oops! Something went wrong"
          message="We encountered an unexpected error. Please try again or refresh the page."
        />
      );
    }

    return this.props.children;
  }
}

export default QueryErrorBoundary;
