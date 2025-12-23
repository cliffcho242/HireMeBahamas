import React from "react";

/**
 * 🔒 STEP 6: ERROR BOUNDARY FOR RUNTIME ERRORS
 * Catches React errors and displays a fallback UI instead of white screen
 */
export default class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { error?: Error }
> {
  state: { error?: Error } = {};

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
