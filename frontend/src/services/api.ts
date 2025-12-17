import axios from 'axios';
import { User } from '../types/user';
import { Job } from '../types/job';
import { debugLog } from '../utils/debugLogger';
import { getApiUrl, logBackendConfiguration } from '../utils/backendRouter';
import { ENV_API } from '../config/env';
import { refreshToken } from './auth';
import { safeParseUrl } from '../lib/safeUrl';
import { apiUrl, getApiBase } from '../lib/api';

// Note: Backend URL validation happens automatically when backendRouter is imported
// The validateBackendUrl() function is called at module load in backendRouter.ts

// API Response Types
interface UserResponse {
  success: boolean;
  user: User;
}

interface FollowersResponse {
  success: boolean;
  followers: User[];
}

interface FollowingResponse {
  success: boolean;
  following: User[];
}

// Session storage key - must match sessionManager.ts
const SESSION_KEY = 'hireme_session';

// Connection state management for user feedback
type ConnectionState = 'connected' | 'connecting' | 'disconnected' | 'error';

class ConnectionStateManager {
  private state: ConnectionState = 'connected';
  private listeners: Array<(state: ConnectionState) => void> = [];

  getState(): ConnectionState {
    return this.state;
  }

  setState(newState: ConnectionState): void {
    if (this.state !== newState) {
      this.state = newState;
      this.notifyListeners();
    }
  }

  subscribe(listener: (state: ConnectionState) => void): () => void {
    this.listeners.push(listener);
    // Return unsubscribe function
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  private notifyListeners(): void {
    this.listeners.forEach(listener => listener(this.state));
  }
}

export const connectionState = new ConnectionStateManager();

// Log backend configuration on module load
if (import.meta.env.DEV) {
  logBackendConfiguration();
}

// Use safe URL builder to get validated API base URL
// getApiBase() returns normalized URL without trailing slash
const API_BASE_URL = getApiBase();

// Export API constant for use in fetch calls (for backward compatibility)
export const API = API_BASE_URL;

// 🔍 TEMP DEBUG: Check if API URL is properly configured (development only)
if (import.meta.env.DEV) {
  console.log("API URL:", import.meta.env.VITE_API_URL);
}

// Log API configuration on startup (development only)
if (typeof window !== 'undefined' && import.meta.env.DEV) {
  console.log('=== API CONFIGURATION ===');
  console.log('API Base URL:', API_BASE_URL);
  console.log('ENV_API:', ENV_API || 'not set');
  console.log('Window Origin:', window.location.origin);
  console.log('========================');
}

// Create axios instance with retry logic
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds default timeout
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false, // Must be false with wildcard CORS
});

// Retry configuration - optimized to prevent excessive timing
const MAX_RETRIES = 3; // Reduced from 5 to prevent excessive waiting
const RETRY_DELAY = 2000; // 2 seconds base delay for retries (reduced from 3s)
const BACKEND_WAKE_TIME = 60000; // 60 seconds (1 minute) for cold starts (reduced from 2 minutes)
const MAX_WAKE_RETRIES = 3; // Reduced from 4 to prevent excessive waiting
const INITIAL_WAIT_MS = 3000; // 3 seconds initial wait before first retry (reduced from 5s)
const BASE_BACKOFF_MS = 5000; // Base for exponential backoff (reduced from 10s)
const MAX_WAIT_MS = 15000; // Maximum wait time between retries (reduced from 30s)
const MAX_TOTAL_TIMEOUT = 180000; // 3 minutes maximum total timeout for all retries combined

// Circuit breaker to prevent infinite retry loops
class CircuitBreaker {
  private failures: number = 0;
  private lastFailureTime: number = 0;
  private readonly threshold = 5; // Open circuit after 5 consecutive failures
  private readonly resetTimeout = 60000; // Reset after 1 minute

  isOpen(): boolean {
    // Reset if enough time has passed
    if (Date.now() - this.lastFailureTime > this.resetTimeout) {
      this.failures = 0;
      return false;
    }
    return this.failures >= this.threshold;
  }

  recordFailure(): void {
    this.failures++;
    this.lastFailureTime = Date.now();
  }

  recordSuccess(): void {
    this.failures = 0;
    this.lastFailureTime = 0;
  }
}

const circuitBreaker = new CircuitBreaker();

// Extend axios config type to include our custom properties
declare module 'axios' {
  export interface InternalAxiosRequestConfig {
    _retryCount?: number;
    _requestStartTime?: number;
    _refreshAttempted?: boolean; // Track if refresh was already attempted for this request
  }
}

