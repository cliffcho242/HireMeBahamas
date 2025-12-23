import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// PWA configuration imported from centralized config
import { pwaConfig } from './src/config/pwa.config';

// Default API base URL for development when not specified
const DEFAULT_API_BASE_URL = 'https://api.hiremebahamas.com';

export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  const env = loadEnv(mode, process.cwd(), '');
  
  // Build-time validation: Warn if VITE_API_BASE_URL is missing but don't fail
  if (mode === 'production') {
    const apiBaseUrl = env.VITE_API_BASE_URL;
    
    if (!apiBaseUrl) {
      console.warn(
        '\n⚠️  WARNING: VITE_API_BASE_URL is not set\n\n' +
        'The application will use fallback URL: https://hiremebahamas-backend.onrender.com\n' +
        'For best results, set VITE_API_BASE_URL in your deployment environment.\n\n' +
        'To configure:\n' +
        '1. Set VITE_API_BASE_URL in your Vercel dashboard:\n' +
        '   Settings → Environment Variables → Production\n' +
        '2. Example value: https://api.hiremebahamas.com\n' +
        '3. Alternative: https://hiremebahamas-backend.onrender.com\n\n' +
        'See .env.example for more details.\n'
      );
    } else {
      // Validate URL format
      if (!apiBaseUrl.startsWith('https://')) {
        console.warn(
          '\n⚠️  WARNING: VITE_API_BASE_URL should use HTTPS in production\n\n' +
          `Current value: ${apiBaseUrl}\n\n` +
          'Production builds should use secure HTTPS URLs.\n' +
          'Consider updating VITE_API_BASE_URL to start with https://\n'
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
      // PWA configuration from centralized config (src/config/pwa.config.ts)
      // ✅ No offline hijack
      // ✅ No broken routing
      // ✅ Safe mobile refreshes
      pwaConfig,
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
