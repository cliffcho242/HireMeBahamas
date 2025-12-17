import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { Analytics } from '@vercel/analytics/react';
import { SpeedInsights } from '@vercel/speed-insights/react';
import { useMemo, Suspense, lazy } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { SocketProvider } from './contexts/SocketContext';
import { MessageNotificationProvider } from './contexts/MessageNotificationContext';
import { AIMonitoringProvider } from './contexts/AIMonitoringContext';
import { queryClient } from './config/reactQuery';

// Premium UI Components
import { AppLayout } from './components/premium';
import { PremiumSkeletonFeed } from './components/premium';

// Core pages - eagerly loaded for fast initial render
import LandingPage from './pages/LandingPage';
import Login from './pages/Login';
import Register from './pages/Register';
import Home from './pages/Home';

// Lazy-loaded pages for super-fast initial bundle
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Jobs = lazy(() => import('./pages/Jobs'));
const JobDetail = lazy(() => import('./pages/JobDetail'));
const Profile = lazy(() => import('./pages/Profile'));
const Messages = lazy(() => import('./pages/Messages'));
const PostJob = lazy(() => import('./pages/PostJob'));
const HireMe = lazy(() => import('./pages/HireMe'));
const Friends = lazy(() => import('./pages/Users'));
const UserProfile = lazy(() => import('./pages/UserProfile'));
const UserAnalytics = lazy(() => import('./pages/UserAnalytics'));
const Download = lazy(() => import('./pages/Download'));
const DownloadTest = lazy(() => import('./pages/DownloadTest'));
const NotFound = lazy(() => import('./pages/NotFound'));

// Components
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ProtectedRoute from './components/ProtectedRoute';
import AuthGuard from './components/AuthGuard';
import { AIErrorBoundary } from './components/AIErrorBoundary';
import { QueryErrorBoundary } from './components/QueryErrorBoundary';
import InstallPWA from './components/InstallPWA';
import ConnectionStatus from './components/ConnectionStatus';

// Sentry error monitoring
import { Sentry } from './config/sentry';

// Fast loading spinner component with accessibility - now premium
const LoadingSpinner = () => (
  <div 
    className="flex items-center justify-center min-h-[50vh]"
    role="status"
    aria-label="Loading"
    aria-live="polite"
  >
    <PremiumSkeletonFeed count={2} />
    <span className="sr-only">Loading page...</span>
  </div>
);

// Wrapper component to capture route for Speed Insights
function SpeedInsightsWrapper() {
  const location = useLocation();
  
  // Convert dynamic route paths to pattern format for proper aggregation
  const route = useMemo(() => {
    return location.pathname
      .replace(/\/jobs\/\d+/, '/jobs/[id]')
      .replace(/\/user\/\d+/, '/user/[userId]');
  }, [location.pathname]);

  return <SpeedInsights route={route} />;
}

function App() {
  return (
    <>
      {/* Sentry ErrorBoundary - Production error monitoring */}
      <Sentry.ErrorBoundary
        fallback={({ error, resetError }) => (
          <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
            <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6 text-center">
              <div className="text-red-500 text-5xl mb-4">⚠️</div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">Something went wrong</h1>
              <p className="text-gray-600 mb-4">
                We've been notified and are looking into it. Please try refreshing the page.
              </p>
              <div className="space-y-2">
                <button
                  onClick={resetError}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
                >
                  Try again
                </button>
                <button
                  onClick={() => window.location.href = '/'}
                  className="w-full bg-gray-200 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-300 transition-colors"
                >
                  Go to homepage
                </button>
              </div>
              {import.meta.env.DEV && (
                <details className="mt-4 text-left">
                  <summary className="cursor-pointer text-sm text-gray-500">Error details</summary>
                  <pre className="mt-2 text-xs bg-gray-100 p-2 rounded overflow-auto">
                    {error?.toString()}
                  </pre>
                </details>
              )}
            </div>
          </div>
        )}
        showDialog={false}
      >
        <AIMonitoringProvider>
          <AIErrorBoundary>
            {/* QueryErrorBoundary wraps QueryClientProvider for React Query v5 + Edge compatibility */}
            <QueryErrorBoundary>
              <QueryClientProvider client={queryClient}>
                <Router>
                  <AuthProvider>
                    <SocketProvider>
                      <MessageNotificationProvider>
                        <AppLayout 
                          enableCustomCursor={true}
                          enableSmoothScroll={true}
                          enablePageTransitions={true}
                          defaultTheme="system"
                        >
                          <AppContent />
                        </AppLayout>
                        <SpeedInsightsWrapper />
                      </MessageNotificationProvider>
                    </SocketProvider>
                  </AuthProvider>
                </Router>
              </QueryClientProvider>
            </QueryErrorBoundary>
          </AIErrorBoundary>
        </AIMonitoringProvider>
      </Sentry.ErrorBoundary>
      <Analytics />
    </>
  );
}

function AppContent() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="app-layout overflow-x-hidden">
      {/* Connection status banner - shows when backend is slow/unavailable */}
      <ConnectionStatus />

      {/* Only show navbar and footer for authenticated users */}
      {isAuthenticated && <Navbar />}

      <main className="main-content flex-grow">
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            {/* Public Routes - Only Login and Register (redirect authenticated users) */}
            <Route
              path="/login"
              element={
                <AuthGuard requireAuth={false}>
                  <Login />
                </AuthGuard>
              }
            />
            <Route
              path="/register"
              element={
                <AuthGuard requireAuth={false}>
                  <Register />
                </AuthGuard>
              }
            />

            {/* Root route - Landing page for unauthenticated, Home for authenticated */}
            <Route
              path="/"
              element={
                isAuthenticated ? (
                  <ProtectedRoute>
                    <Home />
                  </ProtectedRoute>
                ) : (
                  <LandingPage />
                )
              }
            />

            {/* Download Page - Public route for app installation */}
            <Route path="/download" element={<Download />} />
            <Route path="/download-test" element={<DownloadTest />} />

            {/* Protected Routes - Everything else requires authentication */}
            <Route
              path="/jobs"
              element={
                <ProtectedRoute>
                  <Jobs />
                </ProtectedRoute>
              }
          />
          <Route
            path="/jobs/:id"
            element={
              <ProtectedRoute>
                <JobDetail />
              </ProtectedRoute>
            }
          />
          <Route
            path="/hireme"
            element={
              <ProtectedRoute>
                <HireMe />
              </ProtectedRoute>
            }
          />
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
            path="/user/:userId"
            element={
              <ProtectedRoute>
                <UserProfile />
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
            path="/friends"
            element={
              <ProtectedRoute>
                <Friends />
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
          <Route
            path="/admin/analytics/users"
            element={
              <ProtectedRoute>
                <UserAnalytics />
              </ProtectedRoute>
            }
          />

          {/* Catch all route - show 404 page instead of redirecting */}
          <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
      </main>

      {/* Only show footer for authenticated users */}
      {isAuthenticated && <Footer />}

      {/* PWA Install Prompt */}
      <InstallPWA />

      {/* Global toast notifications */}
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
              primary: '#4aed88',
              secondary: '#fff',
            },
          },
          error: {
            duration: 5000,
            iconTheme: {
              primary: '#ff4b4b',
              secondary: '#fff',
            },
          },
        }}
      />
    </div>
  );
}

export default App;