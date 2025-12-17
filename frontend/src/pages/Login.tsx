import { ButtonHTMLAttributes, FormEvent, useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import AppleSignin from 'react-apple-signin-auth';
import { getOAuthConfig } from '../utils/oauthConfig';
import { GoogleCredentialResponse, AppleSignInResponse } from '../types';
import { useLoadingMessages, DEFAULT_AUTH_MESSAGES } from '../hooks/useLoadingMessages';
import { runConnectionDiagnostic, testConnection, getCurrentApiUrl } from '../utils/connectionTest';
import { showFriendlyError } from '../utils/friendlyErrors';
import {
  UserIcon,
  BriefcaseIcon,
  ChatBubbleLeftRightIcon,
  HeartIcon,
  PhotoIcon,
  VideoCameraIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

const Login = () => {
  const { login, loginWithGoogle, loginWithApple, isLoading, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'checking' | 'connected' | 'disconnected' | null>(null);
  const [connectionMessage, setConnectionMessage] = useState<string>('');
  
  // Generate particles once on mount for better performance
  const particles = useMemo(() => 
    Array.from({ length: 20 }, (_, i) => ({
      id: i,
      left: `${Math.random() * 100}%`,
      top: `${Math.random() * 100}%`,
      delay: Math.random() * 2,
      duration: 3 + Math.random() * 2,
    })), []
  );
  
  // Use custom hook for progressive loading messages
  const { loadingMessage, startLoading, stopLoading } = useLoadingMessages({
    messages: DEFAULT_AUTH_MESSAGES,
  });

  // Check OAuth configuration using utility function
  const oauthConfig = getOAuthConfig();
  const isGoogleOAuthEnabled = oauthConfig.google.enabled;
  const isAppleOAuthEnabled = oauthConfig.apple.enabled;
  const isAnyOAuthEnabled = oauthConfig.isAnyEnabled;
  const googleClientId = oauthConfig.google.clientId || '';
  const appleClientId = oauthConfig.apple.clientId || '';

  // Get the redirect path from location state (saved by ProtectedRoute)
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/';

  // Test backend connection on mount
  useEffect(() => {
    const checkConnection = async () => {
      setConnectionStatus('checking');
      
      // Run diagnostic in console
      if (import.meta.env.DEV) {
        await runConnectionDiagnostic();
      }
      
      // Test connection to current API
      const apiUrl = getCurrentApiUrl();
      const result = await testConnection(apiUrl);
      
      // Also test both backends if in dual mode
      const renderUrl = import.meta.env.VITE_RENDER_API_URL;
      if (renderUrl && apiUrl !== renderUrl) {
        console.log('🔍 Testing Render backend...');
        const renderResult = await testConnection(renderUrl);
        console.log('Render backend:', renderResult.success ? '✅ Available' : '❌ Unavailable');
      }
      
      if (result.success) {
        setConnectionStatus('connected');
        const backendInfo = renderUrl ? ' (Dual backend: Vercel + Render)' : '';
        setConnectionMessage(`Connected to backend${backendInfo}`);
      } else {
        setConnectionStatus('disconnected');
        
        // Use user-friendly message for cold start scenarios
        const helpMessage = result.message.includes('timeout') 
          ? 'Backend is starting up (cold start). This can take 30-60 seconds. Please wait and try logging in.'
          : result.message;
        
        setConnectionMessage(helpMessage);
        
        toast.error(
          `Backend connection: ${helpMessage}`,
          { duration: 10000 }
        );
      }
    };
    
    checkConnection();
  }, []);

  // Redirect authenticated users to home or their intended destination
  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, from]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (submitting) return;
    setSubmitting(true);
    startLoading();
    
    try {
      // Only log in development mode to avoid exposing PII
      if (import.meta.env.DEV) {
        console.log('=== LOGIN ATTEMPT ===');
        console.log('Email:', email);
        console.log('API URL:', import.meta.env.VITE_API_URL || 'Same-origin (default)');
        console.log('Window location:', window.location.origin);
      }
      
      await login(email, password);
      
      if (import.meta.env.DEV) {
        console.log('=== LOGIN SUCCESS ===');
      }
      toast.success('Welcome back to HireMeBahamas!');
      // Navigate to intended destination or home
      navigate(from, { replace: true });
    } catch (error: unknown) {
      // Only log detailed error info in development
      if (import.meta.env.DEV) {
        console.error('=== LOGIN ERROR ===');
        console.error('Error object:', error);
      }
      
      // Use friendly error handler - NO GENERIC ERRORS!
      showFriendlyError(error, toast);
    } finally {
      stopLoading();
      setSubmitting(false);
    }
  };

  const handleGoogleSuccess = async (credentialResponse: GoogleCredentialResponse) => {
    try {
      if (credentialResponse.credential) {
        await loginWithGoogle(credentialResponse.credential);
        // Navigate to intended destination or home
        navigate(from, { replace: true });
      }
    } catch (error: unknown) {
      console.error('Google login error:', error);
      showFriendlyError(error, toast);
    }
  };

  const handleGoogleError = () => {
    toast.error('Google sign-in failed. Please try again or use email/password login.');
  };

  const handleAppleSuccess = async (response: AppleSignInResponse) => {
    try {
      if (response.authorization?.id_token) {
        await loginWithApple(response.authorization.id_token);
        // Navigate to intended destination or home
        navigate(from, { replace: true });
      }
    } catch (error: unknown) {
      console.error('Apple login error:', error);
      showFriendlyError(error, toast);
    }
  };

  const handleAppleError = (error: unknown) => {
    console.error('Apple sign-in error:', error);
    toast.error('Apple sign-in failed. Please try again or use email/password login.');
  };

  const features = [
    { 
      icon: UserIcon, 
      text: 'Connect with professionals', 
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200'
    },
    { 
      icon: BriefcaseIcon, 
      text: 'Find your dream job', 
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-200'
    },
    { 
      icon: ChatBubbleLeftRightIcon, 
      text: 'Network and chat', 
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200'
    },
    { 
      icon: HeartIcon, 
      text: 'Share your success', 
      color: 'text-red-600',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200'
    },
    { 
      icon: PhotoIcon, 
      text: 'Post updates & stories', 
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200'
    },
    { 
      icon: VideoCameraIcon, 
      text: 'Join live events', 
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
      borderColor: 'border-indigo-200'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-indigo-950 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse delay-1000" />
        <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse delay-500" />
      </div>

      {/* Floating Particles */}
      <div className="absolute inset-0 pointer-events-none">
        {particles.map((particle) => (
          <motion.div
            key={particle.id}
            className="absolute w-1 h-1 bg-white rounded-full opacity-30"
            style={{
              left: particle.left,
              top: particle.top,
            }}
            animate={{
              y: [0, -30, 0],
              opacity: [0.3, 0.8, 0.3],
            }}
            transition={{
              duration: particle.duration,
              repeat: Infinity,
              delay: particle.delay,
            }}
          />
        ))}
      </div>

      {/* Connection Status Banner */}
      {connectionStatus && connectionStatus !== 'connected' && (() => {
        const isColdStart = connectionMessage.includes('cold start');
        return (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`fixed top-0 left-0 right-0 z-50 ${
              connectionStatus === 'checking' 
                ? 'bg-gradient-to-r from-yellow-500 to-orange-500' 
                : isColdStart
                  ? 'bg-gradient-to-r from-blue-500 to-indigo-500'
                  : 'bg-gradient-to-r from-red-500 to-pink-500'
            } text-white px-4 py-3 shadow-lg backdrop-blur-sm`}
          >
            <div className="container mx-auto flex flex-col sm:flex-row items-center justify-center space-y-1 sm:space-y-0 sm:space-x-2 text-center sm:text-left">
              {connectionStatus === 'checking' ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span className="font-medium">Checking backend connection...</span>
                </>
              ) : isColdStart ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-white flex-shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span className="font-semibold">⏱️ {connectionMessage}</span>
                </>
              ) : (
                <>
                  <ExclamationTriangleIcon className="h-5 w-5 flex-shrink-0" />
                  <span className="font-medium">{connectionMessage}</span>
                </>
              )}
            </div>
          </motion.div>
        );
      })()}

      
      {/* Hero Section */}
      <div className={`container mx-auto px-4 sm:px-6 relative z-10 ${connectionStatus && connectionStatus !== 'connected' ? 'pt-20 pb-4 sm:pb-8' : 'py-4 sm:py-8'}`}>
        <div className="grid lg:grid-cols-2 gap-8 lg:gap-12 items-center min-h-[calc(100vh-4rem)]">
          {/* Left Side - Branding */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center lg:text-left space-y-4 sm:space-y-6 lg:space-y-0"
          >
            {/* Logo with Glow Effect */}
            <motion.div 
              className="flex items-center justify-center lg:justify-start mb-4 sm:mb-6 lg:mb-8"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.2, duration: 0.5 }}
            >
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl sm:rounded-2xl blur-lg sm:blur-xl opacity-60 animate-pulse"></div>
                <div className="relative w-12 h-12 sm:w-14 sm:h-14 lg:w-16 lg:h-16 bg-gradient-to-br from-blue-600 via-cyan-500 to-blue-700 rounded-xl sm:rounded-2xl flex items-center justify-center shadow-2xl">
                  <span className="text-white font-bold text-lg sm:text-xl lg:text-2xl">HB</span>
                </div>
              </div>
              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold ml-3 sm:ml-4 bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-500 bg-clip-text text-transparent">
                HireMeBahamas
              </h1>
            </motion.div>

            {/* Tagline with Shimmer Effect */}
            <motion.h2 
              className="text-2xl sm:text-3xl lg:text-4xl xl:text-5xl font-bold text-white mb-3 sm:mb-4 lg:mb-6 leading-tight px-2 sm:px-0"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.6 }}
            >
              Connect. Share.<br />
              <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-500 bg-clip-text text-transparent">
                Grow Your Career.
              </span>
            </motion.h2>

            <motion.p 
              className="text-base sm:text-lg lg:text-xl text-slate-300 mb-4 sm:mb-6 lg:mb-8 max-w-lg mx-auto lg:mx-0 px-2 sm:px-0"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4, duration: 0.6 }}
            >
              Join the Bahamas' premier professional social network. Connect with employers, 
              showcase your talents, and discover amazing opportunities.
            </motion.p>

            {/* Features Grid - Glass Morphism - Responsive */}
            <div className="grid grid-cols-2 gap-2 sm:gap-3 lg:gap-4 max-w-lg mx-auto lg:mx-0 px-2 sm:px-0">
              {features.map((feature, index) => (
                <motion.div
                  key={feature.text}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 + 0.1 * index }}
                  whileHover={{ scale: 1.05, y: -5 }}
                  className="group relative cursor-pointer"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-xl sm:rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  <div className="relative backdrop-blur-xl bg-white/10 border border-white/20 rounded-xl sm:rounded-2xl p-2.5 sm:p-3 lg:p-4 shadow-xl hover:shadow-2xl transition-all duration-300">
                    <div className="flex items-center space-x-2 sm:space-x-3">
                      <div className={`p-1.5 sm:p-2 rounded-lg sm:rounded-xl bg-gradient-to-br ${feature.color === 'text-blue-600' ? 'from-blue-500 to-cyan-500' : feature.color === 'text-purple-600' ? 'from-purple-500 to-pink-500' : feature.color === 'text-green-600' ? 'from-green-500 to-emerald-500' : feature.color === 'text-red-600' ? 'from-red-500 to-rose-500' : feature.color === 'text-yellow-600' ? 'from-yellow-500 to-orange-500' : 'from-indigo-500 to-purple-500'}`}>
                        <feature.icon className="w-4 h-4 sm:w-5 sm:h-5 lg:w-6 lg:h-6 text-white" />
                      </div>
                      <span className="text-xs sm:text-sm font-medium text-white leading-tight">{feature.text}</span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Stats - Glassmorphism Design - Responsive */}
            <div className="mt-6 sm:mt-8 lg:mt-12 grid grid-cols-3 gap-2 sm:gap-3 lg:gap-4 max-w-lg mx-auto lg:mx-0 px-2 sm:px-0">
              <motion.div 
                className="group relative"
                whileHover={{ scale: 1.05 }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 }}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl sm:rounded-2xl blur-xl opacity-0 group-hover:opacity-60 transition-opacity duration-300" />
                <div className="relative backdrop-blur-xl bg-white/10 border border-white/20 rounded-xl sm:rounded-2xl p-2.5 sm:p-3 lg:p-4 text-center shadow-xl">
                  <div className="text-2xl sm:text-3xl lg:text-4xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">5K+</div>
                  <div className="text-[10px] sm:text-xs font-medium text-slate-300 mt-0.5 sm:mt-1">Professionals</div>
                </div>
              </motion.div>
              <motion.div 
                className="group relative"
                whileHover={{ scale: 1.05 }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.9 }}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl sm:rounded-2xl blur-xl opacity-0 group-hover:opacity-60 transition-opacity duration-300" />
                <div className="relative backdrop-blur-xl bg-white/10 border border-white/20 rounded-xl sm:rounded-2xl p-2.5 sm:p-3 lg:p-4 text-center shadow-xl">
                  <div className="text-2xl sm:text-3xl lg:text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">1K+</div>
                  <div className="text-[10px] sm:text-xs font-medium text-slate-300 mt-0.5 sm:mt-1">Job Posts</div>
                </div>
              </motion.div>
              <motion.div 
                className="group relative"
                whileHover={{ scale: 1.05 }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.0 }}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl sm:rounded-2xl blur-xl opacity-0 group-hover:opacity-60 transition-opacity duration-300" />
                <div className="relative backdrop-blur-xl bg-white/10 border border-white/20 rounded-xl sm:rounded-2xl p-2.5 sm:p-3 lg:p-4 text-center shadow-xl">
                  <div className="text-2xl sm:text-3xl lg:text-4xl font-bold bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text text-transparent">500+</div>
                  <div className="text-[10px] sm:text-xs font-medium text-slate-300 mt-0.5 sm:mt-1">Companies</div>
                </div>
              </motion.div>
            </div>
          </motion.div>

          {/* Right Side - Login Form with Ultra Modern Design - Responsive */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="max-w-md mx-auto w-full relative px-2 sm:px-0"
          >
            {/* Glow Effect */}
            <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 rounded-2xl sm:rounded-3xl blur-xl sm:blur-2xl opacity-30 animate-pulse" />
            
            {/* Glass Morphism Card */}
            <div className="relative backdrop-blur-2xl bg-white/10 border border-white/20 rounded-2xl sm:rounded-3xl shadow-2xl p-4 sm:p-6 lg:p-8 hover:shadow-cyan-500/50 transition-all duration-500">
              {/* Decorative Elements */}
              <div className="absolute top-0 right-0 w-24 sm:w-32 h-24 sm:h-32 bg-gradient-to-br from-cyan-500/20 to-blue-500/20 rounded-full blur-2xl sm:blur-3xl" />
              <div className="absolute bottom-0 left-0 w-24 sm:w-32 h-24 sm:h-32 bg-gradient-to-tr from-purple-500/20 to-pink-500/20 rounded-full blur-2xl sm:blur-3xl" />
              
              <div className="relative">
                <div className="text-center mb-4 sm:mb-6 lg:mb-8">
                  <motion.h2 
                    className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-white via-cyan-200 to-blue-200 bg-clip-text text-transparent mb-2"
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                  >
                    Log In to Your Account
                  </motion.h2>
                  <motion.p 
                    className="text-sm sm:text-base text-slate-300"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.4 }}
                  >
                    Enter your credentials to continue
                  </motion.p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-3 sm:space-y-4 lg:space-y-5">
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.5 }}
                  >
                    <label htmlFor="email" className="block text-xs sm:text-sm font-medium text-white mb-1.5 sm:mb-2">
                      Email or Phone
                    </label>
                    <div className="relative group">
                      <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-lg sm:rounded-xl opacity-0 group-hover:opacity-20 transition-opacity blur" />
                      <input
                        id="email"
                        type="text"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="relative w-full px-3 sm:px-4 py-2.5 sm:py-3 backdrop-blur-xl bg-white/10 border border-white/30 text-white placeholder-slate-400 rounded-lg sm:rounded-xl focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all focus:bg-white/15 text-sm sm:text-base"
                        placeholder="Enter your email"
                        required
                      />
                    </div>
                  </motion.div>
                  
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.6 }}
                  >
                    <label htmlFor="password" className="block text-xs sm:text-sm font-medium text-white mb-1.5 sm:mb-2">
                      Password
                    </label>
                    <div className="relative group">
                      <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg sm:rounded-xl opacity-0 group-hover:opacity-20 transition-opacity blur" />
                      <input
                        id="password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="relative w-full px-3 sm:px-4 py-2.5 sm:py-3 backdrop-blur-xl bg-white/10 border border-white/30 text-white placeholder-slate-400 rounded-lg sm:rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all focus:bg-white/15 text-sm sm:text-base"
                        placeholder="Enter your password"
                        required
                      />
                    </div>
                  </motion.div>

                  <motion.div 
                    className="flex items-center justify-between text-xs sm:text-sm"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.7 }}
                  >
                    <label className="flex items-center group cursor-pointer">
                      <input 
                        type="checkbox" 
                        className="rounded border-white/30 bg-white/10 text-cyan-500 focus:ring-cyan-500 focus:ring-offset-0 transition-all w-4 h-4"
                      />
                      <span className="ml-2 text-slate-300 group-hover:text-white transition-colors">Remember me</span>
                    </label>
                    <Link 
                      to="/forgot-password" 
                      className="text-cyan-400 hover:text-cyan-300 font-medium transition-colors hover:underline"
                    >
                      Forgot password?
                    </Link>
                  </motion.div>

                  <motion.button
                    type="submit"
                    disabled={isLoading || submitting}
                    className="relative w-full group overflow-hidden"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.8 }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 via-blue-500 to-purple-600 rounded-lg sm:rounded-xl transition-all duration-300" />
                    <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-500 rounded-lg sm:rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                    <div className="absolute inset-0 bg-gradient-to-r from-cyan-600 via-blue-600 to-purple-700 rounded-lg sm:rounded-xl blur-xl opacity-50 group-hover:opacity-75 transition-opacity" />
                    <span className="relative block py-2.5 sm:py-3 font-semibold text-white text-sm sm:text-base">
                      {isLoading || submitting ? (
                        <span className="flex items-center justify-center">
                          <svg className="animate-spin -ml-1 mr-2 sm:mr-3 h-4 w-4 sm:h-5 sm:w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          {loadingMessage}
                        </span>
                      ) : (
                        'Log In'
                      )}
                    </span>
                  </motion.button>
                </form>

              {/* Divider - Only show if OAuth is enabled */}
              {isAnyOAuthEnabled && (
                <motion.div 
                  className="relative my-4 sm:my-5 lg:my-6"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.9 }}
                >
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-white/20"></div>
                  </div>
                  <div className="relative flex justify-center text-xs sm:text-sm">
                    <span className="px-3 sm:px-4 backdrop-blur-xl bg-white/5 text-slate-300 rounded-full">or log in with</span>
                  </div>
                </motion.div>
              )}

              {/* OAuth Buttons - Modern Glass Design */}
              <motion.div 
                className="space-y-2.5 sm:space-y-3"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1.0 }}
              >
                {/* Google Sign-In - Only show if properly configured */}
                {isGoogleOAuthEnabled && (
                  <GoogleOAuthProvider clientId={googleClientId}>
                    <div className="w-full">
                      <GoogleLogin
                        onSuccess={handleGoogleSuccess}
                        onError={handleGoogleError}
                        useOneTap
                        theme="outline"
                        size="large"
                        text="signin_with"
                        shape="rectangular"
                        width="100%"
                      />
                    </div>
                  </GoogleOAuthProvider>
                )}

                {/* Apple Sign-In - Only show if properly configured */}
                {isAppleOAuthEnabled && (
                  <AppleSignin
                    uiType="dark"
                    authOptions={{
                      clientId: appleClientId,
                      scope: 'email name',
                      redirectURI: window.location.origin + '/auth/apple/callback',
                      usePopup: true,
                    }}
                    onSuccess={handleAppleSuccess}
                    onError={handleAppleError}
                    render={(props: ButtonHTMLAttributes<HTMLButtonElement>) => (
                      <button
                        {...props}
                        type="button"
                        className="w-full flex items-center justify-center space-x-2 py-2.5 sm:py-3 px-3 sm:px-4 backdrop-blur-xl bg-white/10 border border-white/20 rounded-lg sm:rounded-xl hover:bg-white/15 transition-all group transform hover:scale-[1.02] active:scale-[0.98]"
                      >
                        <svg className="w-4 h-4 sm:w-5 sm:h-5 text-white" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M17.05 20.28c-.98.95-2.05.88-3.08.4-1.09-.5-2.08-.48-3.24 0-1.44.62-2.2.44-3.06-.4C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/>
                        </svg>
                        <span className="font-medium text-white text-sm sm:text-base">Sign in with Apple</span>
                      </button>
                    )}
                  />
                )}

                <motion.div 
                  className="text-center pt-1 sm:pt-2"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 1.1 }}
                >
                  <span className="text-xs sm:text-sm text-slate-300">Don't have an account? </span>
                  <Link 
                    to="/register" 
                    className="text-xs sm:text-sm text-cyan-400 hover:text-cyan-300 font-semibold transition-colors hover:underline"
                  >
                    Create Account
                  </Link>
                </motion.div>
              </motion.div>

              {/* Footer - Glassmorphism Style */}
              <motion.div 
                className="mt-4 sm:mt-6 lg:mt-8 pt-4 sm:pt-5 lg:pt-6 border-t border-white/10 text-center text-[10px] sm:text-xs text-slate-400"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1.2 }}
              >
                <p>By continuing, you agree to HireMeBahamas'</p>
                <p className="mt-1">
                  <Link to="/terms" className="hover:text-cyan-400 transition-colors">Terms of Service</Link>
                  {' · '}
                  <Link to="/privacy" className="hover:text-cyan-400 transition-colors">Privacy Policy</Link>
                </p>
              </motion.div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default Login;
