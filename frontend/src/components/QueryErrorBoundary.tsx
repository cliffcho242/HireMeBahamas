import { ErrorBoundary } from "react-error-boundary";
import type { ReactNode } from "react";

export function QueryErrorBoundary({ children }: { children: ReactNode }) {
  return (
    <ErrorBoundary fallback={<p>Something went wrong.</p>}>
      {children}
    </ErrorBoundary>
  );
}
