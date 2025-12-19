import { StrictMode } from 'react'
import ReactDOM from 'react-dom/client'
import * as Sentry from '@sentry/react'
import App from './App'
import './index.css'
import './styles/mobile-responsive.css'

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

// 🧹 RAILWAY PURGE: Clear ALL caches to remove old Railway URLs
// This runs ONCE on app load to force users to forget Railway backend
if (typeof window !== 'undefined') {
  // Clear service workers that might cache old API URLs
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
  
  // Clear all storage to remove cached Railway URLs
  try {
    localStorage.clear();
    sessionStorage.clear();
    console.log('🧹 Cleared localStorage and sessionStorage');
  } catch (err) {
    console.error('Failed to clear storage:', err);
  }
  
  // Clear IndexedDB if present
  if ('indexedDB' in window) {
    try {
      indexedDB.databases?.().then(dbs => {
        dbs.forEach(db => {
          if (db.name) {
            indexedDB.deleteDatabase(db.name);
            console.log('🧹 Deleted IndexedDB:', db.name);
          }
        });
      });
    } catch (err) {
      console.error('Failed to clear IndexedDB:', err);
    }
  }
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