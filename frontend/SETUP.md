# HireMeBahamas Frontend - Automated Setup Guide

This guide explains how to use the automated setup and fix tools for the HireMeBahamas frontend.

## Quick Start

The easiest way to set up and fix the frontend is to use the automated setup script:

```bash
# Using npm script (recommended)
npm run setup

# Or directly with Node.js
node setup-and-fix.js

# Or using the shell script (Linux/Mac)
./setup-and-fix.sh
```

This single command will:
- ✅ Check system requirements
- ✅ Install all dependencies
- ✅ Generate missing PWA assets
- ✅ Fix vite-plugin-pwa build errors
- ✅ Verify the build works correctly

## Problem Being Solved

The vite-plugin-pwa was failing during build with the error:
```
error during [vite-plugin-pwa:build] [plugin vite-plugin-pwa:build] index.html: 
There was an error during the build
```

**Root Cause:** Missing PWA icon assets that were referenced in:
- `vite.config.ts` (PWA manifest configuration)
- `index.html` (icon and splash screen references)

## What Gets Installed

### Dependencies
All packages from `package.json`:
- **Production dependencies:** React, routing, UI libraries, etc.
- **Dev dependencies:** TypeScript, Vite, testing tools, etc.
- **Build tools:** vite-plugin-pwa and related packages

### Generated Assets

The script generates all required PWA assets with HireMeBahamas branding:

**Icons:**
- `pwa-192x192.png` - PWA manifest icon (192×192)
- `pwa-512x512.png` - PWA manifest icon (512×512)
- `apple-touch-icon.png` - iOS home screen icon (180×180)
- `favicon-32x32.png` - Browser favicon
- `favicon-16x16.png` - Browser favicon
- `favicon.ico` - Legacy favicon
- `vite.svg` - Vite logo

**iOS Splash Screens:**
- iPhone 5/SE (640×1136)
- iPhone 6/7/8 (750×1334)
- iPhone 6+/7+/8+ (1242×2208)
- iPhone X/XS/11 Pro (1125×2436)
- iPhone XR/11 (828×1792)
- iPhone XS Max/11 Pro Max (1242×2688)
- iPad (1536×2048)
- iPad Pro 10.5" (1668×2224)
- iPad Pro 11" (1668×2388)
- iPad Pro 12.9" (2048×2732)

All assets feature a blue gradient background with the HireMeBahamas branding.

## Manual Setup (Alternative)

If you prefer to run steps manually:

### 1. Install Dependencies
```bash
npm install
```

### 2. Install Asset Generation Tool
```bash
npm install --save-dev sharp
```

### 3. Generate PWA Assets
```bash
npm run generate-assets
# or
node scripts/generate-pwa-assets.js
```

### 4. Build and Verify
```bash
npm run build
```

## Available Scripts

### `npm run setup`
Complete automated setup and fix (recommended for first-time setup)

### `npm run generate-assets`
Regenerate PWA assets only (useful if you want to update icons)

### `npm run build`
Build the production-ready frontend

### `npm run dev`
Start the development server

### `npm run preview`
Preview the production build locally

### `npm run lint`
Check code for linting errors

### `npm run lint:fix`
Automatically fix linting errors

## Troubleshooting

### "sharp is not installed"
Run: `npm install --save-dev sharp`

### "PWA assets not found"
Run: `npm run generate-assets`

### "Build still failing"
1. Delete `node_modules` and `package-lock.json`
2. Run: `npm run setup`

### "Permission denied" (Linux/Mac)
Make the shell script executable:
```bash
chmod +x setup-and-fix.sh
```

## System Requirements

- **Node.js:** 18.0.0 or higher
- **npm:** 8.0.0 or higher
- **OS:** Windows, macOS, or Linux

## File Structure

```
frontend/
├── setup-and-fix.js          # Automated setup script (cross-platform)
├── setup-and-fix.sh          # Automated setup script (Bash)
├── scripts/
│   ├── generate-pwa-assets.js # PWA asset generator
│   └── README.md             # Scripts documentation
├── public/
│   ├── *.png                 # Generated icons
│   ├── *.ico                 # Generated favicon
│   ├── *.svg                 # Logos
│   └── splash-screens/       # iOS splash screens
├── package.json              # Dependencies and scripts
└── vite.config.ts           # Vite and PWA configuration
```

## CI/CD Integration

The setup can be automated in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Setup and build frontend
  run: |
    cd frontend
    npm run setup
```

## Customizing Assets

To customize the PWA assets (colors, branding):

1. Edit `frontend/scripts/generate-pwa-assets.js`
2. Update the constants:
   - `BRAND_COLOR_START` - Gradient start color
   - `BRAND_COLOR_END` - Gradient end color
   - `BRAND_NAME` - Full brand name
   - `BRAND_SHORT` - Short brand name for icons
3. Regenerate assets: `npm run generate-assets`

## Support

For issues or questions:
1. Check this documentation
2. Review the error messages from the automated script
3. Check the build logs for specific errors
4. Ensure all system requirements are met

## What's Next?

After successful setup:
1. Start development: `npm run dev`
2. Make your changes
3. Test the build: `npm run build`
4. Deploy to production

---

**Last Updated:** November 2024  
**Script Version:** 1.0.0
