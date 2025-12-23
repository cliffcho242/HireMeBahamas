import { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './contexts/AuthContext';
import { SocketProvider } from './contexts/SocketContext';

// Import ErrorBoundary for error safety
import ErrorBoundary from './components/ErrorBoundary';

// Critical components - import directly to avoid blank screens
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ProtectedRoute from './components/ProtectedRoute';

// Lazy load pages for better performance
const Home = lazy(() => import('./pages/Home'));
const Login = lazy(() => import('./pages/Login'));
const Register = lazy(() => import('./pages/Register'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Jobs = lazy(() => import('./pages/Jobs'));
const JobDetail = lazy(() => import('./pages/JobDetail'));
const Profile = lazy(() => import('./pages/Profile'));
const UserProfile = lazy(() => import('./pages/UserProfile'));
const Messages = lazy(() => import('./pages/Messages'));
const PostJob = lazy(() => import('./pages/PostJob'));
const NotFound = lazy(() => import('./pages/NotFound'));

// Cache duration constants
const CACHE_STALE_TIME = 5 * 60 * 1000; // 5 minutes
const CACHE_GC_TIME = 10 * 60 * 1000; // 10 minutes

// Loading fallback component for Suspense
// Uses inline styles to ensure it works even if CSS fails to load
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-[200px] p-5">
    <div className="text-center">
      <div className="w-10 h-10 border-3 border-gray-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4" />
      <p className="text-gray-500">Loading…</p>
    </div>
  </div>
);

// Create a client with optimized settings
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: CACHE_STALE_TIME,
      gcTime: CACHE_GC_TIME,
    },
  },
});

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <Suspense fallback={<PageLoader />}>
            <QueryClientProvider client={queryClient}>
              <SocketProvider>
                <div className="min-h-screen bg-gray-50 flex flex-col">
                  <Navbar />
                  
                  <main className="flex-grow">
                    <Suspense fallback={<PageLoader />}>
                      <Routes>
                        {/* Public Routes */}
                        <Route path="/" element={<Home />} />
                        <Route path="/login" element={<Login />} />
                        <Route path="/register" element={<Register />} />
                        <Route path="/jobs" element={<Jobs />} />
                        <Route path="/jobs/:id" element={<JobDetail />} />
                        <Route path="/users/:userId" element={<UserProfile />} />

                        {/* Protected Routes */}
                        <Route 
                          path="/dashboard" 
                          element={
                            <ProtectedRoute>
                              <Dashboard />
                            </ProtectedRoute>
                          } 
                        />
                        <Route 
                          path="/profile" 
                          element={
                            <ProtectedRoute>
                              <Profile />
                            </ProtectedRoute>
                          } 
                        />
                        <Route 
                          path="/messages" 
                          element={
                            <ProtectedRoute>
                              <Messages />
                            </ProtectedRoute>
                          } 
                        />
                        <Route 
                          path="/post-job" 
                          element={
                            <ProtectedRoute>
                              <PostJob />
                            </ProtectedRoute>
                          } 
                        />

                        {/* 404 Not Found - Catch-all route */}
                        <Route path="*" element={<NotFound />} />
                      </Routes>
                    </Suspense>
                  </main>

                  <Footer />
                  <Toaster 
                    position="top-right"
                    toastOptions={{
                      duration: 4000,
                      style: {
                        background: '#363636',
                        color: '#fff',
                      },
                    }}
                  />
                </div>
              </SocketProvider>
            </QueryClientProvider>
          </Suspense>
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;