// Helper to check if backend is sleeping (Render free tier)
interface ApiErrorType {
  response?: { status?: number };
  code?: string;
  config?: { timeout?: number };
}

const isBackendSleeping = (error: ApiErrorType): boolean => {
  // Render.com returns 503 when service is sleeping
  if (error.response?.status === 503) return true;
  
  // 405 can indicate backend is down or misconfigured
  if (error.response?.status === 405) return true;
  
  // Long timeout suggests cold start
  if (error.code === 'ECONNABORTED' && (error.config?.timeout ?? 0) > 15000) return true;
  
  // Connection refused during wake-up
  if (error.code === 'ECONNREFUSED') return true;
  
  return false;
};

// Helper to check if endpoint is an authentication endpoint
// Using endsWith for precise matching, avoiding false positives
const isAuthEndpoint = (url: string | undefined): boolean => {
  if (!url) return false;
  return url.endsWith('/auth/login') || url.endsWith('/auth/register');
};

// Future-safe helper: Mark intentionally unused helpers to prevent accidental removal
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const isAuthEndpointGeneral = (url: string): boolean => {
  return url.includes("/auth");
};

// Add auth token to requests and apply smart backend routing
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  // Don't send auth header to authentication endpoints
  if (token && !isAuthEndpoint(config.url)) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  // Initialize retry count and start time for tracking total timeout (using custom config properties)
  if (config._retryCount === undefined) {
    config._retryCount = 0;
  }
  if (config._requestStartTime === undefined) {
    config._requestStartTime = Date.now();
  }
  
  // Apply smart backend routing if URL is relative
  if (config.url && config.url.startsWith('/api/')) {
    const optimalUrl = getApiUrl(config.url);
    
    // Only log routing in development
    if (import.meta.env.DEV) {
      console.log('🎯 Smart routing:', config.url, '->', optimalUrl);
    }
    
    // Override the full URL (baseURL + url)
    // We need to extract just the endpoint part since getApiUrl returns the full URL
    // 🔒 SAFE URL PARSING: Use safeParseUrl to prevent "pattern mismatch" errors
    const urlResult = safeParseUrl(optimalUrl, 'API Request');
    
    if (urlResult.success && urlResult.url) {
      const urlObj = urlResult.url;
      config.baseURL = urlObj.origin;
      config.url = urlObj.pathname + urlObj.search;
    } else {
      // Throw error with clear guidance
      throw new Error(
        `API URL configuration error: ${urlResult.error}\n\n` +
        `Possible solutions:\n` +
        `1. Set VITE_API_URL=https://api.yourdomain.com for production\n` +
        `2. Set VITE_API_URL=http://localhost:8000 for local dev\n` +
        `3. Leave VITE_API_URL unset for Vercel serverless (same-origin)`
      );
    }
  }
  
  // Enhanced logging for debugging (development only)
  if (import.meta.env.DEV) {
    console.log('🔹 API Request:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      baseURL: config.baseURL,
      fullURL: `${config.baseURL}${config.url}`,
    });
  }
  
  return config;
});

