import React, { Component, ErrorInfo, ReactNode } from 'react';
import { useAIMonitoring } from '../contexts/AIMonitoringContext';

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
          // Clear auth tokens but do NOT force a full page reload or hard redirect.
          // Forcing a reload causes the entire SPA state to reset which makes
          // user edits and in-progress work disappear. Instead we clear the
          // token and clear the error boundary so the app can gracefully
          // surface the signed-out state (AuthContext will re-run initialization).
          localStorage.removeItem('token');
          this.setState({
            hasError: false,
            error: null,
            errorId: null,
            recoveryAttempted: false
          });
          console.log('🤖 AI Recovery: Cleared auth token; recovery completed without full reload');
          break;

        case 'navigate_home':
          // Navigate to home/dashboard without forcing a full page reload.
          // Use the History API so the SPA router can handle the navigation
          // and preserve in-memory state where possible.
          try {
            window.history.pushState({}, '', '/');
            // Notify listeners (react-router listens to popstate events)
            window.dispatchEvent(new PopStateEvent('popstate'));
            console.log('🤖 AI Recovery: Navigated to home via history.pushState');
          } catch (navErr) {
            // If history navigation fails, log and do not force a full page reload.
            // Forcing a reload here would wipe in-progress user state.
            console.warn('🤖 AI Recovery: history navigation failed; not performing full redirect', navErr);
          }
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
          // As a last resort, avoid forcing a full page reload which wipes
          // the SPA state and can be disruptive. Instead clear the error
          // boundary and allow components to re-render. If the problem
          // persists the user can manually refresh.
          console.log('🤖 AI Recovery: Clearing error boundary instead of full reload');
          this.setState({
            hasError: false,
            error: null,
            errorId: null,
            recoveryAttempted: false
          });
      }
    } catch (recoveryError) {
      console.error('🤖 AI Recovery: Recovery failed:', recoveryError);
      // If recovery fails, show error UI
    }
  };

  render() {
    if (this.state.hasError) {
      // Silent AI recovery - show simple error message to user
      return (
        <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-50 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-white rounded-xl shadow-2xl p-8 text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>

            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Something went wrong
            </h2>

            <p className="text-gray-600 mb-6">
              We're working to resolve this issue. Please try refreshing the page.
            </p>

            <div className="space-y-2">
              <button
                onClick={() => {
                  // Attempt a soft recovery by clearing the error boundary state.
                  // This avoids a full page reload which would clear in-progress work.
                  try {
                    (this as any).setState({
                      hasError: false,
                      error: null,
                      errorId: null,
                      recoveryAttempted: false
                    });
                    console.log('🤖 AI Recovery: Performed soft recovery (cleared error boundary)');
                  } catch (e) {
                    console.warn('🤖 AI Recovery: soft recovery failed', e);
                  }
                }}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-lg transition-colors"
              >
                🔄 Try to recover
              </button>

              <button
                onClick={() => window.location.reload()}
                className="w-full bg-gray-100 hover:bg-gray-200 text-gray-800 font-medium py-2 px-6 rounded-lg transition-colors text-sm"
              >
                ⚠️ Full refresh (discard changes)
              </button>
            </div>

            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <p className="text-xs text-gray-500 mb-2">Error ID:</p>
              <p className="text-xs font-mono text-gray-700 break-all">
                {this.state.errorId}
              </p>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Wrapper component to use the monitoring context
export const AIErrorBoundary: React.FC<Props> = (props) => {
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