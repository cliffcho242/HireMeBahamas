/**
 * Safe Fetch Wrapper
 * 
 * ✅ Prevents fetch crashes from breaking the app
 * ✅ Returns degraded fallback to avoid blank screen
 * ✅ Logs errors for debugging
 */
import { apiUrl } from "./api";

export async function safeFetch(endpoint: string, options?: RequestInit) {
  const url = apiUrl(endpoint);
  try {
    const res = await fetch(url, options);
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }
    return await res.json();
  } catch (err: unknown) {
    console.error("⚠️ Network/API error", err);
    // Return degraded fallback to avoid blank screen
    return { error: true, message: err instanceof Error ? err.message : String(err) };
  }
}
