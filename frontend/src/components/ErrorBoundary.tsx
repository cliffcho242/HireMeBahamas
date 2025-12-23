// 🧱 LAYER 3: Runtime Error Boundary - Runtime crashes cannot kill UI
import React from "react";

interface ErrorBoundaryState {
  error?: Error;
}

export default class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  ErrorBoundaryState
> {
  state: ErrorBoundaryState = {};

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error };
  }

  componentDidCatch(error: Error, info: any) {
    console.error("RUNTIME CRASH", error, info);
  }

  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: 24 }}>
          <h1>Something went wrong</h1>
          <pre>{this.state.error.message}</pre>
          <button onClick={() => location.reload()}>
            Reload
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

// Named export for backwards compatibility
export { ErrorBoundary };
