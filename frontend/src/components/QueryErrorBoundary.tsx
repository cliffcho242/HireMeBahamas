import { ErrorBoundary } from "react-error-boundary";

export function QueryErrorBoundary({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ErrorBoundary fallback={<p>Something went wrong.</p>}>
      {children}
    </ErrorBoundary>
  );
}
