import axios from 'axios';

/**
 * Safe URL Builder Utility for Admin Panel
 * 
 * Validates and constructs API URLs safely to prevent "pattern mismatch" errors.
 */

/**
 * Validate and get the base API URL from environment
 * @throws Error if VITE_API_URL is missing or invalid
 */
function validateAndGetBaseUrl(): string {
  const base = import.meta.env.VITE_API_URL as string | undefined;

  // If no explicit API URL is set, use same-origin (for Vercel serverless)
  if (!base) {
    // Check if we're in a browser environment
    if (typeof window !== 'undefined') {
      return window.location.origin;
    }
    
    // If not in browser and no URL is set, throw an error
    throw new Error(
      "VITE_API_URL is missing or invalid. " +
      "Set VITE_API_URL environment variable to your backend URL, " +
      "or deploy to a serverless environment where same-origin is used."
    );
  }

  // Validate URL format
  if (!base.startsWith('http://') && !base.startsWith('https://')) {
    throw new Error(
      `VITE_API_URL is invalid: "${base}". ` +
      "URL must start with 'http://' or 'https://'. " +
      "Example: VITE_API_URL=https://your-backend.com"
    );
  }

  return base;
}

/**
 * Build a complete API URL from a path
 * 
 * @param path - The API path (e.g., "/admin/auth/login")
 * @returns The complete URL with base URL prepended
 * @throws Error if VITE_API_URL is missing or invalid
 */
export function apiUrl(path: string): string {
  const base = validateAndGetBaseUrl();
  
  // Normalize the base URL (remove trailing slash) and path (ensure leading slash)
  const normalizedBase = base.replace(/\/$/, "");
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  
  return `${normalizedBase}${normalizedPath}`;
}

/**
 * Get the base API URL
 * 
 * @returns The base API URL
 * @throws Error if VITE_API_URL is missing or invalid
 */
export function getApiBase(): string {
  const base = validateAndGetBaseUrl();
  return base.replace(/\/$/, "");
}

// ✅ SAFE: Use the safe API URL builder - never breaks
const API_BASE_URL = getApiBase();

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 || error.response?.status === 403) {
      localStorage.removeItem('admin_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/admin/auth/login', { email, password }),
  
  me: () => api.get('/admin/auth/me'),
};

// Users API
export const usersAPI = {
  getAll: (params?: { page?: number; per_page?: number; search?: string; user_type?: string }) =>
    api.get('/admin/users', { params }),
  
  getById: (id: number) => api.get(`/admin/users/${id}`),
  
  update: (id: number, data: any) => api.put(`/admin/users/${id}`, data),
  
  delete: (id: number) => api.delete(`/admin/users/${id}`),
};

// Dashboard API
export const dashboardAPI = {
  getStats: () => api.get('/admin/dashboard/stats'),
  
  getActivity: (limit?: number) => api.get('/admin/dashboard/activity', { params: { limit } }),
};

// Logs API
export const logsAPI = {
  getAll: (params?: { page?: number; per_page?: number }) =>
    api.get('/admin/logs', { params }),
};

// Settings API
export const settingsAPI = {
  getAll: () => api.get('/admin/settings'),
  
  update: (settings: Record<string, any>) => api.put('/admin/settings', settings),
};
