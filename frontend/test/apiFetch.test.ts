/**
 * Test Suite for apiFetch Wrapper
 * 
 * Tests the new apiFetch function to ensure it properly wraps
 * the native fetch API with credentials and headers.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { apiFetch } from '../src/services/api';

// Mock the apiUrl function
vi.mock('@/lib/api', () => ({
  apiUrl: (path: string) => `https://api.test.com${path}`,
  getApiBase: () => 'https://api.test.com',
  isApiConfigured: () => true,
}));

// Store the original fetch
const originalFetch = global.fetch;

describe('apiFetch', () => {
  beforeEach(() => {
    // Reset mocks before each test
    vi.clearAllMocks();
  });

  afterEach(() => {
    // Restore original fetch
    global.fetch = originalFetch;
  });

  it('should successfully fetch and parse JSON', async () => {
    // Mock successful response
    const mockData = { id: 1, name: 'Test User' };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockData,
    });

    const result = await apiFetch<typeof mockData>('/api/users/1');

    expect(result).toEqual(mockData);
    expect(global.fetch).toHaveBeenCalledWith(
      'https://api.test.com/api/users/1',
      expect.objectContaining({
        credentials: 'include',
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
        }),
      })
    );
  });

  it('should include credentials in request', async () => {
    // Mock successful response
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({}),
    });

    await apiFetch('/api/test');

    expect(global.fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        credentials: 'include',
      })
    );
  });

  it('should set Content-Type header to application/json', async () => {
    // Mock successful response
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({}),
    });

    await apiFetch('/api/test');

    expect(global.fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
        }),
      })
    );
  });

  it('should merge custom headers with default headers', async () => {
    // Mock successful response
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({}),
    });

    await apiFetch('/api/test', {
      headers: {
        'Authorization': 'Bearer token123',
        'X-Custom-Header': 'custom-value',
      },
    });

    expect(global.fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
          'Authorization': 'Bearer token123',
          'X-Custom-Header': 'custom-value',
        }),
      })
    );
  });

  it('should throw error on non-OK response', async () => {
    // Mock error response
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
    });

    await expect(apiFetch('/api/test')).rejects.toThrow('API error 404');
  });

  it('should handle 500 server error', async () => {
    // Mock server error
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
    });

    await expect(apiFetch('/api/test')).rejects.toThrow('API error 500');
  });

  it('should handle 401 unauthorized error', async () => {
    // Mock unauthorized error
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
    });

    await expect(apiFetch('/api/test')).rejects.toThrow('API error 401');
  });

  it('should pass through RequestInit options', async () => {
    // Mock successful response
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({}),
    });

    await apiFetch('/api/test', {
      method: 'POST',
      body: JSON.stringify({ data: 'test' }),
    });

    expect(global.fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ data: 'test' }),
        credentials: 'include',
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
        }),
      })
    );
  });

  it('should return typed response', async () => {
    // Define a custom type
    interface User {
      id: number;
      email: string;
      name: string;
    }

    const mockUser: User = {
      id: 1,
      email: 'test@example.com',
      name: 'Test User',
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockUser,
    });

    const user = await apiFetch<User>('/api/auth/me');

    // TypeScript should infer the correct type
    expect(user.id).toBe(1);
    expect(user.email).toBe('test@example.com');
    expect(user.name).toBe('Test User');
  });
});
