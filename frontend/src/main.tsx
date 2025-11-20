import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

// TypeScript type declarations for global window properties
declare global {
  interface Window {
    socket?: any;
    Sentry?: any;
  }
}

// ==========================================
// DEPENDENCY INITIALIZATION
// ==========================================

console.log('🚀 Initializing HireMeBahamas Frontend...')
console.log('✅ All critical dependencies loaded')

// ==========================================
// SENTRY INITIALIZATION (Optional)
// ==========================================

const SENTRY_DSN = import.meta.env.VITE_SENTRY_DSN

if (SENTRY_DSN) {
  try {
    // Dynamic import to avoid errors if Sentry is not installed
    import('@sentry/react').then((Sentry) => {
      Sentry.init({
        dsn: SENTRY_DSN,
        integrations: [
          Sentry.browserTracingIntegration(),
          Sentry.replayIntegration(),
        ],
        tracesSampleRate: 1.0,
        replaysSessionSampleRate: 0.1,
        replaysOnErrorSampleRate: 1.0,
      })
      
      console.log('✅ Sentry initialized')
      
      // Send startup event
      Sentry.captureMessage('Frontend application started', 'info')
    }).catch((error) => {
      console.warn('⚠️  Sentry SDK not available:', error)
    })
  } catch (error) {
    console.warn('⚠️  Could not initialize Sentry:', error)
  }
} else {
  console.log('ℹ️  Sentry DSN not configured (optional)')
}

// ==========================================
// SOCKET.IO INITIALIZATION (Optional)
// ==========================================

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000'

try {
  // Check if Socket.IO client is available
  import('socket.io-client').then((io) => {
    const socket = io.default(BACKEND_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5,
    })
    
    socket.on('connect', () => {
      console.log('✅ Socket.IO connected')
    })
    
    socket.on('disconnect', () => {
      console.log('⚠️  Socket.IO disconnected')
    })
    
    socket.on('connect_error', (error) => {
      console.warn('⚠️  Socket.IO connection error:', error.message)
    })
    
    // Store socket instance globally for access in components
    window.socket = socket
  }).catch((error) => {
    console.log('ℹ️  Socket.IO client not available (optional):', error.message)
  })
} catch (error) {
  console.log('ℹ️  Could not initialize Socket.IO:', error)
}

// ==========================================
// PWA SERVICE WORKER REGISTRATION
// ==========================================

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/service-worker.js')
      .then((registration) => {
        console.log('✅ Service Worker registered:', registration.scope)
        
        // Check for updates every hour
        setInterval(() => {
          registration.update()
        }, 60 * 60 * 1000)
      })
      .catch((error) => {
        console.log('⚠️  Service Worker registration failed:', error)
      })
  })
} else {
  console.log('ℹ️  Service Worker not supported in this browser')
}

// ==========================================
// ERROR BOUNDARY
// ==========================================

class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('❌ Application error:', error, errorInfo)
    
    // Send to Sentry if available
    if ((window as any).Sentry) {
      ;(window as any).Sentry.captureException(error)
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          padding: '20px',
          textAlign: 'center',
          fontFamily: 'system-ui, sans-serif'
        }}>
          <h1 style={{ fontSize: '2rem', marginBottom: '1rem', color: '#ef4444' }}>
            ❌ Something went wrong
          </h1>
          <p style={{ marginBottom: '1rem', color: '#666' }}>
            {this.state.error?.message || 'An unexpected error occurred'}
          </p>
          <button
            onClick={() => window.location.reload()}
            style={{
              padding: '10px 20px',
              fontSize: '1rem',
              backgroundColor: '#667eea',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer'
            }}
          >
            🔄 Reload Application
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

// ==========================================
// APPLICATION STARTUP
// ==========================================

console.log('✅ Frontend initialization complete')
console.log(`📡 Backend URL: ${BACKEND_URL}`)
console.log('🎨 Starting React application...')

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>,
)