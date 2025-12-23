# HireMeBahamas Frontend

The frontend application for HireMeBahamas - a Caribbean job platform connecting employers with talented Bahamian professionals.

## 🚀 Quick Start

```bash
# Automated setup (installs dependencies, generates assets, and verifies build)
npm run setup

# Start development server
npm run dev

# Build for production
npm run build
```

## 📋 Prerequisites

- Node.js 18.0.0 or higher
- npm 8.0.0 or higher

## 🔧 Required Environment Variables

### ⚠️ CRITICAL: API Base URL

The frontend **requires** `VITE_API_BASE_URL` to function. Without this variable, the app will show a blank screen or configuration error.

**For Production (Vercel):**
Set in Vercel Dashboard → Settings → Environment Variables → Production:
```bash
VITE_API_BASE_URL=https://api.hiremebahamas.com
```

Alternative production URL:
```bash
VITE_API_BASE_URL=https://hiremebahamas-backend.onrender.com
```

**For Local Development:**
Create a `.env.local` file in the frontend directory:
```bash
# Use the dev proxy (recommended) - no VITE_API_BASE_URL needed
# The Vite dev server will proxy /api requests to the backend

# OR override with local backend
VITE_API_URL=http://localhost:8000
```

**Validation:**
- Build-time: Vite will **fail the build** if `VITE_API_BASE_URL` is missing in production
- Runtime: App will display a user-friendly error message instead of a blank screen

