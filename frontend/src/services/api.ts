import axios from 'axios';
import { User } from '../types/user';
import { Job } from '../types/job';

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

// Derive API base URL with safe production fallback
const DEFAULT_PROD_API = 'https://hiremebahamas.onrender.com';
const ENV_API = (import.meta as ImportMeta & { env?: { VITE_API_URL?: string } }).env?.VITE_API_URL;
let API_BASE_URL = ENV_API || 'http://127.0.0.1:9999';

// If no env is set and we're on the hiremebahamas.com domain, use the Render backend
if (!ENV_API && typeof window !== 'undefined') {
  const origin = window.location.origin;
  if (origin.includes('hiremebahamas.com')) {
    API_BASE_URL = DEFAULT_PROD_API;
  }
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

// Retry configuration
const MAX_RETRIES = 5;
const RETRY_DELAY = 3000; // 3 seconds base delay for retries
const BACKEND_WAKE_TIME = 120000; // 120 seconds (2 minutes) for Render.com free tier cold starts

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

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  // Add retry count
  config.headers['X-Retry-Count'] = config.headers['X-Retry-Count'] || 0;
  
  console.log('API Request:', config.method?.toUpperCase(), config.url);
  return config;
});

// Handle auth errors with automatic retry
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.config.url, response.status);
    return response;
  },
  async (error) => {
    const config = error.config;
    
    console.error('API Error:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      message: error.message,
      data: error.response?.data
    });
    
    // Check if backend is sleeping (Render.com free tier)
    if (isBackendSleeping(error)) {
      const retryCount = parseInt(config.headers['X-Retry-Count'] || '0');
      const maxWakeRetries = 4; // More retries for cold start scenarios
      
      if (retryCount < maxWakeRetries) {
        const isFirstRetry = retryCount === 0;
        
        if (isFirstRetry) {
          console.log('Backend appears to be sleeping or starting up...');
          console.log('This may take 1-2 minutes on first request (cold start).');
          console.log('Status:', error.response?.status || 'No response');
        } else {
          console.log(`Backend still waking up... Retry ${retryCount + 1}/${maxWakeRetries}`);
        }
        
        // Increase timeout for wake-up
        config.timeout = BACKEND_WAKE_TIME;
        config.headers['X-Retry-Count'] = retryCount + 1;
        
        // Exponential backoff: 5s, 10s, 20s, 30s
        const waitTime = isFirstRetry ? 5000 : Math.min(10000 * Math.pow(2, retryCount - 1), 30000);
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
      const retryCount = parseInt(config.headers['X-Retry-Count'] || '0');
      
      if (retryCount < MAX_RETRIES) {
        config.headers['X-Retry-Count'] = retryCount + 1;
        console.log(`Retrying request (${retryCount + 1}/${MAX_RETRIES})...`);
        
        // Wait before retrying
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY * (retryCount + 1)));
        
        return api(config);
      }
      
      console.error('Max retries reached. Network error persists.');
    }
    
    // Handle auth errors
    if (error.response?.status === 401) {
      // Only auto-logout for auth endpoints or profile endpoints
      const isAuthEndpoint = config.url?.includes('/auth/') || config.url?.includes('/profile');
      
      if (isAuthEndpoint) {
        console.log('Authentication failed - logging out');
        localStorage.removeItem('token');
        window.location.href = '/login';
      } else {
        // For other endpoints, just log the error but don't force logout
        console.warn('Unauthorized access to:', config.url);
      }
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
      timeout: BACKEND_WAKE_TIME, // 2 minutes for cold start + password verification
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
      timeout: BACKEND_WAKE_TIME, // 2 minutes for cold start + password hashing
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

// Users API
export const usersAPI = {
  followUser: async (userId: number) => {
    const response = await api.post(`/api/users/follow/${userId}`);
    return response.data;
  },

  unfollowUser: async (userId: number) => {
    const response = await api.post(`/api/users/unfollow/${userId}`);
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

  getUserFollowers: async (userId: number): Promise<FollowersResponse> => {
    const response = await api.get(`/api/users/${userId}/followers`);
    return response.data;
  },

  getUserFollowing: async (userId: number): Promise<FollowingResponse> => {
    const response = await api.get(`/api/users/${userId}/following`);
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

export default api;