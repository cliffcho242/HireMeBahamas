// 🧱 LAYER 2: Runtime Error Boundary - Catches runtime errors and shows graceful fallback
import React from "react";

export default class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { error?: Error }
> {
  state = {};

  static getDerivedStateFromError(error: Error) {
    return { error };
  }

  componentDidCatch(error: Error, info: any) {
    console.error("🔥 RUNTIME ERROR", error, info);
  }

  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: 24, fontFamily: "sans-serif" }}>
          <h1>Something went wrong</h1>
          <pre>{this.state.error.message}</pre>
          <button onClick={() => location.reload()}>Reload</button>
        </div>
      );
    }
    return this.props.children;
  }
}

// Named export for backwards compatibility
export { ErrorBoundary };
