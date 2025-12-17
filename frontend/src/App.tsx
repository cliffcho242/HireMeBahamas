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
import QueryErrorBoundary from './components/QueryErrorBoundary';
import InstallPWA from './components/InstallPWA';
import ConnectionStatus from './components/ConnectionStatus';

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
      <AIMonitoringProvider>
        <AIErrorBoundary>
          {/* QueryErrorBoundary wraps QueryClientProvider for React Query v5 + Edge compatibility */}
          <QueryErrorBoundary
            onReset={() => {
              // Reset query cache on error boundary reset
              queryClient.clear();
            }}
          >
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