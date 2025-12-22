import { API_BASE_URL, apiUrl } from '../lib/api';

interface BackendConfig {
  url: string;
  available: boolean;
}

function getBackendConfig(): BackendConfig {
  return {
    url: API_BASE_URL,
    available: true,
  };
}

/**
 * Get the full URL for an API endpoint
 */
export function getApiUrl(endpoint: string): string {
  return apiUrl(endpoint);
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
      const response = await fetch(apiUrl('/api/health'), {
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
  console.log('Source:', 'Production API');
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
