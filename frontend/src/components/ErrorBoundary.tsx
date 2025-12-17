import { Component, ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: unknown) {
    console.error("UI Error:", error);
  }

  reset = () => {
    this.setState({ hasError: false });
  };

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <div style={{ padding: 24 }}>
            <h2>Something went wrong</h2>
            <button onClick={this.reset}>Retry</button>
          </div>
        )
      );
    }

    return this.props.children;
  }
}
