// AI-Enhanced API Configuration with Error Prevention
// Automatically handles connection issues and provides fallbacks

import axios from 'axios';
import { User } from '../types/user';
import { Job } from '../types/job';

// AI Error Prevention: Multiple backend endpoints for redundancy
const BACKEND_ENDPOINTS = [
  'http://127.0.0.1:8008',
  'http://localhost:8008',
  'http://127.0.0.1:8005', // Fallback
];

// Intelligent endpoint selection
const selectBestEndpoint = async () => {
  for (const endpoint of BACKEND_ENDPOINTS) {
    try {
      const response = await fetch(`${endpoint}/health`, { 
        method: 'GET'
      });
      if (response.ok) {
        console.log(`AI: Selected optimal endpoint: ${endpoint}`);
        return endpoint;
      }
    } catch (error) {
      console.warn(`AI: Endpoint ${endpoint} unavailable`);
    }
  }
  
  // Default fallback
  console.warn('AI: Using default endpoint (may need manual restart)');
  return BACKEND_ENDPOINTS[0];
};

// Get optimal API base URL
let API_BASE_URL = 'http://127.0.0.1:8008';

// AI-Enhanced axios instance with error recovery
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// AI Error Recovery Interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If connection fails, try alternative endpoints
    if (error.code === 'ERR_NETWORK' || error.code === 'ECONNREFUSED') {
      console.log('AI: Network error detected, attempting recovery...');
      
      const newEndpoint = await selectBestEndpoint();
      if (newEndpoint !== originalRequest.baseURL) {
        originalRequest.baseURL = newEndpoint;
        API_BASE_URL = newEndpoint;
        
        // Update the default baseURL for future requests
        api.defaults.baseURL = newEndpoint;
        
        console.log(`AI: Switched to endpoint: ${newEndpoint}`);
        return api.request(originalRequest);
      }
    }
    
    return Promise.reject(error);
  }
);

// Add auth token to requests with AI validation
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    // AI: Validate token format before sending
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const now = Date.now() / 1000;
      
      if (payload.exp && payload.exp > now) {
        config.headers.Authorization = `Bearer ${token}`;
      } else {
        console.log('AI: Token expired, removing from storage');
        localStorage.removeItem('token');
      }
    } catch (error) {
      console.log('AI: Invalid token format, removing from storage');
      localStorage.removeItem('token');
    }
  }
  return config;
});

// AI-Enhanced Authentication Functions
export const authAPI = {
  login: async (email: string, password: string) => {
    try {
      const response = await api.post('/api/auth/login', { email, password });
      
      if (response.data.success && response.data.token) {
        localStorage.setItem('token', response.data.token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        console.log('AI: Login successful, token stored securely');
      }
      
      return response.data;
    } catch (error: any) {
      console.error('AI: Login error detected:', error.message);
      throw error;
    }
  },

  register: async (userData: any) => {
    try {
      const response = await api.post('/auth/register', userData);
      return response.data;
    } catch (error) {
      console.error('AI: Registration error:', error);
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    console.log('AI: User logged out, tokens cleared');
  },

  getCurrentUser: (): User | null => {
    try {
      const userStr = localStorage.getItem('user');
      return userStr ? JSON.parse(userStr) : null;
    } catch {
      console.log('AI: Invalid user data, clearing storage');
      localStorage.removeItem('user');
      return null;
    }
  }
};

// AI-Enhanced Job Functions
export const jobAPI = {
  getAllJobs: async () => {
    const response = await api.get('/jobs');
    return response.data;
  },

  getJobById: async (id: string) => {
    const response = await api.get(`/jobs/${id}`);
    return response.data;
  },

  createJob: async (jobData: Partial<Job>) => {
    const response = await api.post('/jobs', jobData);
    return response.data;
  },

  updateJob: async (id: string, jobData: Partial<Job>) => {
    const response = await api.put(`/jobs/${id}`, jobData);
    return response.data;
  },

  deleteJob: async (id: string) => {
    const response = await api.delete(`/jobs/${id}`);
    return response.data;
  }
};

// AI Health Monitoring
export const healthAPI = {
  checkBackendHealth: async () => {
    try {
      const response = await api.get('/health');
      return {
        healthy: response.status === 200,
        data: response.data,
        endpoint: API_BASE_URL
      };
    } catch (error) {
      return {
        healthy: false,
        error: error,
        endpoint: API_BASE_URL
      };
    }
  }
};

// Export the configured API instance
export default api;

// AI Status Logger
console.log('AI API System: Initialized with intelligent error recovery');
console.log(`Primary endpoint: ${API_BASE_URL}`);
console.log('Features: Auto-recovery, Token validation, Health monitoring');