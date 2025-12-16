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
- **API Client:** Axios with React Query
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
│   ├── hooks/          # Custom React hooks
│   ├── utils/          # Utility functions
│   └── main.tsx        # Application entry point
├── scripts/            # Build and setup scripts
├── vite.config.ts      # Vite configuration
├── tailwind.config.js  # Tailwind CSS configuration
└── tsconfig.json       # TypeScript configuration
```

## 🔧 Development

### Running the Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000` (local development only)

**Note:** HTTP is only used for local development. Production deployments use HTTPS.

### Building for Production

```bash
npm run build
```

Production files will be output to the `dist/` directory.

### Environment Variables

Create a `.env.local` file in the frontend directory:

```env
# For local development only
VITE_API_URL=http://localhost:8008

# For production, always use HTTPS
# VITE_API_URL=https://api.yourdomain.com

# Optional: Guard against undefined URLs (prevents silent failures)
# Set to 'true' to enforce VITE_API_URL is configured
VITE_REQUIRE_BACKEND_URL=true
```

**Guard Against Undefined URLs (Important):**

The `VITE_REQUIRE_BACKEND_URL` environment variable can be used to prevent silent failures when the backend URL is not configured:

- ✅ Set to `'true'` for development or when using an external backend (Railway, Render, etc.)
- ❌ Leave unset or `'false'` for Vercel serverless deployments (same-origin API)

When enabled, the application will throw an error at startup if `VITE_API_URL` is not set, preventing unexpected behavior from using wrong backend URLs.

## 🎨 PWA Features

The application is a Progressive Web App with:
- ✅ Offline support
- ✅ Install to home screen
- ✅ App-like experience
- ✅ Service worker caching
- ✅ iOS splash screens
- ✅ Cross-platform icons

## 🐛 Troubleshooting

### Build Errors

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

For more troubleshooting, see [SETUP.md](./SETUP.md)

## 📚 Documentation

- [Setup Guide](./SETUP.md) - Detailed setup and troubleshooting
- [Scripts Documentation](./scripts/README.md) - Information about utility scripts

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run linting: `npm run lint:fix`
4. Test the build: `npm run build`
5. Submit a pull request

## 📄 License

Copyright © 2024 HireMeBahamas. All rights reserved.

---

**Need Help?** Check the [SETUP.md](./SETUP.md) guide for detailed instructions.
