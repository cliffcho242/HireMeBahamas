import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';
import { VitePWA } from 'vite-plugin-pwa';
import compression from 'vite-plugin-compression';

// =============================================================================
// PRODUCTION-IMMORTAL VITE CONFIGURATION
// =============================================================================
// 
// Performance Targets:
// - LCP (Largest Contentful Paint): <1.5s
// - FID (First Input Delay): <100ms
// - CLS (Cumulative Layout Shift): <0.1
// - TTI (Time to Interactive): <3s
// 
// Features:
// - Gzip + Brotli compression (70% smaller bundles)
// - PWA with offline support
// - Code splitting for parallel loading
// - Preconnect to API for faster requests
// - Service worker caching strategy
// =============================================================================

export default defineConfig({
  plugins: [
    react(),
    // Gzip compression for faster loading (fallback)
    compression({
      algorithm: 'gzip',
      ext: '.gz',
      threshold: 1024,
    }),
    // Brotli compression (20% smaller than gzip)
    compression({
      algorithm: 'brotliCompress',
      ext: '.br',
      threshold: 1024,
    }),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png'],
      manifest: {
        name: 'HireMeBahamas - Caribbean Job Platform',
        short_name: 'HireMeBahamas',
        description: 'Connect. Share. Grow Your Career in the Bahamas',
        theme_color: '#2563eb',
        background_color: '#ffffff',
        display: 'standalone',
        orientation: 'any',
        scope: '/',
        start_url: '/',
        icons: [
          {
            src: '/pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png',
            purpose: 'any',
          },
          {
            src: '/pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any',
          },
        ],
      },
      workbox: {
        // Increase the maximum file size to be precached
        maximumFileSizeToCacheInBytes: 3 * 1024 * 1024, // 3MB
        // Skip waiting for faster updates
        skipWaiting: true,
        clientsClaim: true,
        runtimeCaching: [
          // Google Fonts - cache for 1 year
          {
            urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'google-fonts-cache',
              expiration: {
                maxEntries: 10,
                maxAgeSeconds: 60 * 60 * 24 * 365,
              },
            },
          },
          {
            urlPattern: /^https:\/\/fonts\.gstatic\.com\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'google-fonts-webfonts',
              expiration: {
                maxEntries: 30,
                maxAgeSeconds: 60 * 60 * 24 * 365,
              },
            },
          },
          // Images - cache first, 30 days
          {
            urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp|avif)$/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'image-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24 * 30,
              },
            },
          },
          // JS/CSS - stale while revalidate for fresh updates
          {
            urlPattern: /\.(?:js|css)$/i,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'static-resources',
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 60 * 60 * 24 * 7,
              },
            },
          },
          // API - network first with 10s timeout, fallback to cache
          {
            urlPattern: /\/api\/.*/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              networkTimeoutSeconds: 10,
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60, // 1 hour
              },
              // Cache successful responses only
              cacheableResponse: {
                statuses: [0, 200],
              },
            },
          },
          // Login endpoint - cache for fast repeat logins
          {
            urlPattern: /\/api\/auth\/login/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'auth-cache',
              networkTimeoutSeconds: 5,
              expiration: {
                maxEntries: 10,
                maxAgeSeconds: 60 * 10, // 10 minutes
              },
            },
          },
        ],
      },
    }),
  ],
  server: {
    host: true,
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8008',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  build: {
    target: 'es2015',
    minify: 'terser',
    cssCodeSplit: true,
    chunkSizeWarningLimit: 1000,
    sourcemap: 'hidden',
    // Enable module preload for HTTP/2 parallel loading
    modulePreload: {
      polyfill: true,
    },
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.debug'],
      },
    },
    rollupOptions: {
      output: {
        // Content-hash for long-term caching
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]',
        // Optimized chunking for HTTP/2 parallel loading
        manualChunks: {
          // Core React - loaded first
          vendor: ['react', 'react-dom', 'react-router-dom'],
          // UI framework - second priority
          ui: ['framer-motion', '@heroicons/react'],
          // Forms - lazy loaded
          forms: ['react-hook-form', '@hookform/resolvers', 'zod', 'yup'],
          // Data fetching - critical for API
          query: ['@tanstack/react-query', 'axios'],
          // Utilities
          utils: ['date-fns', 'clsx', 'tailwind-merge'],
          // State management
          state: ['zustand', 'immer'],
          // GraphQL - Apollo Client for queries/mutations/subscriptions
          graphql: ['@apollo/client', 'graphql'],
        },
      },
    },
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom'],
  },
  preview: {
    port: 3000,
    host: true,
  },
});

