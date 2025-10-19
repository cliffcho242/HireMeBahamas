import { VitePWA } from 'vite-plugin-pwa';

export const pwaConfig = VitePWA({
  registerType: 'autoUpdate',
  includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
  manifest: {
    name: 'HireBahamas - Caribbean Job Platform',
    short_name: 'HireBahamas',
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
        purpose: 'any maskable'
      },
      {
        src: '/pwa-512x512.png',
        sizes: '512x512',
        type: 'image/png',
        purpose: 'any maskable'
      }
    ],
    categories: ['business', 'social', 'productivity'],
    shortcuts: [
      {
        name: 'Find Jobs',
        short_name: 'Jobs',
        description: 'Browse available jobs',
        url: '/jobs',
        icons: [{ src: '/icons/jobs.png', sizes: '96x96' }]
      },
      {
        name: 'Messages',
        short_name: 'Messages',
        description: 'View your messages',
        url: '/messages',
        icons: [{ src: '/icons/messages.png', sizes: '96x96' }]
      }
    ]
  },
  workbox: {
    // Cache strategies for optimal performance
    runtimeCaching: [
      {
        urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
        handler: 'CacheFirst',
        options: {
          cacheName: 'google-fonts-cache',
          expiration: {
            maxEntries: 10,
            maxAgeSeconds: 60 * 60 * 24 * 365 // 1 year
          },
          cacheableResponse: {
            statuses: [0, 200]
          }
        }
      },
      {
        urlPattern: /^https:\/\/fonts\.gstatic\.com\/.*/i,
        handler: 'CacheFirst',
        options: {
          cacheName: 'gstatic-fonts-cache',
          expiration: {
            maxEntries: 10,
            maxAgeSeconds: 60 * 60 * 24 * 365
          },
          cacheableResponse: {
            statuses: [0, 200]
          }
        }
      },
      {
        urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp)$/,
        handler: 'CacheFirst',
        options: {
          cacheName: 'image-cache',
          expiration: {
            maxEntries: 50,
            maxAgeSeconds: 60 * 60 * 24 * 30 // 30 days
          }
        }
      },
      {
        urlPattern: /\/api\/.*/,
        handler: 'NetworkFirst',
        options: {
          cacheName: 'api-cache',
          expiration: {
            maxEntries: 50,
            maxAgeSeconds: 60 * 5 // 5 minutes
          },
          networkTimeoutSeconds: 10
        }
      }
    ]
  },
  devOptions: {
    enabled: true,
    type: 'module'
  }
});
