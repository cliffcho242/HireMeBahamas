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
  
  // Safe API base URL with fallback - NEVER throws
  const apiBase =
    env.VITE_API_BASE_URL ||
    "https://hiremebahamas-backend.onrender.com";

  // Build-time validation: Warn if VITE_API_BASE_URL is missing
  // Never fail the build - runtime will use fallback
  if (!env.VITE_API_BASE_URL) {
    console.warn(
      "⚠️ VITE_API_BASE_URL not set at build time. Using fallback:",
      apiBase
    );
  } else {
    // Validate URL format (non-blocking warnings only)
    if (!apiBase.startsWith('https://')) {
      console.warn(
        '\n⚠️  WARNING: VITE_API_BASE_URL should use HTTPS in production\n\n' +
        `Current value: ${apiBase}\n\n` +
        'Production builds should use secure HTTPS URLs.\n'
      );
    }
    
    // Warn about trailing slash
    if (apiBase.endsWith('/')) {
      console.warn(
        '\n⚠️  WARNING: VITE_API_BASE_URL has trailing slash\n' +
        `Current value: ${apiBase}\n` +
        'This may cause API routing issues. Remove the trailing slash.\n'
      );
    } else {
      console.log('✅ Build validation passed: VITE_API_BASE_URL is set correctly');
      console.log(`   API Base URL: ${apiBase}`);
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
    define: {
      // Inject API base URL as a global constant at build time
      // This ensures runtime code always has a fallback value
      __API_BASE__: JSON.stringify(apiBase),
    },
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
