/**
 * Smart Backend Router - Dual Backend Architecture
 * 
 * Uses BOTH Vercel serverless (fast, edge) AND Render (persistent, full-featured)
 * for lightning-fast performance with full functionality.
 * 
 * Strategy:
 * - Vercel Serverless: Fast auth endpoints (login, register, token refresh) - <200ms globally
 * - Render Backend: Heavy operations (file uploads, WebSockets, long queries)
 * 
 * Falls back gracefully if either backend is unavailable.
 */

interface BackendConfig {
  vercel: {
    url: string;
    available: boolean;
  };
  render: {
    url: string;
    available: boolean;
  };
  preferredBackend: 'vercel' | 'render' | 'auto';
}

// Detect backend URLs
function getBackendConfig(): BackendConfig {
  const vercelUrl = import.meta.env.VITE_VERCEL_API_URL || window.location.origin;
  const renderUrl = import.meta.env.VITE_RENDER_API_URL || '';
  
  return {
    vercel: {
      url: vercelUrl,
      available: true, // Assume available since it's same-origin
    },
    render: {
      url: renderUrl,
      available: !!renderUrl, // Available if configured
    },
    preferredBackend: (import.meta.env.VITE_PREFERRED_BACKEND as 'vercel' | 'render' | 'auto') || 'auto',
  };
}

// Categorize endpoints by which backend should handle them
const ENDPOINT_ROUTING = {
  // Fast endpoints - prefer Vercel serverless (edge, <200ms)
  vercel: [
    '/api/auth/login',
    '/api/auth/register',
    '/api/auth/refresh',
    '/api/auth/verify',
    '/api/auth/me',
    '/api/health',
    '/api/ready',
    '/api/users/:id', // Get user by ID (fast lookup)
    '/api/posts', // List posts (with caching)
    '/api/jobs', // List jobs (with caching)
  ],
  
  // Heavy/persistent endpoints - prefer Render (long-running, WebSockets)
  render: [
    '/api/upload',
    '/api/profile-pictures/upload',
    '/api/messages', // WebSocket support
    '/api/notifications', // WebSocket support
    '/api/posts/:id', // Create/update posts (database writes)
    '/api/jobs/:id', // Create/update jobs (database writes)
    '/api/users/:id/follow', // Database writes
  ],
};

/**
 * Determine which backend should handle a given endpoint
 */
export function getBackendForEndpoint(endpoint: string): 'vercel' | 'render' {
  const config = getBackendConfig();
  
  // If only one backend is available, use it
  if (!config.render.available) return 'vercel';
  if (!config.vercel.available) return 'render';
  
  // If explicit preference is set, use it
  if (config.preferredBackend !== 'auto') {
    return config.preferredBackend;
  }
  
  // Auto-routing based on endpoint type
  // Check if endpoint matches Vercel-preferred patterns
  for (const pattern of ENDPOINT_ROUTING.vercel) {
    if (matchesPattern(endpoint, pattern)) {
      return 'vercel';
    }
  }
  
  // Check if endpoint matches Render-preferred patterns
  for (const pattern of ENDPOINT_ROUTING.render) {
    if (matchesPattern(endpoint, pattern)) {
      return 'render';
    }
  }
  
  // Default to Vercel for unlisted endpoints (faster)
  return 'vercel';
}

/**
 * Get the full URL for an API endpoint
 */
export function getApiUrl(endpoint: string): string {
  const backend = getBackendForEndpoint(endpoint);
  const config = getBackendConfig();
  
  const baseUrl = backend === 'vercel' ? config.vercel.url : config.render.url;
  
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
 * Match endpoint against pattern (supports :param wildcards)
 */
function matchesPattern(endpoint: string, pattern: string): boolean {
  // Convert pattern to regex
  // /api/users/:id -> /^\/api\/users\/[^\/]+$/
  const regexPattern = pattern
    .replace(/:[^/]+/g, '[^/]+') // :param -> match any non-slash
    .replace(/\//g, '\\/'); // escape slashes
  
  const regex = new RegExp(`^${regexPattern}$`);
  return regex.test(endpoint);
}

/**
 * Test connectivity to both backends
 */
export async function testBackends(): Promise<{
  vercel: { available: boolean; latency?: number; error?: string };
  render: { available: boolean; latency?: number; error?: string };
}> {
  const config = getBackendConfig();
  
  const results = {
    vercel: { available: false, latency: 0, error: '' },
    render: { available: false, latency: 0, error: '' },
  };
  
  // Test Vercel
  if (config.vercel.url) {
    try {
      const start = Date.now();
      const response = await fetch(`${config.vercel.url}/api/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(5000),
      });
      const latency = Date.now() - start;
      
      if (response.ok) {
        results.vercel = { available: true, latency };
      } else {
        results.vercel = { 
          available: false, 
          error: `HTTP ${response.status}`,
          latency,
        };
      }
    } catch (error: any) {
      results.vercel = { 
        available: false, 
        error: error.message || 'Connection failed',
      };
    }
  }
  
  // Test Render
  if (config.render.url) {
    try {
      const start = Date.now();
      const response = await fetch(`${config.render.url}/api/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(5000),
      });
      const latency = Date.now() - start;
      
      if (response.ok) {
        results.render = { available: true, latency };
      } else {
        results.render = { 
          available: false, 
          error: `HTTP ${response.status}`,
          latency,
        };
      }
    } catch (error: any) {
      results.render = { 
        available: false, 
        error: error.message || 'Connection failed',
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
  console.log('⚡ DUAL BACKEND CONFIGURATION');
  console.log('='.repeat(60));
  console.log('Strategy: Use Vercel for speed, Render for features');
  console.log('');
  console.log('🌐 Vercel Serverless (Edge, <200ms):');
  console.log('  URL:', config.vercel.url);
  console.log('  Available:', config.vercel.available ? '✅ YES' : '❌ NO');
  console.log('  Handles: Auth, listings, fast queries');
  console.log('');
  console.log('🚀 Render Backend (Full-featured):');
  console.log('  URL:', config.render.url || '❌ NOT CONFIGURED');
  console.log('  Available:', config.render.available ? '✅ YES' : '❌ NO');
  console.log('  Handles: Uploads, WebSockets, heavy queries');
  console.log('');
  console.log('🎯 Routing Mode:', config.preferredBackend.toUpperCase());
  console.log('='.repeat(60));
}

/**
 * Get human-readable backend status
 */
export function getBackendStatus(): string {
  const config = getBackendConfig();
  
  if (config.vercel.available && config.render.available) {
    return '⚡ Dual backend active - Lightning fast!';
  } else if (config.vercel.available) {
    return '🌐 Vercel only - Fast but limited features';
  } else if (config.render.available) {
    return '🚀 Render only - Full features but may have cold starts';
  } else {
    return '❌ No backend configured';
  }
}

export { getBackendConfig };