// Handle auth errors with automatic retry
api.interceptors.response.use(
  (response) => {
    // Record successful response in circuit breaker and connection state
    circuitBreaker.recordSuccess();
    connectionState.setState('connected');
    
    // Only log in development to avoid exposing response data
    if (import.meta.env.DEV) {
      console.log('✅ API Response:', {
        url: response.config.url,
        status: response.status,
        statusText: response.statusText,
      });
    }
    return response;
  },
  async (error) => {
    const config = error.config;
    
    // Update connection state based on error type
    if (error.code === 'ERR_NETWORK' || error.code === 'ECONNREFUSED') {
      connectionState.setState('disconnected');
    } else if (error.response?.status && error.response.status >= 500) {
      connectionState.setState('error');
    }
    
    // Check circuit breaker first - if open, fail fast
    if (circuitBreaker.isOpen()) {
      console.error('⚠️ Circuit breaker is OPEN - too many failures. Failing fast.');
      connectionState.setState('error');
      const circuitError = new Error('Service is temporarily unavailable. Please try again in a minute.');
      // Don't record another failure - circuit is already open due to previous failures
      return Promise.reject(circuitError);
    }
    
    // Log errors - detailed in dev, minimal in production
    if (import.meta.env.DEV) {
      console.error('❌ API Error:', {
        url: error.config?.url,
        method: error.config?.method,
        status: error.response?.status,
        statusText: error.response?.statusText,
        message: error.message,
        code: error.code,
        data: error.response?.data,
        baseURL: error.config?.baseURL,
      });
    } else {
      // Production: minimal error logging
      console.error('API Error:', {
        status: error.response?.status,
        message: error.message,
      });
    }
    
    // Check total elapsed time to prevent excessive waiting
    const requestStartTime = config?._requestStartTime;
    const elapsedTime = typeof requestStartTime === 'number' ? Date.now() - requestStartTime : 0;
    
    if (elapsedTime > MAX_TOTAL_TIMEOUT) {
      console.error(`Request timeout: Total time exceeded ${MAX_TOTAL_TIMEOUT / 1000} seconds`);
      circuitBreaker.recordFailure();
      const timeoutError = new Error(`Request timed out after ${Math.round(elapsedTime / 1000)} seconds. Please try again.`);
      return Promise.reject(timeoutError);
    }
    
    // Check if backend is sleeping (Render.com free tier)
    if (isBackendSleeping(error)) {
      const retryCount = config._retryCount ?? 0;
      
      if (retryCount < MAX_WAKE_RETRIES) {
        const attemptNumber = retryCount + 1; // Human-readable attempt number (1-based)
        const isFirstAttempt = retryCount === 0;
        
        // Set connecting state
        connectionState.setState('connecting');
        
        if (isFirstAttempt) {
          console.log('Backend appears to be sleeping or starting up...');
          console.log('This may take up to 1 minute on first request (cold start).');
          console.log('Status:', error.response?.status || 'No response');
        } else {
          console.log(`Backend still waking up... Attempt ${attemptNumber}/${MAX_WAKE_RETRIES}`);
        }
        
        // Increase timeout for wake-up
        config.timeout = BACKEND_WAKE_TIME;
        config._retryCount = attemptNumber;
        
        // Backoff delays: 3s (first), then 5s, 10s for subsequent retries
        const waitTime = isFirstAttempt 
          ? INITIAL_WAIT_MS 
          : Math.min(BASE_BACKOFF_MS * Math.pow(2, retryCount - 1), MAX_WAIT_MS);
        console.log(`Waiting ${waitTime / 1000} seconds before retry...`);
        await new Promise(resolve => setTimeout(resolve, waitTime));
        
        return api(config);
      }
    }
    
    // Retry logic for network errors
    if (
      error.code === 'ECONNABORTED' ||
      error.code === 'ERR_NETWORK' ||
      error.message.includes('Network Error') ||
      error.message.includes('timeout')
    ) {
      const retryCount = config._retryCount ?? 0;
      
      if (retryCount < MAX_RETRIES) {
        connectionState.setState('connecting');
        config._retryCount = retryCount + 1;
        console.log(`Retrying request (${retryCount + 1}/${MAX_RETRIES})...`);
        
        // Wait before retrying
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY * (retryCount + 1)));
        
        return api(config);
      }
      
      console.error('Max retries reached. Network error persists.');
      circuitBreaker.recordFailure();
    }
    
    // Handle auth errors with automatic token refresh
    if (error.response?.status === 401) {
      // Check if this is a USER_NOT_FOUND error (user account deleted or database reset)
      const errorData = error.response?.data;
      const isUserNotFound = errorData?.error_code === 'USER_NOT_FOUND' || 
                             errorData?.action === 'logout';
      
      // Skip refresh for refresh endpoint itself to prevent infinite loop
      const isRefreshEndpoint = config.url === '/api/auth/refresh' || config.url?.endsWith('/auth/refresh');
      
      // Check if we already attempted refresh for this request
      const alreadyRefreshed = config._refreshAttempted === true;
      
      // If user not found, refresh endpoint failing, or already refreshed once, logout immediately
      if (isUserNotFound || isRefreshEndpoint || alreadyRefreshed) {
        console.log('Authentication failed - logging out', isUserNotFound ? '(user not found in database)' : '');
        localStorage.removeItem('token');
        localStorage.removeItem(SESSION_KEY);
        const USER_KEY = 'hireme_user'; // Match sessionManager.ts
        localStorage.removeItem(USER_KEY);
        window.location.href = '/login';
      } else {
        // Try to refresh the token silently
        try {
          await refreshToken();
          
          // Update the config with new token and mark as refreshed
          const newToken = localStorage.getItem('token');
          if (newToken && config.headers) {
            config.headers.Authorization = `Bearer ${newToken}`;
          }
          config._refreshAttempted = true; // Prevent infinite refresh loop
          
          // Retry the original request with new token
          console.log('Token refreshed, retrying request...');
          return api(config);
        } catch (refreshError) {
          // If refresh fails, logout
          console.error('Token refresh failed:', refreshError);
          localStorage.removeItem('token');
          localStorage.removeItem(SESSION_KEY);
          const USER_KEY = 'hireme_user'; // Match sessionManager.ts
          localStorage.removeItem(USER_KEY);
          window.location.href = '/login';
        }
      }
    }
    
    // Record failure in circuit breaker for non-retry errors
    if (error.response?.status && error.response.status >= 500) {
      circuitBreaker.recordFailure();
    }
    
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (credentials: { email: string; password: string }) => {
    // Use extended timeout for login as backend may need to wake up
    // and password verification can take time
    const response = await api.post('/api/auth/login', credentials, {
      timeout: BACKEND_WAKE_TIME, // 1 minute for cold start + password verification
    });
    return response.data;
  },

  register: async (userData: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    user_type: 'freelancer' | 'client' | 'employer' | 'recruiter';
    location: string;
    phone?: string;
  }) => {
    // Use extended timeout for registration as backend may need to wake up
    // and password hashing can take time
    const response = await api.post('/api/auth/register', userData, {
      timeout: BACKEND_WAKE_TIME, // 1 minute for cold start + password hashing
    });
    return response.data;
  },

  refreshToken: async () => {
    const response = await api.post('/api/auth/refresh');
    return response.data;
  },

  verifySession: async () => {
    const response = await api.get('/api/auth/verify');
    return response.data;
  },

  getProfile: async (): Promise<User> => {
    const response = await api.get('/api/auth/profile');
    return response.data;
  },

  updateProfile: async (data: Partial<User>): Promise<User> => {
    const response = await api.put('/api/auth/profile', data);
    return response.data;
  },

  changePassword: async (data: {
    current_password: string;
    new_password: string;
  }) => {
    const response = await api.put('/api/auth/change-password', data);
    return response.data;
  },

  getUserProfile: async (identifier: string | number): Promise<UserResponse> => {
    // Debug logging for user profile API calls (only in development)
    debugLog.log('[API] getUserProfile called with identifier:', identifier, 
      '| Type:', typeof identifier,
      '| URL:', `/api/users/${identifier}`);
    
    const response = await api.get(`/api/users/${identifier}`);
    return response.data;
  },

  // OAuth methods
  googleLogin: async (token: string, userType?: string) => {
    const response = await api.post('/api/auth/oauth/google', {
      token,
      provider: 'google',
      user_type: userType || 'user'
    });
    return response.data;
  },

  appleLogin: async (token: string, userType?: string) => {
    const response = await api.post('/api/auth/oauth/apple', {
      token,
      provider: 'apple',
      user_type: userType || 'user'
    });
    return response.data;
  },
};

