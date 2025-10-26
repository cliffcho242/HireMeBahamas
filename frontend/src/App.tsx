import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { SocketProvider } from './contexts/SocketContext';
import { AIMonitoringProvider } from './contexts/AIMonitoringContext';

// Pages
import Home from './pages/Home';
import LandingPage from './pages/LandingPage';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Jobs from './pages/Jobs';
import JobDetail from './pages/JobDetail';
import Profile from './pages/Profile';
import Messages from './pages/Messages';
import PostJob from './pages/PostJob';
import HireMe from './pages/HireMe';
import Friends from './pages/Friends';
import UserProfile from './pages/UserProfile';
import Download from './pages/Download';

// Components
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ProtectedRoute from './components/ProtectedRoute';
import AuthGuard from './components/AuthGuard';
import { AIErrorBoundary } from './components/AIErrorBoundary';
import InstallPWA from './components/InstallPWA';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <AIMonitoringProvider>
      <AIErrorBoundary>
        <QueryClientProvider client={queryClient}>
          <Router>
            <AuthProvider>
              <SocketProvider>
                <AppContent />
              </SocketProvider>
            </AuthProvider>
          </Router>
        </QueryClientProvider>
      </AIErrorBoundary>
    </AIMonitoringProvider>
  );
}

function AppContent() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen min-h-[100dvh] bg-gray-50 flex flex-col overflow-x-hidden">
      {/* Only show navbar and footer for authenticated users */}
      {isAuthenticated && <Navbar />}

      <main className="flex-grow w-full">
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

          {/* Catch all route - redirect to login if not authenticated */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
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