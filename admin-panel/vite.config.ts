import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3001,
    proxy: {
      '/admin': {
        // Proxy configuration for local development server only
        // In production, admin-panel uses VITE_API_URL environment variable (see src/lib/api.ts)
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    chunkSizeWarningLimit: 1000, // Increase chunk size warning limit to 1000 kB (default is 500 kB)
  },
})