// Jobs API
export const jobsAPI = {
  getJobs: async (params?: {
    skip?: number;
    limit?: number;
    category?: string;
    location?: string;
    is_remote?: boolean;
    budget_min?: number;
    budget_max?: number;
    search?: string;
  }) => {
    const response = await api.get('/api/jobs', { params });
    return response.data;
  },

  getJob: async (id: string): Promise<Job> => {
    const response = await api.get(`/api/jobs/${id}`);
    return response.data;
  },

  createJob: async (jobData: {
    title: string;
    description: string;
    category: string;
    budget: number;
    budget_type: 'fixed' | 'hourly';
    location: string;
    is_remote: boolean;
    skills?: string[];
  }) => {
    const response = await api.post('/api/jobs', jobData);
    return response.data;
  },

  updateJob: async (id: string, data: Partial<Job>) => {
    const response = await api.put(`/api/jobs/${id}`, data);
    return response.data;
  },

  deleteJob: async (id: string) => {
    const response = await api.delete(`/api/jobs/${id}`);
    return response.data;
  },

  applyToJob: async (
    id: string,
    applicationData: {
      cover_letter: string;
      proposed_budget: number;
    }
  ) => {
    const response = await api.post(`/api/jobs/${id}/apply`, applicationData);
    return response.data;
  },

  getJobApplications: async (id: string) => {
    const response = await api.get(`/api/jobs/${id}/applications`);
    return response.data;
  },

  getMyPostedJobs: async () => {
    const response = await api.get('/api/jobs/my/posted');
    return response.data;
  },

  getMyApplications: async () => {
    const response = await api.get('/api/jobs/my/applications');
    return response.data;
  },

  toggleJobStatus: async (id: string | number) => {
    const response = await api.post(`/api/jobs/${id}/toggle`);
    return response.data;
  },
};

