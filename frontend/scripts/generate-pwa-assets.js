#!/usr/bin/env node

/**
 * PWA Asset Generator for HireMeBahamas
 * 
 * This script generates all required PWA assets (icons and splash screens)
 * for the HireMeBahamas frontend application.
 * 
 * Usage: node scripts/generate-pwa-assets.js
 * 
 * Requirements: npm install sharp (dev dependency)
 */

import sharp from 'sharp';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const publicDir = path.resolve(__dirname, '../public');

// Configuration
const BRAND_COLOR_START = '#2563eb'; // Blue
const BRAND_COLOR_END = '#1e40af';   // Darker Blue
const BRAND_NAME = 'HireMeBahamas';
const BRAND_SHORT = 'HMB';

/**
 * Create an icon buffer with gradient background and text
 */
async function createIconBuffer(width, height, text = BRAND_SHORT) {
  const fontSize = Math.min(width, height) * 0.3;
  const borderRadius = width * 0.1;
  
  const svg = `
    <svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:${BRAND_COLOR_START};stop-opacity:1" />
          <stop offset="100%" style="stop-color:${BRAND_COLOR_END};stop-opacity:1" />
        </linearGradient>
      </defs>
      <rect width="${width}" height="${height}" fill="url(#grad1)" rx="${borderRadius}"/>
      <text x="50%" y="50%" font-family="Arial, sans-serif" font-size="${fontSize}" font-weight="bold" fill="white" text-anchor="middle" dominant-baseline="middle">${text}</text>
    </svg>
  `;
  
  return Buffer.from(svg);
}

/**
 * Create a splash screen buffer with gradient background and brand name
 */
async function createSplashBuffer(width, height) {
  const fontSize = Math.min(width, height) * 0.06;
  
  const svg = `
    <svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="splash-grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:${BRAND_COLOR_START};stop-opacity:1" />
          <stop offset="100%" style="stop-color:${BRAND_COLOR_END};stop-opacity:1" />
        </linearGradient>
      </defs>
      <rect width="${width}" height="${height}" fill="url(#splash-grad)"/>
      <text x="50%" y="50%" font-family="Arial, sans-serif" font-size="${fontSize}" font-weight="bold" fill="white" text-anchor="middle" dominant-baseline="middle">${BRAND_NAME}</text>
    </svg>
  `;
  
  return Buffer.from(svg);
}

