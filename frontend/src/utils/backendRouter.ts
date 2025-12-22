import { API_BASE_URL, apiUrl } from '@/lib/api';

interface BackendConfig {
  url: string;
  available: boolean;
}

export function validateBackendUrl(): void {
  if (!API_BASE_URL) {
    throw new Error('VITE_API_BASE_URL is required for backend routing');
  }
}

validateBackendUrl();

function getBackendConfig(): BackendConfig {
  return {
    url: API_BASE_URL,
    available: true,
  };
}

export function getApiUrl(endpoint: string): string {
  return apiUrl(endpoint);
}

export async function testBackends(): Promise<{
  backend: { available: boolean; latency?: number; error?: string };
}> {
  const config = getBackendConfig();
  const results = {
    backend: { available: false, latency: 0, error: '' },
  };

  try {
    const start = Date.now();
    // Backend exposes /health (no /api prefix) as required by Render health checks
    const response = await fetch(apiUrl('/health'), {
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

  return results;
}

export function logBackendConfiguration(): void {
  const config = getBackendConfig();

  console.log('='.repeat(60));
  console.log('🌐 BACKEND CONFIGURATION');
  console.log('='.repeat(60));
  console.log('Backend URL:', config.url);
  console.log('Available:', config.available ? '✅ YES' : '❌ NO');
  console.log('Source: VITE_API_BASE_URL');
  console.log('='.repeat(60));
}

export function getBackendStatus(): string {
  const config = getBackendConfig();
  return config.available ? '✅ Backend configured and ready' : '❌ Backend unavailable';
}

export { getBackendConfig };