// Messages API
export const messagesAPI = {
  getConversations: async () => {
    const response = await api.get('/api/messages/conversations');
    return response.data;
  },

  createConversation: async (participantId: string) => {
    const response = await api.post('/api/messages/conversations', {
      participant_id: participantId,
    });
    return response.data;
  },

  getConversationMessages: async (
    conversationId: string,
    params?: { skip?: number; limit?: number }
  ) => {
    const response = await api.get(
      `/api/messages/conversations/${conversationId}/messages`,
      { params }
    );
    return response.data;
  },

  sendMessage: async (conversationId: string, content: string) => {
    const response = await api.post(
      `/api/messages/conversations/${conversationId}/messages`,
      { content }
    );
    return response.data;
  },

  markMessageRead: async (messageId: string) => {
    const response = await api.put(`/api/messages/messages/${messageId}/read`);
    return response.data;
  },

  getUnreadCount: async () => {
    const response = await api.get('/api/messages/unread-count');
    return response.data;
  },
};

// Reviews API
export const reviewsAPI = {
  createReview: async (reviewData: {
    job_id: string;
    reviewee_id: string;
    rating: number;
    comment?: string;
  }) => {
    const response = await api.post('/api/reviews', reviewData);
    return response.data;
  },

  getUserReviews: async (
    userId: string,
    params?: { skip?: number; limit?: number }
  ) => {
    const response = await api.get(`/api/reviews/user/${userId}`, { params });
    return response.data;
  },

  getJobReviews: async (jobId: string) => {
    const response = await api.get(`/api/reviews/job/${jobId}`);
    return response.data;
  },

  getMyGivenReviews: async () => {
    const response = await api.get('/api/reviews/my/given');
    return response.data;
  },

  getMyReceivedReviews: async () => {
    const response = await api.get('/api/reviews/my/received');
    return response.data;
  },

  updateReview: async (
    reviewId: string,
    data: { rating?: number; comment?: string }
  ) => {
    const response = await api.put(`/api/reviews/${reviewId}`, data);
    return response.data;
  },

  deleteReview: async (reviewId: string) => {
    const response = await api.delete(`/api/reviews/${reviewId}`);
    return response.data;
  },

  getUserReviewStats: async (userId: string) => {
    const response = await api.get(`/api/reviews/stats/${userId}`);
    return response.data;
  },
};

