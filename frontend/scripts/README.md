# Frontend Scripts

This directory contains utility scripts for the HireMeBahamas frontend.

## generate-pwa-assets.js

Generates all required PWA (Progressive Web App) assets including:
- App icons in various sizes (16x16, 32x32, 192x192, 512x512, 180x180)
- Favicon files
- iOS splash screens for different device sizes
- Vite logo

### Prerequisites

The script requires the `sharp` package for image processing:

```bash
npm install sharp --save-dev
```

### Usage

```bash
node scripts/generate-pwa-assets.js
```

### What it generates

**Icons:**
- `pwa-192x192.png` - PWA manifest icon
- `pwa-512x512.png` - PWA manifest icon
- `apple-touch-icon.png` - iOS home screen icon
- `favicon-32x32.png` - Browser favicon
- `favicon-16x16.png` - Browser favicon
- `favicon.ico` - Legacy favicon
- `vite.svg` - Vite logo

**Splash Screens:**
- `splash-screens/iphone5_splash.png`
- `splash-screens/iphone6_splash.png`
- `splash-screens/iphoneplus_splash.png`
- `splash-screens/iphonex_splash.png`
- `splash-screens/iphonexr_splash.png`
- `splash-screens/iphonexsmax_splash.png`
- `splash-screens/ipad_splash.png`
- `splash-screens/ipadpro1_splash.png`
- `splash-screens/ipadpro3_splash.png`
- `splash-screens/ipadpro2_splash.png`

All assets are generated with the HireMeBahamas brand colors (blue gradient).

### Customization

Edit the configuration constants in the script to customize:
- `BRAND_COLOR_START` - Gradient start color
- `BRAND_COLOR_END` - Gradient end color
- `BRAND_NAME` - Full brand name for splash screens
- `BRAND_SHORT` - Short brand name for icons
