import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { User } from '../types/user';
import { authAPI } from '../services/api';
import toast from 'react-hot-toast';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  updateProfile: (data: Partial<User>) => Promise<void>;
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
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const userData = await authAPI.getProfile();
          setUser(userData);
        } catch (error) {
          localStorage.removeItem('token');
          console.error('Auth initialization failed:', error);
        }
      }
      setIsLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (email: string, password: string) => {
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
      
      localStorage.setItem('token', response.access_token);
      setToken(response.access_token);
      setUser(response.user);
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
      toast.success('Registration successful!');
    } catch (error: any) {
      const message = error?.response?.data?.message || error?.message || 'Registration failed';
      toast.error(message);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    toast.success('Logged out successfully');
  };

  const updateProfile = async (data: Partial<User>) => {
    try {
      const updatedUser = await authAPI.updateProfile(data);
      setUser(updatedUser);
      toast.success('Profile updated successfully!');
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Profile update failed');
      throw error;
    }
  };

  const value: AuthContextType = {
    user,
    token,
    isLoading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    updateProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};