// Upload API
export const uploadAPI = {
  uploadAvatar: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/api/upload/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  uploadPortfolioImages: async (files: File[]) => {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    const response = await api.post('/api/upload/portfolio', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  deletePortfolioImage: async (fileUrl: string) => {
    const formData = new FormData();
    formData.append('file_url', fileUrl);
    const response = await api.delete('/api/upload/portfolio', {
      data: formData,
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  uploadDocument: async (file: File, description?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (description) formData.append('description', description);
    const response = await api.post('/api/upload/document', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getMyFiles: async () => {
    const response = await api.get('/api/upload/my-files');
    return response.data;
  },

  deleteFile: async (fileId: string) => {
    const response = await api.delete(`/api/upload/file/${fileId}`);
    return response.data;
  },
};

// Profile Pictures API
export const profilePicturesAPI = {
  uploadPicture: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/api/profile-pictures/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  uploadMultiplePictures: async (files: File[]) => {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    const response = await api.post('/api/profile-pictures/upload-multiple', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  listPictures: async () => {
    const response = await api.get('/api/profile-pictures/list');
    return response.data;
  },

  setCurrentPicture: async (pictureId: number) => {
    const response = await api.post(`/api/profile-pictures/${pictureId}/set-current`);
    return response.data;
  },

  deletePicture: async (pictureId: number) => {
    const response = await api.delete(`/api/profile-pictures/${pictureId}`);
    return response.data;
  },
};

// Posts API
export const postsAPI = {
  getPosts: async () => {
    const response = await api.get('/api/posts');
    return response.data.posts || []; // Return the posts array, default to empty array
  },

  getUserPosts: async (userId: number) => {
    const response = await api.get(`/api/posts/user/${userId}`);
    return response.data.posts || []; // Return the posts array, default to empty array
  },

  createPost: async (postData: {
    content: string;
    image_url?: string;
    video_url?: string;
  }) => {
    const response = await api.post('/api/posts', postData);
    return response.data;
  },

  likePost: async (postId: number) => {
    const response = await api.post(`/api/posts/${postId}/like`);
    return response.data;
  },

  deletePost: async (postId: number) => {
    const response = await api.delete(`/api/posts/${postId}`);
    return response.data;
  },

  updatePost: async (postId: number, postData: { content: string }) => {
    const response = await api.put(`/api/posts/${postId}`, postData);
    return response.data;
  },

  getComments: async (postId: number) => {
    const response = await api.get(`/api/posts/${postId}/comments`);
    return response.data.comments || [];
  },

  createComment: async (postId: number, content: string) => {
    const response = await api.post(`/api/posts/${postId}/comments`, { content });
    return response.data;
  },

  deleteComment: async (postId: number, commentId: number) => {
    const response = await api.delete(`/api/posts/${postId}/comments/${commentId}`);
    return response.data;
  },
};

// HireMe API
export const hireMeAPI = {
  getAvailableUsers: async (searchQuery: string = '') => {
    const params = searchQuery ? { search: searchQuery } : {};
    const response = await api.get('/api/hireme/available', { params });
    return response.data;
  },

  toggleAvailability: async () => {
    const response = await api.post('/api/hireme/toggle');
    return response.data;
  },
};

/**
 * Validate and normalize a user ID for API requests.
 * @param userId - The user ID to validate (can be string or number)
 * @returns The validated and normalized user ID as a string
 * @throws Error if the user ID is invalid
 */
function validateUserId(userId: number | string): string {
  // Convert to string for consistent handling
  const id = typeof userId === 'string' ? userId.trim() : String(userId);
  
  // Check for empty, null, undefined, or NaN values
  if (!id || id === '' || id === 'NaN' || id === 'undefined' || id === 'null') {
    throw new Error('Invalid user ID');
  }
  
  // Additional validation: if it looks like a number, ensure it's positive
  if (/^\d+$/.test(id)) {
    const numId = parseInt(id, 10);
    if (isNaN(numId) || numId <= 0) {
      throw new Error('Invalid user ID');
    }
  }
  
  return id;
}

// Users API
export const usersAPI = {
  followUser: async (userId: number | string) => {
    const id = validateUserId(userId);
    const response = await api.post(`/api/users/follow/${id}`);
    return response.data;
  },

  unfollowUser: async (userId: number | string) => {
    const id = validateUserId(userId);
    const response = await api.post(`/api/users/unfollow/${id}`);
    return response.data;
  },

  getFollowers: async (): Promise<FollowersResponse> => {
    const response = await api.get('/api/users/followers/list');
    return response.data;
  },

  getFollowing: async (): Promise<FollowingResponse> => {
    const response = await api.get('/api/users/following/list');
    return response.data;
  },

  getUserFollowers: async (userId: number | string): Promise<FollowersResponse> => {
    const id = validateUserId(userId);
    const response = await api.get(`/api/users/${id}/followers`);
    return response.data;
  },

  getUserFollowing: async (userId: number | string): Promise<FollowingResponse> => {
    const id = validateUserId(userId);
    const response = await api.get(`/api/users/${id}/following`);
    return response.data;
  },

  /**
   * Get list of users with optional search
   */
  getUsers: async (params?: { search?: string; skip?: number; limit?: number }) => {
    const response = await api.get('/api/users/list', { params });
    return response.data;
  },
};

// Notifications API
export const notificationsAPI = {
  getNotifications: async (params?: {
    skip?: number;
    limit?: number;
    unread_only?: boolean;
  }) => {
    const response = await api.get('/api/notifications/list', { params });
    return response.data;
  },

  getUnreadCount: async () => {
    const response = await api.get('/api/notifications/unread-count');
    return response.data;
  },

  markAsRead: async (notificationId: number) => {
    const response = await api.put(`/api/notifications/${notificationId}/read`);
    return response.data;
  },

  markAllAsRead: async () => {
    const response = await api.put('/api/notifications/mark-all-read');
    return response.data;
  },
};

/**
 * Fetch wrapper for API requests with proper type safety and error handling
 * 
 * @param path - The API path (e.g., "/api/auth/me")
 * @param options - Optional fetch RequestInit options
 * @returns Promise with typed response data
 * @throws Error if the API response is not OK
 * 
 * @example
 * ```typescript
 * const user = await apiFetch<User>("/api/auth/me");
 * ```
 */
export async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(apiUrl(path), {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {})
    }
  });

  if (!res.ok) {
    throw new Error(`API error ${res.status}`);
  }

  return res.json();
}

export default api;