### Environment Requirements
- Must be HTTPS in production (http:// only allowed for localhost)
- Must NOT include trailing slash
- Must be a valid URL format

See `.env.example` for more configuration options.

## 🛠️ Installation & Setup

### Option 1: Automated Setup (Recommended)

Run the automated setup script that handles everything:

```bash
npm run setup
```

This will:
- ✅ Install all dependencies
- ✅ Generate PWA assets (icons, splash screens)
- ✅ Verify the build works
- ✅ Fix vite-plugin-pwa errors

For detailed documentation, see [SETUP.md](./SETUP.md)

### Option 2: Manual Setup

```bash
# Install dependencies
npm install

# Generate PWA assets
npm run generate-assets

# Build the application
npm run build
```

## 🏃 Running Locally

### Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

**API Proxy:** The dev server automatically proxies `/api/*` requests to the backend (configured via `VITE_API_BASE_URL` or defaults to `https://api.hiremebahamas.com`). This prevents CORS issues during local development.

### Verifying Backend Connectivity

The app includes an automatic health check that runs on startup:

1. **Health Check Banner**: A banner appears if the backend is slow or unavailable
2. **Console Logs**: Check browser console for connection status
3. **Manual Test**: Visit `http://localhost:3000` and watch for:
   - ✅ "Connected to backend" message
   - ✅ No blank white screen
   - ✅ Connection status banner (if backend is waking up)

### Error Handling

The app includes multiple layers of protection against blank screens:

1. **Build-time Guard**: Vite build fails if `VITE_API_BASE_URL` is missing
2. **Runtime Guard**: Clear error message displayed if config is invalid
3. **Error Boundary**: Top-level error boundary catches render errors and shows fallback UI
4. **Health Check**: Monitors backend connectivity and shows status banner
5. **Graceful Degradation**: App renders even if API is down (shows appropriate messages)

### Testing the Error Boundary

To test the error boundary and recovery mechanisms:

1. Set invalid `VITE_API_BASE_URL` (if testing locally with `.env.local`)
2. Reload the app
3. You should see a configuration error screen (NOT a blank white screen)
4. Fix the configuration and reload

## 📜 Available Scripts

| Command | Description |
|---------|-------------|
| `npm run setup` | Complete automated setup and fix |
| `npm run dev` | Start development server (port 3000) |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |
| `npm run lint` | Check code for linting errors |
| `npm run lint:fix` | Auto-fix linting errors |
| `npm run generate-assets` | Regenerate PWA assets |

## 🏗️ Tech Stack

- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite 7
- **Styling:** Tailwind CSS 3
- **State Management:** Zustand
- **Routing:** React Router 7
- **API Client:** Axios with React Query + Custom Robust API Client
- **PWA:** vite-plugin-pwa with Workbox
- **Icons:** Heroicons, Lucide React
- **Animations:** Framer Motion
- **Forms:** React Hook Form with Zod validation

## 📁 Project Structure

```
frontend/
├── public/              # Static assets (icons, splash screens)
├── src/
│   ├── components/      # Reusable React components
│   ├── pages/          # Page components
│   ├── services/       # API services and utilities
│   ├── lib/            # Core libraries (API client, utilities)
│   │   ├── api.ts           # API URL configuration
│   │   └── apiClient.ts     # Robust API client with retries
│   ├── hooks/          # Custom React hooks
│   ├── utils/          # Utility functions
│   ├── config/         # Configuration files
│   │   └── envValidator.ts  # Environment variable validation
│   └── main.tsx        # Application entry point
├── scripts/            # Build and setup scripts
├── vite.config.ts      # Vite configuration (includes proxy)
├── tailwind.config.js  # Tailwind CSS configuration
└── tsconfig.json       # TypeScript configuration
```

## 🔧 Development

### Running the Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000` (local development only)

**API Proxy**: The dev server automatically proxies `/api/*` requests to prevent CORS issues.

**Note:** HTTP is only used for local development. Production deployments use HTTPS.

### Building for Production

```bash
npm run build
```

Production files will be output to the `dist/` directory.

### Environment Variables

Create a `.env.local` file in the frontend directory for local development:

```env
# Local development (optional - dev proxy will handle API routing)
# VITE_API_URL=http://localhost:8000

# For production, always use HTTPS
# Set this in Vercel Dashboard, not in .env files
# VITE_API_BASE_URL=https://api.hiremebahamas.com
```

**Important Notes:**
- `VITE_API_BASE_URL` is **required** in production (set in Vercel Dashboard)
- `VITE_API_URL` is optional for local development
- The dev server proxy handles API routing automatically
- Never commit `.env.local` to version control

## 🎨 PWA Features

The application is a Progressive Web App with:
- ✅ Offline support
- ✅ Install to home screen
- ✅ App-like experience
- ✅ Service worker caching
- ✅ iOS splash screens
- ✅ Cross-platform icons

## 🐛 Troubleshooting

### Blank White Screen

If you see a blank white screen:

1. **Check Browser Console**: Look for configuration errors
2. **Verify Environment Variables**: Ensure `VITE_API_BASE_URL` is set in production
3. **Check Network Tab**: Look for failed API requests
4. **Clear Cache**: Clear browser cache and reload
5. **Check Error Boundary**: The app should show an error message, not a blank screen

The app has multiple safeguards to prevent blank screens:
- Build-time validation fails the build if config is missing
- Runtime guard shows user-friendly error message
- Error boundary catches and displays render errors
- Health check banner shows connection status

### Build Errors

If you encounter build errors about `VITE_API_BASE_URL`:

```bash
# Check if the variable is set
echo $VITE_API_BASE_URL

# For local testing, you can skip the check (not recommended for production)
# Build will still work but may show runtime errors
```

In production (Vercel):
1. Go to Vercel Dashboard → Settings → Environment Variables
2. Add `VITE_API_BASE_URL` with value `https://api.hiremebahamas.com`
3. Redeploy the application

### vite-plugin-pwa Errors

If you encounter vite-plugin-pwa build errors:

```bash
npm run setup
```

This will regenerate all missing PWA assets and fix common issues.

### Dependencies Not Installing

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Assets Not Loading

Regenerate PWA assets:

```bash
npm run generate-assets
```

### API Connection Issues

The app includes automatic health checks and retry logic:

1. **Health Banner**: Shows when backend is slow/unavailable
2. **Automatic Retries**: GET requests retry automatically with exponential backoff
3. **Graceful Degradation**: App shows appropriate messages when API is down

To debug API issues:
- Check browser console for connection logs
- Verify `VITE_API_BASE_URL` is correct
- Test backend health endpoint directly: `https://api.hiremebahamas.com/health`

For more troubleshooting, see [SETUP.md](./SETUP.md)

## 📚 Documentation

- [Setup Guide](./SETUP.md) - Detailed setup and troubleshooting
- [Scripts Documentation](./scripts/README.md) - Information about utility scripts
- [Environment Variables](./.env.example) - All available configuration options

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run linting: `npm run lint:fix`
4. Test the build: `npm run build`
5. Submit a pull request

## 🔒 Security

- Never commit secrets or API keys to version control
- Always use HTTPS in production
- Environment variables with `VITE_` prefix are exposed to the client
- Never add backend secrets (DATABASE_URL, JWT_SECRET, etc.) with `VITE_` prefix

## 📄 License

Copyright © 2024 HireMeBahamas. All rights reserved.

---

**Need Help?** Check the [SETUP.md](./SETUP.md) guide for detailed instructions.
