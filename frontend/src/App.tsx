import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { ErrorBoundary } from 'react-error-boundary';
import { AuthProvider } from './contexts/AuthContext';
import { SocketProvider } from './contexts/SocketContext';
import { Suspense, lazy } from 'react';

// Import critical components directly (not lazy) to avoid blank screens
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ProtectedRoute from './components/ProtectedRoute';
import ErrorFallback from './components/ErrorFallback';

// Lazy load pages for better performance (they'll show loading state)
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

// Loading fallback component
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-screen bg-gray-50">
    <div className="text-center">
      <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
      <p className="text-gray-600 text-lg">Loading...</p>
    </div>
  </div>
);

// Create a React Query client with optimized settings
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime in v4)
    },
  },
});

function App() {
  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      onReset={() => window.location.reload()}
      onError={(error, errorInfo) => {
        // Log error to console for debugging
        console.error('Application Error:', error);
        console.error('Error Info:', errorInfo);
        
        // TODO: Send to error tracking service (Sentry, etc.)
        // Sentry.captureException(error, { contexts: { react: errorInfo } });
      }}
    >
      <QueryClientProvider client={queryClient}>
        <Router>
          <AuthProvider>
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
                      <Route path="/users/:username" element={<UserProfile />} />

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

                      {/* 404 Not Found */}
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
                    success: {
                      duration: 3000,
                      iconTheme: {
                        primary: '#10b981',
                        secondary: '#fff',
                      },
                    },
                    error: {
                      duration: 5000,
                      iconTheme: {
                        primary: '#ef4444',
                        secondary: '#fff',
                      },
                    },
                  }}
                />
              </div>
            </SocketProvider>
          </AuthProvider>
        </Router>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
