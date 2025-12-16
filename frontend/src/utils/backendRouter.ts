/**
 * API URL Configuration
 * 
 * Uses environment variable or defaults to same-origin (Vercel serverless).
 * 
 * Configuration:
 * - VITE_API_URL: Set this to point to your backend (Railway, custom domain, or local dev)
 * - VITE_REQUIRE_BACKEND_URL: Set to 'true' to enforce VITE_API_URL (prevents silent failures)
 * - If not set: Uses same-origin (window.location.origin) for Vercel deployments
 * 
 * Examples:
 * - Vercel serverless (same-origin): Don't set VITE_API_URL
 * - Railway backend: VITE_API_URL=https://your-app.up.railway.app
 * - Local dev: VITE_API_URL=http://localhost:8000
 * - Strict mode: VITE_REQUIRE_BACKEND_URL=true (will throw error if VITE_API_URL not set)
 */

interface BackendConfig {
  url: string;
  available: boolean;
}

// Guard: Prevent silent failures when backend URL is required but not configured
if (import.meta.env.VITE_REQUIRE_BACKEND_URL === 'true' && !import.meta.env.VITE_API_URL) {
  throw new Error(
    "VITE_API_URL is not set. " +
    "Either set VITE_API_URL environment variable or disable VITE_REQUIRE_BACKEND_URL. " +
    "This prevents silent failures when an explicit backend URL is required."
  );
}

// Detect backend URL
function getBackendConfig(): BackendConfig {
  const envUrl = import.meta.env.VITE_API_URL;
  
  // If explicit URL is set in env, use it
  if (envUrl) {
    return {
      url: envUrl,
      available: true,
    };
  }
  
  // Otherwise, use same-origin (for Vercel deployments)
  return {
    url: window.location.origin,
    available: true,
  };
}

/**
 * Get the full URL for an API endpoint
 */
export function getApiUrl(endpoint: string): string {
  const config = getBackendConfig();
  const baseUrl = config.url;
  
  // Ensure endpoint starts with /
  const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  
  // Don't double up /api if endpoint already includes it
  if (normalizedEndpoint.startsWith('/api/')) {
    return `${baseUrl}${normalizedEndpoint}`;
  } else {
    return `${baseUrl}/api${normalizedEndpoint}`;
  }
}

/**
 * Test connectivity to backend
 */
export async function testBackends(): Promise<{
  backend: { available: boolean; latency?: number; error?: string };
}> {
  const config = getBackendConfig();
  
  const results = {
    backend: { available: false, latency: 0, error: '' },
  };
  
  // Test backend
  if (config.url) {
    try {
      const start = Date.now();
      const response = await fetch(`${config.url}/api/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(5000),
      });
      const latency = Date.now() - start;
      
      if (response.ok) {
        results.backend = { available: true, latency, error: '' };
      } else {
        results.backend = { 
          available: false, 
          error: `HTTP ${response.status}`,
          latency,
        };
      }
    } catch (error: unknown) {
      results.backend = { 
        available: false, 
        error: error instanceof Error ? error.message : 'Connection failed',
        latency: 0,
      };
    }
  }
  
  return results;
}

/**
 * Log backend configuration on app startup
 */
export function logBackendConfiguration(): void {
  const config = getBackendConfig();
  
  console.log('='.repeat(60));
  console.log('🌐 BACKEND CONFIGURATION');
  console.log('='.repeat(60));
  console.log('Backend URL:', config.url);
  console.log('Available:', config.available ? '✅ YES' : '❌ NO');
  console.log('Source:', import.meta.env.VITE_API_URL ? 'Environment Variable' : 'Same-Origin (Vercel)');
  console.log('='.repeat(60));
}

/**
 * Get human-readable backend status
 */
export function getBackendStatus(): string {
  const config = getBackendConfig();
  
  if (config.available) {
    return '✅ Backend configured and ready';
  } else {
    return '❌ No backend configured';
  }
}

export { getBackendConfig };
