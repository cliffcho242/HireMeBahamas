"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import { CACHE_TIMES } from "./cache-config";

export function Providers({ children }: { children: React.ReactNode }) {
  // Create a client instance per component mount to avoid sharing state between requests
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // Avoid duplicate fetches with staleTime
            staleTime: CACHE_TIMES.STALE_TIME, // Data is fresh for 30s
            gcTime: CACHE_TIMES.GC_TIME, // Cache garbage collection time
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
