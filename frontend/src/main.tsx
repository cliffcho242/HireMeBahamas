import { StrictMode } from 'react'
import ReactDOM from 'react-dom/client'
import * as Sentry from '@sentry/react'
import App from './App'
import './index.css'
import './styles/mobile-responsive.css'

// 🚫 HARD BLOCK: Prevent loading if served from deprecated Railway domains
if (typeof window !== 'undefined' && window.location.hostname.includes('railway')) {
  document.body.innerHTML = '❌ Deprecated backend detected';
  throw new Error('Railway backend blocked');
}

// 🔒 FOREVER FIX: Validate environment variables at startup
// This catches configuration errors early before they cause runtime issues
import './config/envValidator'

// Performance monitoring: Track Core Web Vitals
import { reportWebVitals } from './utils/webVitals'

// Initialize Sentry for production error monitoring with Web Vitals tracking
Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.MODE,
  
  // Performance monitoring - trace sample rate
  tracesSampleRate: parseFloat(import.meta.env.VITE_SENTRY_TRACES_SAMPLE_RATE || '0.2'),
  
  // Enable profiling for performance insights
  profilesSampleRate: parseFloat(import.meta.env.VITE_SENTRY_PROFILES_SAMPLE_RATE || '0.1'),
  
  // Web Vitals tracking - automatically capture Core Web Vitals
  integrations: [
    Sentry.browserTracingIntegration({
      // Track navigation timing and long tasks
      enableLongTask: true,
      enableInp: true,
    }),
    // Capture user interactions and session replays for debugging
    Sentry.replayIntegration({
      maskAllText: true,
      blockAllMedia: true,
    }),
  ],
  
  // Session replay sample rates
  replaysSessionSampleRate: 0.1,  // 10% of normal sessions
  replaysOnErrorSampleRate: 1.0,  // 100% of sessions with errors
  
  // Only enable if DSN is configured
  enabled: !!import.meta.env.VITE_SENTRY_DSN,
  
  // Send performance data
  beforeSend(event) {
    // Don't send events in development
    if (import.meta.env.DEV) {
      return null;
    }
    return event;
  },
})

// 🧹 RAILWAY PURGE: Clear caches ONCE to remove old Railway URLs
// This migration runs only once per browser to avoid impacting performance
// v2: Force all users to clear caches again to ensure Railway URLs are completely removed
const MIGRATION_KEY = 'hiremebahamas_railway_migration_v2';

if (typeof window !== 'undefined') {
  const migrationDone = localStorage.getItem(MIGRATION_KEY);
  
  if (!migrationDone) {
    console.log('🧹 Running Railway to Render migration (one-time cleanup)...');
    
    // Clear service workers that might cache old Railway API URLs
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.getRegistrations().then(regs => {
        regs.forEach(reg => {
          reg.unregister();
          console.log('🧹 Unregistered service worker:', reg.scope);
        });
      }).catch(err => {
        console.error('Failed to unregister service workers:', err);
      });
    }
    
    // Selectively clear Railway-related storage keys
    try {
      // Remove API URL caches that might contain Railway URLs
      const keysToRemove = ['api_cache', 'backend_url', 'cached_api_url'];
      keysToRemove.forEach(key => {
        localStorage.removeItem(key);
        sessionStorage.removeItem(key);
      });
      console.log('🧹 Cleared Railway-related cache keys');
    } catch (err) {
      console.error('Failed to clear storage:', err);
    }
    
    // Clear IndexedDB caches if present (compatible with all browsers)
    if ('indexedDB' in window) {
      try {
        // Modern browsers with databases() method
        if (typeof indexedDB.databases === 'function') {
          indexedDB.databases().then(dbs => {
            dbs.forEach(db => {
              if (db.name && db.name.includes('cache')) {
                indexedDB.deleteDatabase(db.name);
                console.log('🧹 Deleted IndexedDB cache:', db.name);
              }
            });
          });
        }
      } catch (err) {
        console.error('Failed to clear IndexedDB:', err);
      }
    }
    
    // Mark migration as complete
    try {
      localStorage.setItem(MIGRATION_KEY, 'true');
      console.log('✅ Railway migration complete');
    } catch (err) {
      console.error('Failed to mark migration as complete:', err);
    }
  }
}

// 🔍 BACKEND CONNECTION VERIFICATION
// Verify on startup that we're connecting to the correct Render backend
if (typeof window !== 'undefined') {
  window.addEventListener('load', () => {
    // Import the API utility to get the backend URL
    import('./lib/api').then(({ getApiBase }) => {
      const backendUrl = getApiBase();
      
      // Log the backend URL for debugging
      console.log('🔗 Backend URL:', backendUrl);
      
      // Verify it's the Render backend
      if (backendUrl === 'https://hiremebahamas.onrender.com') {
        console.log('✅ Connected to Render backend (correct)');
      } else if (backendUrl.includes('localhost') || backendUrl.includes('127.0.0.1')) {
        console.log('🔧 Using local development backend');
      } else {
        console.warn('⚠️ Unexpected backend URL:', backendUrl);
      }
      
      // Test backend connectivity with a lightweight health check
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
      
      fetch(`${backendUrl}/health/ping`, {
        method: 'GET',
        signal: controller.signal,
      })
        .then(response => {
          if (!response.ok) {
            throw new Error(`Backend returned ${response.status}`);
          }
          console.log('✅ Backend connectivity verified');
        })
        .catch(error => {
          console.error('❌ Backend connection failed:', error.message);
          console.error('   This may indicate the backend is starting up or unreachable');
          console.error('   Backend URL:', backendUrl);
        })
        .finally(() => {
          clearTimeout(timeoutId);
        });
    }).catch(err => {
      console.error('Failed to load API utility:', err);
    });
  });
}

// Register Service Worker for PWA (fresh registration after cleanup)
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/service-worker.js')
      .then((registration) => {
        console.log('Service Worker registered successfully:', registration.scope);
        
        // Check for updates every hour
        setInterval(() => {
          registration.update();
        }, 60 * 60 * 1000);
      })
      .catch((error) => {
        console.log('Service Worker registration failed:', error);
      });
  });
}

// Enhanced error fallback component with recovery options
const ErrorFallback = () => (
  <div style={{ 
    display: 'flex', 
    flexDirection: 'column', 
    alignItems: 'center', 
    justifyContent: 'center', 
    minHeight: '100vh', 
    padding: '20px',
    textAlign: 'center',
    fontFamily: 'system-ui, -apple-system, sans-serif'
  }}>
    <h1 style={{ fontSize: '24px', marginBottom: '16px', color: '#dc2626' }}>
      Oops! Something went wrong
    </h1>
    <p style={{ marginBottom: '24px', color: '#6b7280', maxWidth: '500px' }}>
      We're sorry for the inconvenience. The error has been reported to our team.
    </p>
    <button 
      onClick={() => window.location.reload()} 
      style={{ 
        padding: '12px 24px', 
        backgroundColor: '#3b82f6', 
        color: 'white', 
        border: 'none', 
        borderRadius: '6px', 
        cursor: 'pointer',
        fontSize: '16px'
      }}
    >
      Reload Page
    </button>
  </div>
);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Sentry.ErrorBoundary fallback={<ErrorFallback />}>
      <App />
    </Sentry.ErrorBoundary>
  </StrictMode>,
)

// Start tracking Web Vitals after the app is mounted
reportWebVitals()
