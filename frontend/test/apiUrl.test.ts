import { describe, it, expect, vi, afterEach } from 'vitest';

const loadApiModule = async () => {
  const mod = await import('../src/lib/api');
  return mod;
};

afterEach(() => {
  vi.resetModules();
  vi.unstubAllEnvs();
});

describe('getApiBaseUrl & buildApiUrl', () => {
  it('prefers localhost override when present', async () => {
    vi.stubEnv('VITE_API_URL', 'http://localhost:8000/');
    vi.stubEnv('VITE_API_BASE_URL', 'https://hiremebahamas-backend.onrender.com');

    const { getApiBaseUrl } = await loadApiModule();
    expect(getApiBaseUrl()).toBe('http://localhost:8000');
  });

  it('normalizes trailing slash for production base URL', async () => {
    vi.stubEnv('VITE_API_BASE_URL', 'https://hiremebahamas-backend.onrender.com/');

    const { getApiBaseUrl } = await loadApiModule();
    expect(getApiBaseUrl()).toBe('https://hiremebahamas-backend.onrender.com');
  });

  it('builds paths without double slashes', async () => {
    vi.stubEnv('VITE_API_BASE_URL', 'https://hiremebahamas-backend.onrender.com/');

    const { buildApiUrl } = await loadApiModule();
    expect(buildApiUrl('api/auth/login')).toBe(
      'https://hiremebahamas-backend.onrender.com/api/auth/login'
    );
  });
});
