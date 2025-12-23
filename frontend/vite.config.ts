import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';
import path from 'path';

// Default API base URL for development when not specified
const DEFAULT_API_BASE_URL = 'https://api.hiremebahamas.com';

export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  const env = loadEnv(mode, process.cwd(), '');
  
  // Build-time validation: Fail fast if VITE_API_BASE_URL is missing in production
  if (mode === 'production') {
    const apiBaseUrl = env.VITE_API_BASE_URL;
    
    if (!apiBaseUrl) {
      throw new Error(
        '\n❌ CRITICAL BUILD ERROR: VITE_API_BASE_URL is not set\n\n' +
        'The application requires VITE_API_BASE_URL for production builds.\n' +
        'This prevents blank screens and silent failures.\n\n' +
        'To fix:\n' +
        '1. Set VITE_API_BASE_URL in your Vercel dashboard:\n' +
        '   Settings → Environment Variables → Production\n' +
        '2. Example value: https://api.hiremebahamas.com\n' +
        '3. Alternative: https://hiremebahamas-backend.onrender.com\n\n' +
        'See .env.example for more details.\n'
      );
    }
    
    // Validate URL format
    if (!apiBaseUrl.startsWith('https://')) {
      throw new Error(
        '\n❌ CRITICAL BUILD ERROR: VITE_API_BASE_URL must use HTTPS in production\n\n' +
        `Current value: ${apiBaseUrl}\n\n` +
        'Production builds require secure HTTPS URLs.\n' +
        'Update VITE_API_BASE_URL to start with https://\n'
      );
    }
    
    // Warn about trailing slash
    if (apiBaseUrl.endsWith('/')) {
      console.warn(
        '\n⚠️  WARNING: VITE_API_BASE_URL has trailing slash\n' +
        `Current value: ${apiBaseUrl}\n` +
        'This may cause API routing issues. Remove the trailing slash.\n'
      );
    }
    
    console.log('✅ Build validation passed: VITE_API_BASE_URL is set correctly');
    console.log(`   API Base URL: ${apiBaseUrl}`);
  }
  
  return {
    // Explicit base required for Vercel static asset resolution
    base: '/',
    build: {
      outDir: 'dist',
      assetsDir: 'assets',
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    plugins: [
      react(),
      // PWA configuration for production + mobile safety
      // ✅ No offline hijack
      // ✅ No broken routing
      // ✅ Safe mobile refreshes
      VitePWA({
        registerType: 'autoUpdate',
        injectRegister: 'inline',
        workbox: {
          cleanupOutdatedCaches: true,
          // Don't cache API routes - let them go to the real backend
          navigateFallbackDenylist: [/^\/api\//],
        },
      }),
    ],
    // Dev server configuration with API proxy
    server: {
      port: 3000,
      proxy: {
        // Proxy /api requests to backend to avoid CORS during local development
        '/api': {
          target: env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL,
          changeOrigin: true,
          secure: true,
          // Uncomment for debugging proxy issues:
          // configure: (proxy, _options) => {
          //   proxy.on('error', (err, _req, _res) => {
          //     console.log('proxy error', err);
          //   });
          //   proxy.on('proxyReq', (proxyReq, req, _res) => {
          //     console.log('Sending Request:', req.method, req.url, '→', proxyReq.path);
          //   });
          //   proxy.on('proxyRes', (proxyRes, req, _res) => {
          //     console.log('Received Response:', proxyRes.statusCode, req.url);
          //   });
          // },
        },
      },
    },
  };
});
