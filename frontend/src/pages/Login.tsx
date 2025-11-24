import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import AppleSignin from 'react-apple-signin-auth';
import { getOAuthConfig } from '../utils/oauthConfig';
import {
  UserIcon,
  BriefcaseIcon,
  ChatBubbleLeftRightIcon,
  HeartIcon,
  PhotoIcon,
  VideoCameraIcon
} from '@heroicons/react/24/outline';

const Login: React.FC = () => {
  const { login, loginWithGoogle, loginWithApple, isLoading, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('admin@hiremebahamas.com');
  const [password, setPassword] = useState('AdminPass123!');

  // Check OAuth configuration using utility function
  const oauthConfig = getOAuthConfig();
  const isGoogleOAuthEnabled = oauthConfig.google.enabled;
  const isAppleOAuthEnabled = oauthConfig.apple.enabled;
  const isAnyOAuthEnabled = oauthConfig.isAnyEnabled;
  const googleClientId = oauthConfig.google.clientId || '';
  const appleClientId = oauthConfig.apple.clientId || '';

  // Redirect authenticated users to home
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      toast.success('Welcome back to HireMeBahamas!');
      navigate('/');
    } catch (error: any) {
      toast.error(error.message || 'Login failed');
    }
  };

  const handleGoogleSuccess = async (credentialResponse: any) => {
    try {
      if (credentialResponse.credential) {
        await loginWithGoogle(credentialResponse.credential);
        navigate('/');
      }
    } catch (error: any) {
      console.error('Google login error:', error);
      const errorMessage = error?.response?.data?.detail || error?.message || 'Google sign-in failed';
      toast.error(errorMessage);
    }
  };

  const handleGoogleError = () => {
    toast.error('Google sign-in failed. Please try again.');
  };

  const handleAppleSuccess = async (response: any) => {
    try {
      if (response.authorization?.id_token) {
        await loginWithApple(response.authorization.id_token);
        navigate('/');
      }
    } catch (error: any) {
      console.error('Apple login error:', error);
      const errorMessage = error?.response?.data?.detail || error?.message || 'Apple sign-in failed';
      toast.error(errorMessage);
    }
  };

  const handleAppleError = (error: any) => {
    console.error('Apple sign-in error:', error);
    toast.error('Apple sign-in failed. Please try again.');
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-2 gap-12 items-center min-h-[calc(100vh-4rem)]">
          {/* Left Side - Branding */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center lg:text-left"
          >
            {/* Logo */}
            <div className="flex items-center justify-center lg:justify-start mb-8">
              <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-2xl">HB</span>
              </div>
              <h1 className="text-5xl font-bold ml-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                HireMeBahamas
              </h1>
            </div>

            {/* Tagline */}
            <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-6 leading-tight">
              Connect. Share.<br />Grow Your Career.
            </h2>

            <p className="text-xl text-gray-600 mb-8 max-w-lg">
              Join the Bahamas' premier professional social network. Connect with employers, 
              showcase your talents, and discover amazing opportunities.
            </p>

            {/* Features Grid - Enhanced with Colors */}
            <div className="grid grid-cols-2 gap-4 max-w-lg mx-auto lg:mx-0">
              {features.map((feature, index) => (
                <motion.div
                  key={feature.text}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * index }}
                  whileHover={{ scale: 1.05, y: -5 }}
                  className={`flex items-center space-x-3 ${feature.bgColor} rounded-xl p-4 shadow-md border ${feature.borderColor} hover:shadow-lg transition-all duration-200 cursor-pointer`}
                >
                  <div className={`p-2 ${feature.bgColor} rounded-lg`}>
                    <feature.icon className={`w-6 h-6 ${feature.color}`} />
                  </div>
                  <span className="text-sm font-medium text-gray-700">{feature.text}</span>
                </motion.div>
              ))}
            </div>

            {/* Stats - Enhanced Design */}
            <div className="mt-12 grid grid-cols-3 gap-4 max-w-lg mx-auto lg:mx-0">
              <motion.div 
                className="text-center bg-white rounded-xl p-4 shadow-md border border-blue-100 hover:shadow-lg transition-shadow"
                whileHover={{ scale: 1.05 }}
              >
                <div className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-blue-700 bg-clip-text text-transparent">5K+</div>
                <div className="text-xs font-medium text-gray-600 mt-1">Professionals</div>
              </motion.div>
              <motion.div 
                className="text-center bg-white rounded-xl p-4 shadow-md border border-purple-100 hover:shadow-lg transition-shadow"
                whileHover={{ scale: 1.05 }}
              >
                <div className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-purple-700 bg-clip-text text-transparent">1K+</div>
                <div className="text-xs font-medium text-gray-600 mt-1">Job Posts</div>
              </motion.div>
              <motion.div 
                className="text-center bg-white rounded-xl p-4 shadow-md border border-green-100 hover:shadow-lg transition-shadow"
                whileHover={{ scale: 1.05 }}
              >
                <div className="text-4xl font-bold bg-gradient-to-r from-green-600 to-green-700 bg-clip-text text-transparent">500+</div>
                <div className="text-xs font-medium text-gray-600 mt-1">Companies</div>
              </motion.div>
            </div>
          </motion.div>

          {/* Right Side - Login Form */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="max-w-md mx-auto w-full"
          >
            <div className="bg-white rounded-3xl shadow-2xl p-8 border border-gray-100">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-900 mb-2">Welcome Back</h2>
                <p className="text-gray-600">Sign in to continue your journey</p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                    Email or Phone
                  </label>
                  <input
                    id="email"
                    type="text"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                    placeholder="Enter your email"
                    required
                  />
                </div>
                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                    Password
                  </label>
                  <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                    placeholder="Enter your password"
                    required
                  />
                </div>

                <div className="flex items-center justify-between text-sm">
                  <label className="flex items-center">
                    <input type="checkbox" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                    <span className="ml-2 text-gray-600">Remember me</span>
                  </label>
                  <Link to="/forgot-password" className="text-blue-600 hover:text-blue-700 font-medium">
                    Forgot password?
                  </Link>
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-3 rounded-xl font-semibold hover:from-blue-700 hover:to-blue-800 transition-all transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
                >
                  {isLoading ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Signing in...
                    </span>
                  ) : (
                    'Sign In'
                  )}
                </button>
              </form>

              {/* Divider - Only show if OAuth is enabled */}
              {isAnyOAuthEnabled && (
                <div className="relative my-6">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-300"></div>
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-4 bg-white text-gray-500">or continue with</span>
                  </div>
                </div>
              )}

              {/* OAuth Buttons */}
              <div className="space-y-3">
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
                    render={(props: any) => (
                      <button
                        {...props}
                        type="button"
                        className="w-full flex items-center justify-center space-x-2 py-3 px-4 border border-gray-300 rounded-xl hover:bg-gray-50 transition-all bg-white"
                      >
                        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M17.05 20.28c-.98.95-2.05.88-3.08.4-1.09-.5-2.08-.48-3.24 0-1.44.62-2.2.44-3.06-.4C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/>
                        </svg>
                        <span className="font-medium text-gray-700">Sign in with Apple</span>
                      </button>
                    )}
                  />
                )}

                {/* Test Account Button - Only visible in development */}
                {import.meta.env.DEV && (
                  <button
                    type="button"
                    onClick={() => {
                      setEmail('admin@hiremebahamas.com');
                      setPassword('admin123');
                      toast.success('Test credentials loaded!');
                    }}
                    className={`w-full flex items-center justify-center space-x-2 py-3 px-4 border border-gray-300 rounded-xl hover:bg-gray-50 transition-all ${!isAnyOAuthEnabled ? 'mt-6' : ''}`}
                  >
                    <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                    </svg>
                    <span className="font-medium text-gray-700">Use Test Account</span>
                  </button>
                )}

                <div className="text-center">
                  <span className="text-gray-600">Don't have an account? </span>
                  <Link to="/register" className="text-blue-600 hover:text-blue-700 font-semibold">
                    Sign Up
                  </Link>
                </div>
              </div>

              {/* Footer */}
              <div className="mt-8 pt-6 border-t border-gray-200 text-center text-xs text-gray-500">
                <p>By continuing, you agree to HireMeBahamas'</p>
                <p className="mt-1">
                  <Link to="/terms" className="hover:text-blue-600">Terms of Service</Link>
                  {' · '}
                  <Link to="/privacy" className="hover:text-blue-600">Privacy Policy</Link>
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default Login;
