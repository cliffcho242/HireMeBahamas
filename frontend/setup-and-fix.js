#!/usr/bin/env node

/**
 * HireMeBahamas Frontend - Automated Setup and Fix Script
 * 
 * This script automates the complete setup and fixing of the frontend build,
 * including:
 * - Checking and installing all dependencies
 * - Generating missing PWA assets
 * - Fixing vite-plugin-pwa build errors
 * - Verifying the build works correctly
 * 
 * Usage: node setup-and-fix.js
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

// Print functions
const printHeader = (msg) => {
  console.log(`\n${colors.blue}${'='.repeat(50)}${colors.reset}`);
  console.log(`${colors.blue}${msg}${colors.reset}`);
  console.log(`${colors.blue}${'='.repeat(50)}${colors.reset}\n`);
};

const printSuccess = (msg) => {
  console.log(`${colors.green}✓ ${msg}${colors.reset}`);
};

const printError = (msg) => {
  console.log(`${colors.red}✗ ${msg}${colors.reset}`);
};

const printWarning = (msg) => {
  console.log(`${colors.yellow}⚠ ${msg}${colors.reset}`);
};

const printInfo = (msg) => {
  console.log(`${colors.cyan}ℹ ${msg}${colors.reset}`);
};

// Execute command with error handling
const execCommand = (command, options = {}) => {
  try {
    const output = execSync(command, {
      stdio: options.silent ? 'pipe' : 'inherit',
      encoding: 'utf-8',
      ...options
    });
    return { success: true, output };
  } catch (error) {
    return { success: false, error: error.message };
  }
};

// Check if file exists
const fileExists = (filePath) => {
  try {
    return fs.existsSync(filePath);
  } catch {
    return false;
  }
};

async function main() {
  printHeader('HireMeBahamas Frontend - Automated Setup & Fix');

  // Step 1: Check Node.js version
  printHeader('Step 1: Checking System Requirements');
  
  const nodeVersion = process.version.match(/v(\d+)/)[1];
  if (parseInt(nodeVersion) < 18) {
    printError(`Node.js version ${process.version} is too old. Please install Node.js 18+.`);
    process.exit(1);
  }
  
  printSuccess(`Node.js ${process.version} detected`);
  
  const npmVersionResult = execCommand('npm -v', { silent: true });
  if (npmVersionResult.success) {
    printSuccess(`npm ${npmVersionResult.output.trim()} detected`);
  }

  // Step 2: Install dependencies
  printHeader('Step 2: Installing Frontend Dependencies');
  
  printInfo('Checking for existing node_modules...');
  if (fileExists(path.join(__dirname, 'node_modules'))) {
    printInfo('node_modules found. Using existing installation.');
  } else {
    printInfo('Installing dependencies (this may take a few minutes)...');
  }
  
  const installResult = execCommand('npm install');
  if (!installResult.success) {
    printError('Failed to install dependencies');
    process.exit(1);
  }
  printSuccess('All frontend dependencies installed successfully');

  // Step 3: Install sharp for asset generation
  printHeader('Step 3: Installing Asset Generation Tool');
  
  const sharpCheckResult = execCommand('npm list sharp', { silent: true });
  if (sharpCheckResult.success && sharpCheckResult.output.includes('sharp@')) {
    printInfo('sharp already installed');
  } else {
    printInfo('Installing sharp for PWA asset generation...');
    const sharpInstallResult = execCommand('npm install --save-dev sharp');
    if (!sharpInstallResult.success) {
      printError('Failed to install sharp');
      process.exit(1);
    }
    printSuccess('sharp installed successfully');
  }

  // Step 4: Generate PWA assets
  printHeader('Step 4: Generating PWA Assets');
  
  const assetGeneratorPath = path.join(__dirname, 'scripts', 'generate-pwa-assets.js');
  if (!fileExists(assetGeneratorPath)) {
    printError('PWA asset generator script not found at scripts/generate-pwa-assets.js');
    process.exit(1);
  }
  
  printInfo('Running PWA asset generator...');
  const assetGenResult = execCommand(`node ${assetGeneratorPath}`);
  if (!assetGenResult.success) {
    printError('Failed to generate PWA assets');
    process.exit(1);
  }
  printSuccess('PWA assets generated successfully');

  // Step 5: Verify generated assets
  printHeader('Step 5: Verifying Generated Assets');
  
  const requiredAssets = [
    'public/pwa-192x192.png',
    'public/pwa-512x512.png',
    'public/apple-touch-icon.png',
    'public/favicon-16x16.png',
    'public/favicon-32x32.png',
    'public/favicon.ico',
    'public/vite.svg',
    'public/splash-screens/iphone5_splash.png',
    'public/splash-screens/iphone6_splash.png',
    'public/splash-screens/iphonex_splash.png',
  ];
  
  let missingAssets = 0;
  for (const asset of requiredAssets) {
    const assetPath = path.join(__dirname, asset);
    if (fileExists(assetPath)) {
      printSuccess(`Found: ${asset}`);
    } else {
      printError(`Missing: ${asset}`);
      missingAssets++;
    }
  }
  
  if (missingAssets > 0) {
    printError(`${missingAssets} required assets are missing`);
    process.exit(1);
  }

  // Step 6: Build the frontend
  printHeader('Step 6: Testing Frontend Build');
  
  printInfo('Running TypeScript compiler and Vite build...');
  const buildResult = execCommand('npm run build');
  if (!buildResult.success) {
    printError('Frontend build failed');
    process.exit(1);
  }
  printSuccess('Frontend build completed successfully!');

  // Step 7: Verify build output
  printHeader('Step 7: Verifying Build Output');
  
  const distDir = path.join(__dirname, 'dist');
  if (!fileExists(distDir)) {
    printError('Build output directory not found');
    process.exit(1);
  }
  
  printSuccess('Build output directory created');
  
  const criticalFiles = [
    'dist/index.html',
    'dist/sw.js',
    'dist/manifest.webmanifest',
  ];
  
  for (const file of criticalFiles) {
    const filePath = path.join(__dirname, file);
    if (fileExists(filePath)) {
      printSuccess(`${path.basename(file)} generated`);
    } else {
      printWarning(`${path.basename(file)} not found (may be optional)`);
    }
  }

  // Step 8: Summary
  printHeader('Setup Complete! 🎉');
  
  printSuccess('All dependencies installed');
  printSuccess('All PWA assets generated');
  printSuccess('Frontend build verified');
  printSuccess('Ready for deployment');
  
  console.log(`\n${colors.green}Next steps:${colors.reset}`);
  console.log('  1. Start development server: npm run dev');
  console.log('  2. Preview production build: npm run preview');
  console.log('  3. Deploy to production');
  
  console.log(`\n${colors.cyan}Generated assets location:${colors.reset}`);
  console.log('  - PWA icons: frontend/public/*.png');
  console.log('  - Splash screens: frontend/public/splash-screens/*.png');
  console.log('  - Build output: frontend/dist/');
  
  printSuccess('Setup completed successfully!');
}

// Run the script
main().catch((error) => {
  printError(`Unexpected error: ${error.message}`);
  console.error(error);
  process.exit(1);
});