async function main() {
  console.log('🎨 PWA Asset Generator for HireMeBahamas\n');
  console.log('Generating PWA assets...\n');

  // Ensure public directory exists
  if (!fs.existsSync(publicDir)) {
    fs.mkdirSync(publicDir, { recursive: true });
  }

  // Generate icons
  const icons = [
    { name: 'pwa-192x192.png', size: 192, description: 'PWA Icon 192x192' },
    { name: 'pwa-512x512.png', size: 512, description: 'PWA Icon 512x512' },
    { name: 'apple-touch-icon.png', size: 180, description: 'Apple Touch Icon' },
    { name: 'favicon-32x32.png', size: 32, description: 'Favicon 32x32' },
    { name: 'favicon-16x16.png', size: 16, description: 'Favicon 16x16' },
  ];

  console.log('📱 Creating icons...');
  for (const icon of icons) {
    const buffer = await createIconBuffer(icon.size, icon.size);
    await sharp(buffer)
      .png()
      .toFile(path.join(publicDir, icon.name));
    console.log(`  ✓ ${icon.name} (${icon.description})`);
  }

  // Create favicon.ico (using 32x32 as base)
  const faviconBuffer = await createIconBuffer(32, 32);
  await sharp(faviconBuffer)
    .png()
    .toFile(path.join(publicDir, 'favicon.ico'));
  console.log('  ✓ favicon.ico (Website Favicon)');

  // Create vite.svg (keep the official Vite logo)
  const viteSvg = `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" aria-hidden="true" role="img" class="iconify iconify--logos" width="31.88" height="32" preserveAspectRatio="xMidYMid meet" viewBox="0 0 256 257"><defs><linearGradient id="IconifyId1813088fe1fbc01fb466" x1="-.828%" x2="57.636%" y1="7.652%" y2="78.411%"><stop offset="0%" stop-color="#41D1FF"></stop><stop offset="100%" stop-color="#BD34FE"></stop></linearGradient><linearGradient id="IconifyId1813088fe1fbc01fb467" x1="43.376%" x2="50.316%" y1="2.242%" y2="89.03%"><stop offset="0%" stop-color="#FFEA83"></stop><stop offset="8.333%" stop-color="#FFDD35"></stop><stop offset="100%" stop-color="#FFA800"></stop></linearGradient></defs><path fill="url(#IconifyId1813088fe1fbc01fb466)" d="M255.153 37.938L134.897 252.976c-2.483 4.44-8.862 4.466-11.382.048L.875 37.958c-2.746-4.814 1.371-10.646 6.827-9.67l120.385 21.517a6.537 6.537 0 0 0 2.322-.004l117.867-21.483c5.438-.991 9.574 4.796 6.877 9.62Z"></path><path fill="url(#IconifyId1813088fe1fbc01fb467)" d="M185.432.063L96.44 17.501a3.268 3.268 0 0 0-2.634 3.014l-5.474 92.456a3.268 3.268 0 0 0 3.997 3.378l24.777-5.718c2.318-.535 4.413 1.507 3.936 3.838l-7.361 36.047c-.495 2.426 1.782 4.5 4.151 3.78l15.304-4.649c2.372-.72 4.652 1.36 4.15 3.788l-11.698 56.621c-.732 3.542 3.979 5.473 5.943 2.437l1.313-2.028l72.516-144.72c1.215-2.423-.88-5.186-3.54-4.672l-25.505 4.922c-2.396.462-4.435-1.77-3.759-4.114l16.646-57.705c.677-2.35-1.37-4.583-3.769-4.113Z"></path></svg>`;
  fs.writeFileSync(path.join(publicDir, 'vite.svg'), viteSvg);
  console.log('  ✓ vite.svg (Vite Logo)');

  // Create splash screens directory
  const splashDir = path.join(publicDir, 'splash-screens');
  if (!fs.existsSync(splashDir)) {
    fs.mkdirSync(splashDir, { recursive: true });
  }

  // Generate splash screens for iOS devices
  const splashScreens = [
    { name: 'iphone5_splash.png', width: 640, height: 1136, device: 'iPhone 5/SE' },
    { name: 'iphone6_splash.png', width: 750, height: 1334, device: 'iPhone 6/7/8' },
    { name: 'iphoneplus_splash.png', width: 1242, height: 2208, device: 'iPhone 6+/7+/8+' },
    { name: 'iphonex_splash.png', width: 1125, height: 2436, device: 'iPhone X/XS/11 Pro' },
    { name: 'iphonexr_splash.png', width: 828, height: 1792, device: 'iPhone XR/11' },
    { name: 'iphonexsmax_splash.png', width: 1242, height: 2688, device: 'iPhone XS Max/11 Pro Max' },
    { name: 'ipad_splash.png', width: 1536, height: 2048, device: 'iPad' },
    { name: 'ipadpro1_splash.png', width: 1668, height: 2224, device: 'iPad Pro 10.5"' },
    { name: 'ipadpro3_splash.png', width: 1668, height: 2388, device: 'iPad Pro 11"' },
    { name: 'ipadpro2_splash.png', width: 2048, height: 2732, device: 'iPad Pro 12.9"' },
  ];

  console.log('\n🖼️  Creating splash screens...');
  for (const splash of splashScreens) {
    const buffer = await createSplashBuffer(splash.width, splash.height);
    await sharp(buffer)
      .png()
      .toFile(path.join(splashDir, splash.name));
    console.log(`  ✓ ${splash.name} (${splash.device})`);
  }

  console.log('\n✅ All PWA assets generated successfully!\n');
  console.log(`📊 Summary:`);
  console.log(`  - ${icons.length + 1} icons created`);
  console.log(`  - ${splashScreens.length} splash screens created`);
  console.log(`  - 1 Vite logo created`);
  console.log(`\n💡 Assets are ready for production use!`);
}

// Run the script
main().catch(err => {
  console.error('❌ Error generating assets:', err);
  process.exit(1);
});
