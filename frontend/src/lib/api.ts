/**
 * FINAL, LOCKED, PRODUCTION API HANDLER
 * - iOS Safari safe
 * - Chrome safe
 * - No double slashes
 * - No silent failures
 * - Never returns empty or HTTP in production
 */

export function getApiBaseUrl(): string {
  const prod = import.meta.env.VITE_API_BASE_URL?.trim();
  const dev = import.meta.env.VITE_API_URL?.trim();

  const normalize = (url: string) => url.replace(/\/+$/, "");

  // 1. Allow localhost for development
  if (dev && dev.startsWith("http://localhost")) return normalize(dev);
  
  // 2. Prefer production URL if set
  if (prod && prod.startsWith("https://")) return normalize(prod);
  
  // 3. Allow dev URL if it's HTTPS
  if (dev && dev.startsWith("https://")) return normalize(dev);

  // 4. For production builds, throw error if no valid URL
  if (import.meta.env.PROD) {
    throw new Error(
      "CRITICAL: No API base URL configured for production build.\n" +
      "Set VITE_API_BASE_URL=https://api.yourdomain.com in your environment.\n" +
      "See .env.example for configuration details."
    );
  }

  // 5. Development fallback - empty means same-origin
  return "";
}

export function apiUrl(path: string): string {
  if (!path.startsWith("/")) path = "/" + path;
  return `${getApiBaseUrl()}${path}`;
}

export function buildApiUrl(path: string): string {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const base = getApiBaseUrl();
  if (!base) {
    throw new Error("API base URL is not set");
  }
  return `${base}${normalizedPath}`;
}

// Backward compatibility aliases
export const getApiBase = getApiBaseUrl;
export function isApiConfigured(): boolean {
  return getApiBaseUrl() !== "";
}

// API configuration
const API_TIMEOUT_MS = 30000; // 30 seconds
const API_RETRY_ATTEMPTS = 3;
const API_RETRY_DELAY_MS = 1000; // 1 second base delay
const API_MAX_RETRY_DELAY_MS = 10000; // 10 seconds max delay between retries

// Helper to check if error is retryable
function isRetryableError(error: unknown): boolean {
  if (error instanceof TypeError && error.message.includes('fetch')) {
    return true; // Network error
  }
  if (error instanceof Error) {
    const message = error.message.toLowerCase();
    return message.includes('network') || 
           message.includes('timeout') || 
           message.includes('failed to fetch');
  }
  return false;
}

// Helper to check if HTTP status is retryable
function isRetryableStatus(status: number): boolean {
  // Retry on 5xx errors and 429 (rate limit)
  return status >= 500 || status === 429 || status === 408;
}

// Sleep helper for retry delays
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = apiUrl(path);
  let lastError: Error | null = null;

  // Retry loop with exponential backoff
  for (let attempt = 0; attempt < API_RETRY_ATTEMPTS; attempt++) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        controller.abort(new DOMException('Request timeout', 'TimeoutError'));
      }, API_TIMEOUT_MS);

      try {
        const res = await fetch(url, {
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
          },
          ...options,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!res.ok) {
          // Check if we should retry this status
          if (attempt < API_RETRY_ATTEMPTS - 1 && isRetryableStatus(res.status)) {
            const delay = Math.min(
              API_RETRY_DELAY_MS * Math.pow(2, attempt),
              API_MAX_RETRY_DELAY_MS
            );
            console.warn(`API error ${res.status}, retrying in ${delay}ms... (attempt ${attempt + 1}/${API_RETRY_ATTEMPTS})`);
            await sleep(delay);
            continue;
          }

          const text = await res.text();
          console.error("API ERROR", res.status, text);
          throw new Error(`API request failed with status ${res.status}`);
        }

        return res.json();
      } finally {
        clearTimeout(timeoutId);
      }
    } catch (err) {
      lastError = err instanceof Error ? err : new Error(String(err));
      
      // Check if this is the last attempt
      if (attempt === API_RETRY_ATTEMPTS - 1) {
        break;
      }

      // Check if error is retryable
      if (isRetryableError(err)) {
        const delay = Math.min(
          API_RETRY_DELAY_MS * Math.pow(2, attempt),
          API_MAX_RETRY_DELAY_MS
        );
        console.warn(`Network error, retrying in ${delay}ms... (attempt ${attempt + 1}/${API_RETRY_ATTEMPTS})`);
        await sleep(delay);
        continue;
      }

      // Non-retryable error, throw immediately
      break;
    }
  }

  // All retries failed
  console.error("NETWORK FAILURE after all retries", lastError);
  throw lastError || new Error("API request failed after all retry attempts");
}
