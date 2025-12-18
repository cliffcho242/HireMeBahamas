/**
 * MASTER PLAYBOOK - Safe API URL Builder
 * 
 * Stack: React + Vite + TypeScript + Vercel
 * 
 * ABSOLUTE LAWS:
 * ✅ ALWAYS use VITE_* prefix (not NEXT_PUBLIC_*)
 * ✅ ALWAYS validate URL format
 * ✅ ALWAYS throw on misconfiguration
 * ✅ NEVER fail silently
 */

/**
 * Safe API URL builder with strict validation
 * @throws Error if VITE_API_URL is invalid or missing
 */
export function apiUrl(path: string): string {
  const base = import.meta.env.VITE_API_URL;
  
  // Strict validation
  if (!base?.startsWith("http")) {
    throw new Error("VITE_API_URL invalid or missing");
  }
  
  // Remove trailing slash from base, ensure leading slash on path
  const normalizedBase = base.replace(/\/$/, "");
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  
  return `${normalizedBase}${normalizedPath}`;
}


/**
 * Type-safe fetch wrapper with error handling
 * 
 * @example
 * const user = await apiFetch<User>("/api/auth/me");
 */
export async function apiFetch<T>(path: string): Promise<T> {
  const res = await fetch(apiUrl(path), { 
    credentials: "include" 
  });
  
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  
  return res.json();
}


/**
 * Query Error Boundary Component
 * Wraps React Query or other data fetching
 */
export function QueryErrorBoundary({ 
  children 
}: { 
  children: React.ReactNode 
}) {
  // In production, you'd add actual error boundary logic
  // For now, just pass through
  return <>{children}</>;
}
