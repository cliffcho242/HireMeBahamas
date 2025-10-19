import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Eye, EyeOff, Mail, Lock, User, MapPin, Phone } from 'lucide-react';

const FacebookLikeAuth = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    location: '',
    phone: '',
    user_type: 'freelancer' as 'freelancer' | 'client' | 'employer' | 'recruiter'
  });

  const { login, register, isLoading } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (isLogin) {
        await login(formData.email, formData.password);
        console.log('Login successful, navigating to dashboard...');
        navigate('/dashboard');
      } else {
        await register(formData);
        console.log('Registration successful, navigating to dashboard...');
        navigate('/dashboard');
      }
    } catch (error) {
      console.error('Auth error:', error);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleDemoLogin = async () => {
    try {
      console.log('Starting demo login...');
      await login('admin@hiremebahamas.com', 'admin123');
      console.log('Demo login successful, navigating to dashboard...');
      navigate('/dashboard');
    } catch (error) {
      console.error('Demo login error:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-cyan-400 via-teal-300 to-blue-500 relative overflow-hidden">
      {/* Caribbean Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-10 left-10 w-32 h-32 bg-yellow-300 rounded-full opacity-20 animate-pulse"></div>
        <div className="absolute top-1/3 right-20 w-24 h-24 bg-pink-300 rounded-full opacity-30 animate-bounce" style={{animationDelay: '2s'}}></div>
        <div className="absolute bottom-20 left-1/4 w-40 h-40 bg-orange-300 rounded-full opacity-15 animate-pulse" style={{animationDelay: '4s'}}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-white rounded-full opacity-5"></div>
        
        {/* Palm leaves pattern */}
        <div className="absolute top-0 right-0 w-64 h-64 opacity-10">
          <svg viewBox="0 0 200 200" className="w-full h-full text-green-600">
            <path d="M100,100 C120,80 140,60 160,40 C140,60 120,80 100,100 C80,80 60,60 40,40 C60,60 80,80 100,100" fill="currentColor"/>
            <path d="M100,100 C120,120 140,140 160,160 C140,140 120,120 100,100 C80,120 60,140 40,160 C60,140 80,120 100,100" fill="currentColor"/>
          </svg>
        </div>
        
        {/* Wave pattern at bottom */}
        <div className="absolute bottom-0 left-0 w-full h-32 opacity-30">
          <svg viewBox="0 0 1200 120" className="w-full h-full text-blue-600">
            <path d="M0,96L48,112C96,128 192,160 288,160C384,160 480,128 576,122.7C672,117 768,139 864,138.7C960,139 1056,117 1152,112L1200,107L1200,120L1152,120C1056,120 960,120 864,120C768,120 672,120 576,120C480,120 384,120 288,120C192,120 96,120 48,120L0,120Z" fill="currentColor"/>
          </svg>
        </div>
      </div>

      {/* Header */}
      <div className="relative z-10 bg-white/90 backdrop-blur-sm shadow-lg border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-cyan-500 to-teal-600 rounded-lg flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-xl">H</span>
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-600 to-teal-700 bg-clip-text text-transparent">
                HireMeBahamas
              </h1>
            </div>
            <div className="text-sm text-white/90 bg-gradient-to-r from-cyan-500/20 to-teal-500/20 px-4 py-2 rounded-full backdrop-blur-sm border border-white/20">
              🌴 Find Your Perfect Job in Paradise
            </div>
          </div>
        </div>
      </div>

      <div className="flex min-h-screen">
        {/* Left Side - Caribbean Paradise Hero */}
        <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-cyan-500 via-teal-500 to-blue-600 text-white relative overflow-hidden">
          {/* Caribbean Background Elements */}
          <div className="absolute inset-0">
            <div className="absolute top-20 left-20 w-20 h-20 bg-yellow-300 rounded-full opacity-30 animate-pulse"></div>
            <div className="absolute bottom-32 right-16 w-16 h-16 bg-pink-300 rounded-full opacity-25 animate-bounce" style={{animationDelay: '3s'}}></div>
            <div className="absolute top-1/2 right-10 w-32 h-32 bg-orange-300 rounded-full opacity-20 animate-pulse" style={{animationDelay: '1s'}}></div>
            
            {/* Palm tree silhouettes */}
            <div className="absolute bottom-0 left-10 opacity-20">
              <svg width="80" height="120" viewBox="0 0 80 120" className="text-green-400">
                <path d="M40,120 L40,60 M20,70 Q40,60 40,60 Q60,70 60,70 M15,75 Q40,65 40,65 Q65,75 65,75 M25,80 Q40,70 40,70 Q55,80 55,80" stroke="currentColor" strokeWidth="3" fill="none"/>
              </svg>
            </div>
            <div className="absolute bottom-0 right-20 opacity-15">
              <svg width="60" height="100" viewBox="0 0 60 100" className="text-green-400">
                <path d="M30,100 L30,50 M10,58 Q30,50 30,50 Q50,58 50,58 M8,63 Q30,55 30,55 Q52,63 52,63" stroke="currentColor" strokeWidth="2" fill="none"/>
              </svg>
            </div>
          </div>

          <div className="relative z-10 flex flex-col justify-center px-12 py-16">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <div className="mb-6">
                <span className="inline-block px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full text-sm font-medium border border-white/20 mb-4">
                  🏝️ #1 Caribbean Job Platform
                </span>
              </div>
              
              <h2 className="text-5xl font-bold mb-6 leading-tight">
                Your Career
                <span className="block text-yellow-300"> in Paradise</span>
                <span className="block text-cyan-200">Awaits</span>
              </h2>
              
              <p className="text-xl text-white/90 mb-8 leading-relaxed">
                Discover amazing opportunities across the beautiful Bahamas. From luxury resorts to financial services, 
                find your perfect role in the Caribbean's premier destination.
              </p>
              
              {/* Caribbean Features Grid */}
              <div className="grid grid-cols-2 gap-4 mb-8">
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20 hover:bg-white/15 transition-all">
                  <div className="text-3xl mb-2">🏖️</div>
                  <h4 className="font-semibold mb-1">Beach Offices</h4>
                  <p className="text-sm text-white/80">Work steps from pristine beaches</p>
                </div>
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20 hover:bg-white/15 transition-all">
                  <div className="text-3xl mb-2">🌺</div>
                  <h4 className="font-semibold mb-1">Island Culture</h4>
                  <p className="text-sm text-white/80">Embrace Caribbean lifestyle</p>
                </div>
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20 hover:bg-white/15 transition-all">
                  <div className="text-3xl mb-2">💰</div>
                  <h4 className="font-semibold mb-1">Tax Advantages</h4>
                  <p className="text-sm text-white/80">Favorable tax environment</p>
                </div>
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20 hover:bg-white/15 transition-all">
                  <div className="text-3xl mb-2">☀️</div>
                  <h4 className="font-semibold mb-1">Perfect Weather</h4>
                  <p className="text-sm text-white/80">Sunshine year-round</p>
                </div>
              </div>
              
              {/* Success Stats */}
              <div className="grid grid-cols-3 gap-6 text-center">
                <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4 border border-white/10">
                  <div className="text-3xl font-bold text-yellow-300">500+</div>
                  <div className="text-sm text-white/80">Active Jobs</div>
                </div>
                <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4 border border-white/10">
                  <div className="text-3xl font-bold text-cyan-300">200+</div>
                  <div className="text-sm text-white/80">Companies</div>
                </div>
                <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4 border border-white/10">
                  <div className="text-3xl font-bold text-pink-300">95%</div>
                  <div className="text-sm text-white/80">Success Rate</div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>

        {/* Right Side - Auth Form with Caribbean Styling */}
        <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-white/90 backdrop-blur-sm relative">
          {/* Tropical accent elements */}
          <div className="absolute top-10 right-10 w-16 h-16 bg-gradient-to-br from-yellow-300 to-orange-400 rounded-full opacity-20 animate-pulse"></div>
          <div className="absolute bottom-20 left-10 w-12 h-12 bg-gradient-to-br from-pink-300 to-red-400 rounded-full opacity-25 animate-bounce" style={{animationDelay: '2s'}}></div>
          
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="max-w-md w-full space-y-8 relative z-10"
          >
            <div className="bg-white rounded-3xl shadow-2xl p-8 border border-cyan-100/50 backdrop-blur-sm">
              <div className="text-center mb-8">
                <div className="w-20 h-20 bg-gradient-to-r from-cyan-500 to-teal-600 rounded-full flex items-center justify-center mx-auto mb-4 shadow-xl">
                  <span className="text-white font-bold text-3xl">H</span>
                </div>
                <h3 className="text-3xl font-bold bg-gradient-to-r from-cyan-600 to-teal-700 bg-clip-text text-transparent mb-2">
                  {isLogin ? 'Welcome Back!' : 'Join Paradise'}
                </h3>
                <p className="text-gray-600">
                  {isLogin 
                    ? '🌴 Sign in to your Caribbean career dashboard' 
                    : '🏝️ Create your account and start your island journey'
                  }
                </p>
              </div>

              {/* Auth Toggle with Caribbean Colors */}
              <div className="flex bg-gradient-to-r from-cyan-50 to-teal-50 rounded-xl p-1 mb-6 border border-cyan-100">
                <button
                  onClick={() => setIsLogin(true)}
                  className={`flex-1 py-3 px-4 rounded-lg text-sm font-medium transition-all ${
                    isLogin
                      ? 'bg-gradient-to-r from-cyan-500 to-teal-600 text-white shadow-lg transform scale-105'
                      : 'text-gray-600 hover:text-cyan-700'
                  }`}
                >
                  🏖️ Sign In
                </button>
                <button
                  onClick={() => setIsLogin(false)}
                  className={`flex-1 py-3 px-4 rounded-lg text-sm font-medium transition-all ${
                    !isLogin
                      ? 'bg-gradient-to-r from-cyan-500 to-teal-600 text-white shadow-lg transform scale-105'
                      : 'text-gray-600 hover:text-cyan-700'
                  }`}
                >
                  🌺 Sign Up
                </button>
              </div>              {/* Caribbean-styled Auth Form */}
              <form onSubmit={handleSubmit} className="space-y-6">
              {!isLogin && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  transition={{ duration: 0.3 }}
                  className="grid grid-cols-2 gap-4"
                >
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                    <input
                      type="text"
                      name="first_name"
                      placeholder="First Name"
                      value={formData.first_name}
                      onChange={handleInputChange}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                      required={!isLogin}
                    />
                  </div>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                    <input
                      type="text"
                      name="last_name"
                      placeholder="Last Name"
                      value={formData.last_name}
                      onChange={handleInputChange}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                      required={!isLogin}
                    />
                  </div>
                </motion.div>
              )}

              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                <input
                  type="email"
                  name="email"
                  placeholder="Email Address"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  required
                />
              </div>

              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  placeholder="Password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>

              {!isLogin && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  transition={{ duration: 0.3, delay: 0.1 }}
                  className="space-y-4"
                >
                  <div className="relative">
                    <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                    <input
                      type="text"
                      name="location"
                      placeholder="Location (e.g., Nassau, Freeport)"
                      value={formData.location}
                      onChange={handleInputChange}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                      required={!isLogin}
                    />
                  </div>

                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                    <input
                      type="tel"
                      name="phone"
                      placeholder="Phone Number"
                      value={formData.phone}
                      onChange={handleInputChange}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      I'm looking to:
                    </label>
                    <div className="grid grid-cols-2 gap-4">
                      <label className="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="radio"
                          name="user_type"
                          value="freelancer"
                          checked={formData.user_type === 'freelancer'}
                          onChange={handleInputChange}
                          className="text-blue-600 focus:ring-blue-500"
                        />
                        <span className="text-sm text-gray-700">Find Work</span>
                      </label>
                      <label className="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="radio"
                          name="user_type"
                          value="client"
                          checked={formData.user_type === 'client'}
                          onChange={handleInputChange}
                          className="text-blue-600 focus:ring-blue-500"
                        />
                        <span className="text-sm text-gray-700">Hire Talent</span>
                      </label>
                    </div>
                  </div>
                </motion.div>
              )}

              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-gradient-to-r from-cyan-500 to-teal-600 text-white py-3 px-4 rounded-xl font-medium hover:from-cyan-600 hover:to-teal-700 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-[1.02] shadow-lg"
              >
                {isLoading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>{isLogin ? '🌊 Signing In...' : '🏝️ Creating Account...'}</span>
                  </div>
                ) : (
                  isLogin ? '🏖️ Sign In to Paradise' : '🌺 Create Paradise Account'
                )}
              </button>

              {isLogin && (
                <div className="text-center">
                  <a href="#" className="text-sm text-cyan-600 hover:text-cyan-700 transition-colors font-medium">
                    🔐 Forgot your password?
                  </a>
                </div>
              )}
            </form>

            {/* Quick Demo Login - Caribbean Style */}
            <div className="mt-8 p-6 bg-gradient-to-r from-cyan-50 to-teal-50 rounded-2xl border-2 border-cyan-100/50 backdrop-blur-sm">
              <div className="text-center mb-4">
                <div className="text-2xl mb-2">🏝️</div>
                <p className="text-sm text-cyan-700 font-medium mb-2">Quick Paradise Demo</p>
                <p className="text-xs text-cyan-600">Experience the Caribbean job platform instantly</p>
              </div>
              <button
                onClick={handleDemoLogin}
                className="w-full bg-gradient-to-r from-yellow-400 to-orange-500 text-white py-3 px-4 rounded-xl text-sm font-medium hover:from-yellow-500 hover:to-orange-600 transition-all transform hover:scale-[1.02] shadow-lg border-2 border-orange-200"
              >
                🌺 Login with Demo Account
              </button>
            </div>
          </div>
        </motion.div>
        </div>
      </div>
    </div>
  );
};

export default FacebookLikeAuth;