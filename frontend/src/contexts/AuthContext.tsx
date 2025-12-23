/* eslint-disable react-refresh/only-export-components */
// Context files export both Provider components and custom hooks
import { createContext, useContext, useEffect, useState, ReactNode, useCallback } from 'react';
import { User } from '../types/user';
import { authAPI } from '../services/api';
import toast from 'react-hot-toast';
import { sessionManager } from '../services/sessionManager';
import { ApiError } from '../types';
import { loginWithRetry, registerWithRetry } from '../utils/retryWithBackoff';
import { getSession } from '../services/auth';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  rememberMe: boolean;
  login: (email: string, password: string, rememberMe?: boolean) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  loginWithGoogle: (token: string, userType?: string) => Promise<void>;
  loginWithApple: (token: string, userType?: string) => Promise<void>;
  logout: () => void;
  updateProfile: (data: Partial<User>) => Promise<void>;
  refreshToken: () => Promise<void>;
  setRememberMe: (remember: boolean) => void;
}

interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  user_type: 'freelancer' | 'client' | 'employer' | 'recruiter';
  location: string;
  phone?: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [rememberMe, setRememberMeState] = useState(false);

  // Token refresh function - memoized to prevent useEffect dependency issues
  // Must be defined before useEffects that depend on it
  const refreshTokenInternal = useCallback(async () => {
    const currentToken = localStorage.getItem('token');
    if (!currentToken) {
      throw new Error('No token to refresh');
    }

    try {
      // Call refresh token endpoint
      const response = await authAPI.refreshToken();
      
      if (response.access_token) {
        // Update with new token
        localStorage.setItem('token', response.access_token);
        setToken(response.access_token);
        setUser(response.user);
        
        // Update session with new token and data
        const expiresAt = sessionManager.getTokenExpiration(response.access_token);
        sessionManager.saveSession({
          token: response.access_token,
          user: response.user,
          lastActivity: Date.now(),
          expiresAt: expiresAt || Date.now() + 7 * 24 * 60 * 60 * 1000,
          rememberMe,
        });
        
        console.log('Token refreshed successfully');
        return true;
      } else {
        throw new Error('No token in refresh response');
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      
      // Check if it's an auth error (401/403) - means token is invalid
      const apiError = error as { response?: { status?: number }; code?: string };
      if (apiError.response?.status === 401 || apiError.response?.status === 403) {
        console.warn('Token is invalid or expired. User needs to log in again.');
        // Force logout to clear invalid state
        setToken(null);
        setUser(null);
        sessionManager.clearSession();
        return false;
      }
      
      // For network errors, don't clear session - just log and continue
      // The user can keep using their current token and retry later
      if (apiError.code === 'ERR_NETWORK' || apiError.code === 'ECONNREFUSED') {
        console.warn('Network error during token refresh. Will retry later.');
        return false;
      }
      
      // For other errors, be safe and don't throw
      return false;
    }
  }, [rememberMe]);

  const refreshToken = useCallback(async () => {
    try {
      await refreshTokenInternal();
    } catch (error) {
      console.error('Manual token refresh failed:', error);
      throw error;
    }
  }, [refreshTokenInternal]);

  // Initialize auth from session manager with getSession bootstrap
  // ✅ STEP 5: Frontend Auth Bootstrap - Call getSession() on app startup
  // This provides production-grade session restoration that is:
  // ✔ Page refresh safe
  // ✔ Safari safe (credentials: 'include')
  // ✔ Vercel safe (works with serverless deployments)
  useEffect(() => {
    const initializeAuth = async () => {
      const isDev = import.meta.env.DEV;
      
      try {
        if (isDev) console.log('[Auth Bootstrap] Initializing session...');
        
        // First, try to get session from backend (the official way)
        const sessionUser = await getSession();
        
        if (sessionUser) {
          // Session exists on backend - this is the source of truth
          if (isDev) console.log('[Auth Bootstrap] Session restored from backend:', sessionUser.email);
          setUser(sessionUser);
          
          // Get stored token for API calls (if available)
          const storedToken = localStorage.getItem('token');
          if (storedToken) {
            setToken(storedToken);
            
            // Check if we have a saved session to get the original rememberMe preference
            const savedSession = sessionManager.loadSession();
            // Default to true if backend session exists (user chose persistent session previously)
            // This handles the case where local session data was cleared but backend cookie remains
            const rememberMePreference = savedSession?.rememberMe ?? true;
            
            // Save/update session in session manager
            const expiresAt = sessionManager.getTokenExpiration(storedToken);
            sessionManager.saveSession({
              token: storedToken,
              user: sessionUser,
              lastActivity: Date.now(),
              expiresAt: expiresAt || Date.now() + 7 * 24 * 60 * 60 * 1000,
              rememberMe: rememberMePreference,
            });
            setRememberMeState(rememberMePreference);
          } else {
            // Backend has session but we don't have token locally
            // This can happen after browser restart with cookies
            if (isDev) console.log('[Auth Bootstrap] Backend session exists but no local token - will refresh');
          }
        } else {
          // No backend session - try local session manager as fallback
          if (isDev) console.log('[Auth Bootstrap] No backend session, checking local session...');
          const savedSession = sessionManager.loadSession();
          
          if (savedSession) {
            // Local session exists, attempt to restore it
            setToken(savedSession.token);
            setUser(savedSession.user);
            setRememberMeState(savedSession.rememberMe);
            if (isDev) console.log('[Auth Bootstrap] Local session restored:', savedSession.user.email);
          } else {
            // Final fallback: check for bare token in localStorage
            const storedToken = localStorage.getItem('token');
            if (storedToken) {
              try {
                if (isDev) console.log('[Auth Bootstrap] Attempting profile fetch with stored token...');
                const userData = await authAPI.getProfile();
                setUser(userData);
                setToken(storedToken);
                
                // Migrate to new session management
                const expiresAt = sessionManager.getTokenExpiration(storedToken);
                sessionManager.saveSession({
                  token: storedToken,
                  user: userData,
                  lastActivity: Date.now(),
                  expiresAt: expiresAt || Date.now() + 7 * 24 * 60 * 60 * 1000,
                  rememberMe: false,
                });
                if (isDev) console.log('[Auth Bootstrap] Token migration successful:', userData.email);
              } catch (error) {
                console.error('[Auth Bootstrap] Profile fetch failed:', error);
                // Only clear session if it's a genuine auth error, not a network error
                const apiError = error as { code?: string; message?: string };
                const isNetworkError = apiError?.code === 'ERR_NETWORK' || 
                                      apiError?.message?.includes('Network Error');
                
                if (!isNetworkError) {
                  // Genuine auth failure - clear invalid session
                  localStorage.removeItem('token');
                  sessionManager.clearSession();
                  if (isDev) console.log('[Auth Bootstrap] Invalid token cleared');
                } else {
                  // Network error - keep session for retry
                  if (isDev) console.warn('[Auth Bootstrap] Network error - keeping session for retry');
                }
              }
            } else {
              if (isDev) console.log('[Auth Bootstrap] No session found - user is not authenticated');
            }
          }
        }
      } catch (error) {
        console.error('[Auth Bootstrap] Failed to initialize auth:', error);
      } finally {
        setIsLoading(false);
        if (isDev) console.log('[Auth Bootstrap] Initialization complete');
      }
    };

    initializeAuth();
  }, []);

  // Setup session expiration handlers
  useEffect(() => {
    // Handler for session expiring warning (5 minutes before timeout)
    const handleExpiring = () => {
      console.warn('Session expiring soon');
      // Note: Warning threshold is defined in sessionManager (5 minutes)
      toast('Your session will expire soon. Please save your work.', {
        duration: 10000,
        icon: '⏰',
      });
    };

    // Handler for session expired
    const handleExpired = () => {
      setToken(null);
      setUser(null);
      toast.error('Your session has expired. Please log in again.');
      
      // Save current location for redirect after login
      const currentPath = window.location.pathname;
      if (currentPath !== '/login' && currentPath !== '/register') {
        sessionStorage.setItem('redirectAfterLogin', currentPath);
      }
      
      // Redirect to login if not already there
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    };

    sessionManager.onExpiring(handleExpiring);
    sessionManager.onExpired(handleExpired);

    // Cleanup function - clean up session manager resources on unmount
    return () => {
      // Note: Only cleanup if this is truly the last AuthProvider unmounting
      // In most apps, AuthProvider stays mounted for the entire session
      // Uncomment if you need to support dynamic AuthProvider mounting/unmounting
      // sessionManager.cleanup();
    };
  }, []);

  // Setup automatic token refresh
  useEffect(() => {
    if (!token) return;

    const expiresAt = sessionManager.getTokenExpiration(token);
    if (!expiresAt) return;

    const checkAndRefresh = async () => {
      if (sessionManager.shouldRefreshToken(expiresAt)) {
        try {
          await refreshTokenInternal();
        } catch (error) {
          console.error('Auto token refresh failed:', error);
          // Don't force logout on refresh failure - user might be offline
          // The token will be validated on next API call if needed
        }
      }
    };

    // Check every 10 minutes
    const interval = setInterval(checkAndRefresh, 10 * 60 * 1000);
    
    // Also check immediately (but don't block initialization)
    checkAndRefresh().catch((err) => {
      console.error('Initial token refresh check failed:', err);
    });

    return () => clearInterval(interval);
  }, [token, refreshTokenInternal]);

  const login = async (email: string, password: string, remember: boolean = false) => {
    try {
      console.log('AuthContext: Starting login for:', email);
      
      // Use retry logic with user-friendly error handling
      const response = await loginWithRetry(
        { email, password },
        (credentials) => authAPI.login(credentials),
        (message, attempt) => {
          // Show progress to user during retries
          console.log(`[Login Retry ${attempt}]`, message);
          
          // Show toast for all retry attempts (attempt starts at 1 for first retry)
          if (attempt >= 1) {
            toast.loading(message, { 
              id: 'login-retry',
              duration: 20000 // Keep showing during the wait
            });
          }
        }
      );
      
      console.log('AuthContext: Login response received:', response);
      
      if (!response.access_token) {
        console.error('AuthContext: No token in response:', response);
        throw new Error('No authentication token received');
      }
      
      if (!response.user) {
        console.error('AuthContext: No user in response:', response);
        throw new Error('No user data received');
      }
      
      // Dismiss any retry loading toasts
      toast.dismiss('login-retry');
      
      // Save to localStorage for backward compatibility
      localStorage.setItem('token', response.access_token);
      setToken(response.access_token);
      setUser(response.user);
      setRememberMeState(remember);
      
      // Save session with encryption
      const expiresAt = sessionManager.getTokenExpiration(response.access_token);
      sessionManager.saveSession({
        token: response.access_token,
        user: response.user,
        lastActivity: Date.now(),
        expiresAt: expiresAt || Date.now() + 7 * 24 * 60 * 60 * 1000,
        rememberMe: remember,
      });
      
      console.log('AuthContext: Login successful, user set:', response.user);
      toast.success('Login successful!');
    } catch (error: unknown) {
      console.error('AuthContext: Login error:', error);
      // Dismiss any retry loading toasts
      toast.dismiss('login-retry');
      // Note: Do not show toast here - let the caller (Login.tsx) handle error display
      // to avoid duplicate toast notifications
      throw error;
    }
  };

  const register = async (userData: RegisterData) => {
    try {
      // Use retry logic with user-friendly error handling
      const response = await registerWithRetry(
        userData,
        (data) => authAPI.register(data),
        (message, attempt) => {
          // Show progress to user during retries
          console.log(`[Register Retry ${attempt}]`, message);
          
          // Show toast for all retry attempts (attempt starts at 1 for first retry)
          if (attempt >= 1) {
            toast.loading(message, {
              id: 'register-retry',
              duration: 20000
            });
          }
        }
      );
      
      if (!response?.access_token || !response?.user) {
        throw new Error(response?.message || 'Registration failed');
      }
      
      // Dismiss any retry loading toasts
      toast.dismiss('register-retry');
      
      localStorage.setItem('token', response.access_token);
      setToken(response.access_token);
      setUser(response.user);
      
      // Save session
      const expiresAt = sessionManager.getTokenExpiration(response.access_token);
      sessionManager.saveSession({
        token: response.access_token,
        user: response.user,
        lastActivity: Date.now(),
        expiresAt: expiresAt || Date.now() + 7 * 24 * 60 * 60 * 1000,
        rememberMe: false,
      });
      
      toast.success('Registration successful!');
    } catch (error: unknown) {
      console.error('AuthContext: Registration error:', error);
      // Dismiss any retry loading toasts
      toast.dismiss('register-retry');
      // Note: Do not show toast here - let the caller (Register.tsx) handle error display
      // to avoid duplicate toast notifications
      throw error;
    }
  };

  const loginWithGoogle = async (token: string, userType?: string) => {
    try {
      console.log('AuthContext: Starting Google OAuth login');
      const response = await authAPI.googleLogin(token, userType);
      console.log('AuthContext: Google OAuth response received:', response);
      
      if (!response.access_token) {
        console.error('AuthContext: No token in Google OAuth response:', response);
        throw new Error('No authentication token received');
      }
      
      if (!response.user) {
        console.error('AuthContext: No user in Google OAuth response:', response);
        throw new Error('No user data received');
      }
      
      // Save to localStorage for backward compatibility
      localStorage.setItem('token', response.access_token);
      setToken(response.access_token);
      setUser(response.user);
      setRememberMeState(true); // OAuth logins are persistent by default
      
      // Save session with encryption
      const expiresAt = sessionManager.getTokenExpiration(response.access_token);
      sessionManager.saveSession({
        token: response.access_token,
        user: response.user,
        lastActivity: Date.now(),
        expiresAt: expiresAt || Date.now() + 7 * 24 * 60 * 60 * 1000,
        rememberMe: true,
      });
      
      console.log('AuthContext: Google OAuth login successful, user set:', response.user);
      toast.success('Google sign-in successful!');
    } catch (error: unknown) {
      console.error('AuthContext: Google OAuth error:', error);
      // Note: Do not show toast here - let the caller (Login.tsx/Register.tsx) handle error display
      // to avoid duplicate toast notifications
      throw error;
    }
  };

  const loginWithApple = async (token: string, userType?: string) => {
    try {
      console.log('AuthContext: Starting Apple OAuth login');
      const response = await authAPI.appleLogin(token, userType);
      console.log('AuthContext: Apple OAuth response received:', response);
      
      if (!response.access_token) {
        console.error('AuthContext: No token in Apple OAuth response:', response);
        throw new Error('No authentication token received');
      }
      
      if (!response.user) {
        console.error('AuthContext: No user in Apple OAuth response:', response);
        throw new Error('No user data received');
      }
      
      // Save to localStorage for backward compatibility
      localStorage.setItem('token', response.access_token);
      setToken(response.access_token);
      setUser(response.user);
      setRememberMeState(true); // OAuth logins are persistent by default
      
      // Save session with encryption
      const expiresAt = sessionManager.getTokenExpiration(response.access_token);
      sessionManager.saveSession({
        token: response.access_token,
        user: response.user,
        lastActivity: Date.now(),
        expiresAt: expiresAt || Date.now() + 7 * 24 * 60 * 60 * 1000,
        rememberMe: true,
      });
      
      console.log('AuthContext: Apple OAuth login successful, user set:', response.user);
      toast.success('Apple sign-in successful!');
    } catch (error: unknown) {
      console.error('AuthContext: Apple OAuth error:', error);
      // Note: Do not show toast here - let the caller (Login.tsx/Register.tsx) handle error display
      // to avoid duplicate toast notifications
      throw error;
    }
  };

  const logout = () => {
    // Clear all session data
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setRememberMeState(false);
    sessionManager.clearSession();
    toast.success('Logged out successfully');
  };

  const updateProfile = async (data: Partial<User>) => {
    try {
      const updatedUser = await authAPI.updateProfile(data);
      setUser(updatedUser);
      
      // Update session with new user data
      const savedSession = sessionManager.loadSession();
      if (savedSession) {
        sessionManager.saveSession({
          ...savedSession,
          user: updatedUser,
        });
      }
      
      toast.success('Profile updated successfully!');
    } catch (error: unknown) {
      const apiError = error as ApiError;
      toast.error(apiError.response?.data?.detail || apiError.response?.data?.message || 'Profile update failed');
      throw error;
    }
  };

  const setRememberMe = (remember: boolean) => {
    setRememberMeState(remember);
    const savedSession = sessionManager.loadSession();
    if (savedSession) {
      sessionManager.saveSession({
        ...savedSession,
        rememberMe: remember,
      });
    }
  };

  const value: AuthContextType = {
    user,
    token,
    isLoading,
    isAuthenticated: !!user,
    rememberMe,
    login,
    register,
    loginWithGoogle,
    loginWithApple,
    logout,
    updateProfile,
    refreshToken,
    setRememberMe,
  };

  // ✅ Auth Boot Guard: Prevent rendering children until auth state is initialized
  // This prevents:
  // - Blank screen on refresh
  // - Mobile cold-start crashes
  // - Token race conditions
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading session…</p>
        </div>
      </div>
    );
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};