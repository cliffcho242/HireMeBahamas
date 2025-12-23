import { StrictMode } from 'react'
import ReactDOM from 'react-dom/client'
import * as Sentry from '@sentry/react'
import { API_BASE_URL, apiUrl } from '@/lib/api'
import App from './App'
import './index.css'
import './styles/mobile-responsive.css'

console.log('APP VERSION:', import.meta.env.VITE_APP_VERSION);

// 🚀 Startup smoke test - if this log disappears, the app didn't boot
console.info('🚀 App booting', {
  apiBase: import.meta.env.VITE_API_BASE_URL,
  mode: import.meta.env.MODE,
  timestamp: new Date().toISOString(),
});

// 🚫 HARD BLOCK: Prevent loading if served from deprecated Railway domains
if (typeof window !== 'undefined' && window.location.hostname.includes('railway')) {
  const message = '❌ Deprecated backend detected';
  const root = document.getElementById('root');
  if (root) {
    root.textContent = message;
  } else if (document.body) {
    document.body.textContent = message;
  }
  throw new Error('Railway backend blocked');
}

// 🔒 FOREVER FIX: Validate environment variables at startup
// This catches configuration errors early before they cause runtime issues
import './config/envValidator'

// Runtime guard: Display user-friendly error if API URL is missing
if (typeof window !== 'undefined') {
  try {
    const apiBase = import.meta.env.VITE_API_BASE_URL;
    if (!apiBase && import.meta.env.PROD) {
      // Show user-friendly error message instead of blank screen
      const errorMessage = 
        '⚙️ Configuration Error\n\n' +
        'The application is not properly configured. Please contact the site administrator.\n\n' +
        'Error details: API base URL is missing from environment configuration.';
      
      const root = document.getElementById('root');
      if (root) {
        root.innerHTML = `
          <div style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 20px;
            text-align: center;
            font-family: system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
          ">
            <div style="
              background: rgba(255, 255, 255, 0.1);
              backdrop-filter: blur(10px);
              border-radius: 16px;
              padding: 40px;
              max-width: 500px;
              box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            ">
              <h1 style="font-size: 48px; margin: 0 0 20px 0;">⚙️</h1>
              <h2 style="font-size: 24px; margin: 0 0 16px 0;">Configuration Error</h2>
              <p style="margin: 0 0 24px 0; line-height: 1.6;">
                The application is not properly configured. Please contact the site administrator.
              </p>
              <button 
                onclick="window.location.reload()" 
                style="
                  padding: 12px 32px;
                  background: white;
                  color: #667eea;
                  border: none;
                  border-radius: 8px;
                  cursor: pointer;
                  font-size: 16px;
                  font-weight: 600;
                  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                  transition: transform 0.2s;
                "
                onmouseover="this.style.transform='scale(1.05)'"
                onmouseout="this.style.transform='scale(1)'"
              >
                Reload Page
              </button>
              <p style="
                margin: 24px 0 0 0;
                font-size: 12px;
                opacity: 0.8;
              ">
                Error: API base URL is missing from environment configuration
              </p>
            </div>
          </div>
        `;
      }
      throw new Error(errorMessage);
    }
  } catch (configError) {
    if (import.meta.env.PROD) {
      console.error('Configuration error:', configError);
      // Error display is already handled above
    }
  }
}

// Performance monitoring: Track Core Web Vitals
import { reportWebVitals } from './utils/webVitals'

// Global error handler: Catch all unhandled errors
import { initGlobalErrorHandler } from './utils/globalErrorHandler'

// Initialize global error handler before anything else
initGlobalErrorHandler();

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
    const backendUrl = API_BASE_URL;

    console.log('🔗 Backend URL:', backendUrl);

    if (!backendUrl) {
      console.warn('API base missing, skipping startup health check');
      return;
    }

    if (backendUrl === 'https://hiremebahamas-backend.onrender.com') {
      console.log('✅ Connected to Render backend (correct)');
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    fetch(apiUrl('/health/ping'), {
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
  });
}

// PWA temporarily disabled to avoid offline cache mismatches during deployment

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

// 🧱 LAYER 2: React Boot Safety - Boot failure must show visible error
const rootElement = document.getElementById('root');

if (!rootElement) {
  document.body.innerHTML = "<h1>Root missing</h1>";
} else {
  try {
    ReactDOM.createRoot(rootElement).render(
      <StrictMode>
        <Sentry.ErrorBoundary fallback={<ErrorFallback />}>
          <App />
        </Sentry.ErrorBoundary>
      </StrictMode>,
    );
  } catch (e) {
    console.error("BOOT FAILURE", e);
    rootElement.innerHTML = `
      <div style="padding:32px">
        <h2>App failed to start</h2>
        <pre>${String(e)}</pre>
        <button onclick="location.reload()">Reload</button>
      </div>
    `;
  }
}

// Start tracking Web Vitals after the app is mounted
reportWebVitals()
