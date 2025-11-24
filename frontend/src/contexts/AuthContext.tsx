import { createContext, useContext, useEffect, useState, ReactNode, useCallback } from 'react';
import { User } from '../types/user';
import { authAPI } from '../services/api';
import toast from 'react-hot-toast';
import { sessionManager } from '../services/sessionManager';

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
          
          // Check if token needs refresh
          const expiresAt = sessionManager.getTokenExpiration(savedSession.token);
          if (expiresAt && sessionManager.shouldRefreshToken(expiresAt)) {
            try {
              await refreshTokenInternal();
            } catch (error) {
              console.error('Token refresh failed during initialization:', error);
            }
          }
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
              localStorage.removeItem('token');
              sessionManager.clearSession();
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
      
      // Redirect to login if not already there
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    });
  }, []);

  // Token refresh function
  const refreshTokenInternal = async () => {
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
      throw error;
    }
  };

  const refreshToken = useCallback(async () => {
    try {
      await refreshTokenInternal();
    } catch (error) {
      console.error('Manual token refresh failed:', error);
      throw error;
    }
  }, [rememberMe]);

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
        }
      }
    };

    // Check every 10 minutes
    const interval = setInterval(checkAndRefresh, 10 * 60 * 1000);
    
    // Also check immediately
    checkAndRefresh();

    return () => clearInterval(interval);
  }, [token, rememberMe]);

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
    } catch (error: any) {
      console.error('AuthContext: Login error:', error);
      const errorMessage = error.response?.data?.error || error.response?.data?.message || error.message || 'Login failed';
      toast.error(errorMessage);
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
    } catch (error: any) {
      const message = error?.response?.data?.message || error?.message || 'Registration failed';
      toast.error(message);
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
    } catch (error: any) {
      console.error('AuthContext: Google OAuth error:', error);
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Google sign-in failed';
      toast.error(errorMessage);
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
    } catch (error: any) {
      console.error('AuthContext: Apple OAuth error:', error);
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Apple sign-in failed';
      toast.error(errorMessage);
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
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Profile update failed');
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