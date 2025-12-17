import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from './config/reactQuery'
import { ErrorBoundary } from './components/ErrorBoundary'
import App from './App'
import './index.css'
import './styles/mobile-responsive.css'

// Register Service Worker for PWA
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

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    </ErrorBoundary>
  </React.StrictMode>,
)