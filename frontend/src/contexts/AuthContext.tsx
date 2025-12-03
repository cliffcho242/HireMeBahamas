/* eslint-disable react-refresh/only-export-components */
// Context files export both Provider components and custom hooks
import { createContext, useContext, useEffect, useState, ReactNode, useCallback } from 'react';
import { User } from '../types/user';
import { authAPI } from '../services/api';
import toast from 'react-hot-toast';
import { sessionManager } from '../services/sessionManager';
import { ApiError } from '../types';

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
      } else {
        throw new Error('No token in refresh response');
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      // Don't throw - just log the error to prevent breaking the app
      // The user can continue using their current token until it expires
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

  // Initialize auth from session manager
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // Try to restore session from session manager
        const savedSession = sessionManager.loadSession();
        
        if (savedSession) {
          // Session exists, restore it
          setToken(savedSession.token);
          setUser(savedSession.user);
          setRememberMeState(savedSession.rememberMe);
          
          // Check if token needs refresh - do this in a separate effect
          // to avoid calling refreshTokenInternal before it's stable
        } else {
          // Fallback to old method if session doesn't exist
          const storedToken = localStorage.getItem('token');
          if (storedToken) {
            try {
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
            } catch (error) {
              console.error('Auth initialization failed:', error);
              // Only clear session if it's a genuine auth error, not a network error
              const apiError = error as { code?: string; message?: string };
              const isNetworkError = apiError?.code === 'ERR_NETWORK' || 
                                    apiError?.message?.includes('Network Error');
              
              if (!isNetworkError) {
                // Genuine auth failure - clear invalid session
                localStorage.removeItem('token');
                sessionManager.clearSession();
              } else {
                // Network error - keep session for retry
                console.warn('Network error during auth init - keeping session for retry');
              }
            }
          }
        }
      } catch (error) {
        console.error('Failed to initialize auth:', error);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // Setup session expiration handlers
  useEffect(() => {
    sessionManager.onExpired(() => {
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
    });
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
      const response = await authAPI.login({ email, password });
      console.log('AuthContext: Login response received:', response);
      
      if (!response.access_token) {
        console.error('AuthContext: No token in response:', response);
        throw new Error('No authentication token received');
      }
      
      if (!response.user) {
        console.error('AuthContext: No user in response:', response);
        throw new Error('No user data received');
      }
      
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
      // Note: Do not show toast here - let the caller (Login.tsx) handle error display
      // to avoid duplicate toast notifications
      throw error;
    }
  };

  const register = async (userData: RegisterData) => {
    try {
      const response = await authAPI.register(userData);
      if (!response?.access_token || !response?.user) {
        throw new Error(response?.message || 'Registration failed');
      }
      
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
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
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

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};