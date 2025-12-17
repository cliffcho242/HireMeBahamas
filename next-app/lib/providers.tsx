"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";

export function Providers({ children }: { children: React.ReactNode }) {
  // Create a client instance per component mount to avoid sharing state between requests
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // Avoid duplicate fetches with staleTime
            staleTime: 30_000, // 30 seconds - data is fresh for 30s
            gcTime: 60_000, // 60 seconds - cache garbage collection time (formerly cacheTime)
            refetchOnWindowFocus: false, // Don't refetch on window focus to reduce load
            retry: 1, // Retry failed requests once
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
