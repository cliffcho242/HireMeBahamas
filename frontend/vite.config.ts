import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';
import { VitePWA } from 'vite-plugin-pwa';
import compression from 'vite-plugin-compression';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    // Gzip compression for faster loading
    compression({
      algorithm: 'gzip',
      ext: '.gz',
      threshold: 1024,
    }),
    // Brotli compression for even faster loading
    compression({
      algorithm: 'brotliCompress',
      ext: '.br',
      threshold: 1024,
    }),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'sounds/notification.mp3'],
      // Inject register for prompt-based updates
      injectRegister: 'auto',
      // Enable development mode for testing
      devOptions: {
        enabled: false, // Set to true for PWA testing in dev
      },
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
        // iOS specific
        categories: ['business', 'social', 'productivity'],
        // Shortcuts for quick access (addictive feature!)
        shortcuts: [
          {
            name: 'Messages',
            short_name: 'Messages',
            description: 'Check your messages',
            url: '/messages',
            icons: [{ src: '/pwa-192x192.png', sizes: '192x192' }],
          },
          {
            name: 'Jobs',
            short_name: 'Jobs',
            description: 'Browse job listings',
            url: '/jobs',
            icons: [{ src: '/pwa-192x192.png', sizes: '192x192' }],
          },
          {
            name: 'Post',
            short_name: 'Post',
            description: 'Create a new post',
            url: '/create-post',
            icons: [{ src: '/pwa-192x192.png', sizes: '192x192' }],
          },
        ],
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
          {
            src: '/pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable',
          },
        ],
      },
      workbox: {
        // Increase the maximum file size to be precached (default is 2MB)
        maximumFileSizeToCacheInBytes: 3 * 1024 * 1024, // 3MB
        // Skip waiting for immediate activation
        skipWaiting: true,
        clientsClaim: true,
        // Precache navigation routes for instant loading
        navigateFallback: '/index.html',
        navigateFallbackDenylist: [/^\/api/],
        // Clean old caches
        cleanupOutdatedCaches: true,
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'google-fonts-cache',
              expiration: {
                maxEntries: 10,
                maxAgeSeconds: 60 * 60 * 24 * 365, // 1 year
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
                maxAgeSeconds: 60 * 60 * 24 * 365, // 1 year
              },
            },
          },
          {
            urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp|avif)$/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'image-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24 * 30, // 30 days
              },
            },
          },
          {
            // Cache audio files for notification sounds
            urlPattern: /\.(?:mp3|wav|ogg)$/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'audio-cache',
              expiration: {
                maxEntries: 20,
                maxAgeSeconds: 60 * 60 * 24 * 365, // 1 year
              },
            },
          },
          {
            // Cache JS/CSS chunks for offline access
            urlPattern: /\.(?:js|css)$/i,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'static-resources',
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 60 * 60 * 24 * 7, // 7 days
              },
            },
          },
          {
            // API with network-first for fresh data
            urlPattern: /\/api\/.*/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              networkTimeoutSeconds: 10,
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 60 * 60, // 1 hour
              },
              // Enable background sync for failed requests
              backgroundSync: {
                name: 'api-queue',
                options: {
                  // maxRetentionTime is specified in minutes for workbox
                  maxRetentionTime: 24 * 60, // 24 hours = 1440 minutes
                },
              },
            },
          },
          {
            // Posts API with shorter cache for freshness
            urlPattern: /\/api\/posts.*/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'posts-cache',
              networkTimeoutSeconds: 5,
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 5, // 5 minutes
              },
            },
          },
          {
            // Messages API - always fresh
            urlPattern: /\/api\/messages.*/,
            handler: 'NetworkOnly',
            options: {
              backgroundSync: {
                name: 'messages-queue',
                options: {
                  maxRetentionTime: 60, // 1 hour in minutes
                },
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
    // HTTP/2 is automatically enabled in Vite when using HTTPS
    // For development, enable HTTPS for HTTP/2 benefits:
    // https: true,
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
    // Enable module preload for HTTP/2 multiplexing benefits
    modulePreload: {
      polyfill: true, // Polyfill for older browsers
    },
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
    rollupOptions: {
      output: {
        // Generate chunk names with content hash for better caching
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]',
        // Optimized chunking for HTTP/2 parallel loading
        manualChunks: {
          // Core React libraries - loaded first for initial render
          vendor: ['react', 'react-dom', 'react-router-dom'],
          // UI animation and icons - separate chunk for HTTP/2 multiplexing
          ui: ['framer-motion', '@heroicons/react'],
          // Form handling libraries - loaded on demand
          forms: ['react-hook-form', '@hookform/resolvers', 'yup'],
          // Data fetching and state - critical for data loading
          query: ['@tanstack/react-query', 'axios'],
          // Utility libraries
          utils: ['date-fns', 'clsx', 'tailwind-merge'],
        },
      },
    },
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom'],
  },
  // Preview server settings for production-like testing
  preview: {
    port: 3000,
    host: true,
  },
});

