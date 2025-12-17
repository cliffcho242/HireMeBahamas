/* eslint-disable @typescript-eslint/no-explicit-any */
// Error boundary uses dynamic window.gc and analysis objects
import { Component, ErrorInfo, ReactNode } from 'react';
import { useAIMonitoring } from '../contexts/AIMonitoringContext';
import ErrorFallback from './ErrorFallback';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorId: string | null;
  recoveryAttempted: boolean;
}

class AIErrorBoundaryClass extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorId: null,
      recoveryAttempted: false
    };
  }

  static getDerivedStateFromError(error: Error): State {
    // Generate unique error ID for tracking
    const errorId = `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    return {
      hasError: true,
      error,
      errorId,
      recoveryAttempted: false
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // AI-powered error analysis (silent operation)
    const errorAnalysis = this.analyzeError(error, errorInfo);

    console.log('🤖 AI Error Boundary: Error detected (silent mode)', {
      error: error.message,
      analysis: errorAnalysis,
      errorId: this.state.errorId
    });

    // Automatically attempt recovery without user interaction
    this.attemptRecovery(error, errorAnalysis);

    // Report to monitoring system
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  analyzeError(error: Error, errorInfo: ErrorInfo) {
    const analysis = {
      severity: 'medium' as 'low' | 'medium' | 'high' | 'critical',
      recoverable: false,
      category: 'unknown' as string,
      suggestedAction: 'reload' as string
    };

    const message = error.message.toLowerCase();
    const stack = error.stack?.toLowerCase() || '';
    const componentStack = errorInfo.componentStack?.toLowerCase() || '';

    // AI analysis: Categorize error type
    if (message.includes('network') || message.includes('fetch') || message.includes('api')) {
      analysis.category = 'network';
      analysis.recoverable = true;
      analysis.suggestedAction = 'retry';
    } else if (message.includes('auth') || message.includes('token') || message.includes('unauthorized')) {
      analysis.category = 'authentication';
      analysis.recoverable = true;
      analysis.suggestedAction = 'relogin';
    } else if (stack.includes('typeerror') || stack.includes('referenceerror') || stack.includes('null')) {
      analysis.category = 'runtime';
      analysis.severity = 'high';
      analysis.recoverable = false;
    } else if (componentStack.includes('router') || message.includes('route')) {
      analysis.category = 'routing';
      analysis.recoverable = true;
      analysis.suggestedAction = 'navigate_home';
    } else if (message.includes('memory') || message.includes('heap')) {
      analysis.category = 'memory';
      analysis.severity = 'critical';
      analysis.recoverable = true;
      analysis.suggestedAction = 'cleanup';
    }

    // Determine severity based on error patterns
    if (analysis.category === 'memory' || stack.includes('outofmemory')) {
      analysis.severity = 'critical';
    } else if (analysis.category === 'runtime' || message.includes('cannot read')) {
      analysis.severity = 'high';
    }

    return analysis;
  }

  attemptRecovery = async (_error: Error, analysis: any) => {
    console.log('🤖 AI Error Boundary: Attempting recovery...', analysis);

    this.setState({ recoveryAttempted: true });

    try {
      switch (analysis.suggestedAction) {
        case 'retry':
          // Wait and retry - the component will remount
          await new Promise(resolve => setTimeout(resolve, 2000));
          this.setState({
            hasError: false,
            error: null,
            errorId: null,
            recoveryAttempted: false
          });
          console.log('🤖 AI Recovery: Retrying after network error');
          break;

        case 'relogin':
          // Clear auth tokens and redirect to login
          localStorage.removeItem('token');
          window.location.href = '/auth';
          console.log('🤖 AI Recovery: Cleared auth and redirecting to login');
          break;

        case 'navigate_home':
          // Navigate to home/dashboard
          window.location.href = '/';
          console.log('🤖 AI Recovery: Navigating to home');
          break;

        case 'cleanup':
          // Memory cleanup
          if ((window as any).gc) {
            (window as any).gc();
          }
          localStorage.removeItem('temp_data');
          sessionStorage.clear();

          // Wait and retry
          await new Promise(resolve => setTimeout(resolve, 1000));
          this.setState({
            hasError: false,
            error: null,
            errorId: null,
            recoveryAttempted: false
          });
          console.log('🤖 AI Recovery: Memory cleanup completed');
          break;

        default:
          // Force reload as last resort
          console.log('🤖 AI Recovery: Force reloading page');
          window.location.reload();
      }
    } catch (recoveryError) {
      console.error('🤖 AI Recovery: Recovery failed:', recoveryError);
      // If recovery fails, show error UI
    }
  };

  render() {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Use ErrorFallback component with AI-specific messaging
      return (
        <ErrorFallback
          error={this.state.error}
          errorId={this.state.errorId}
          onReset={() => {
            this.setState({
              hasError: false,
              error: null,
              errorId: null,
              recoveryAttempted: false
            });
          }}
          title="Something went wrong"
          message="We're working to resolve this issue. The AI system has attempted automatic recovery."
          iconVariant="warning"
          className="bg-gradient-to-br from-red-50 to-orange-50"
        />
      );
    }

    return this.props.children;
  }
}

// Wrapper component to use the monitoring context
export const AIErrorBoundary = (props: any) => {
  const { reportError } = useAIMonitoring();

  return (
    <AIErrorBoundaryClass
      {...props}
      onError={(error, errorInfo) => {
        reportError(error, 'react_error_boundary');
        props.onError?.(error, errorInfo);
      }}
    />
  );
};