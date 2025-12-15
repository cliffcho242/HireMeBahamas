import axios from 'axios';

// 🔍 TEMP DEBUG: Check if API URL is properly configured (development only)
if (import.meta.env.DEV) {
  console.log("API URL:", import.meta.env.VITE_API_URL);
}

// Use environment variable or fall back to same-origin for serverless deployments
const API_BASE_URL = import.meta.env.VITE_API_URL || window.location.origin;

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
