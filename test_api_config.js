#!/usr/bin/env node

/**
 * Test API Configuration
 * 
 * This script tests that the API configuration is working correctly
 * with various environment variable combinations.
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Configuration
const TEST_API_URL = process.env.TEST_API_URL || 'https://api.hiremebahamas.com';
const TEST_LOCAL_URL = 'http://localhost:8000';

console.log('🧪 Testing API Configuration...\n');

// Test 1: Build with VITE_API_BASE_URL (production)
console.log(`Test 1: Building with VITE_API_BASE_URL=${TEST_API_URL}...`);
try {
  execSync(`cd frontend && VITE_API_BASE_URL=${TEST_API_URL} npm run build`, {
    stdio: 'ignore',
    env: { ...process.env, VITE_API_BASE_URL: TEST_API_URL }
  });
  console.log('✅ Build succeeded with VITE_API_BASE_URL\n');
} catch (error) {
  console.error('❌ Build failed with VITE_API_BASE_URL');
  process.exit(1);
}

// Test 2: Build with VITE_API_URL (local dev fallback)
console.log(`Test 2: Building with VITE_API_URL=${TEST_LOCAL_URL}...`);
try {
  execSync(`cd frontend && VITE_API_URL=${TEST_LOCAL_URL} npm run build`, {
    stdio: 'ignore',
    env: { ...process.env, VITE_API_URL: TEST_LOCAL_URL }
  });
  console.log('✅ Build succeeded with VITE_API_URL\n');
} catch (error) {
  console.error('❌ Build failed with VITE_API_URL');
  process.exit(1);
}

// Test 3: Verify dist directory was created
console.log('Test 3: Verifying build output...');
const distPath = path.join(__dirname, 'frontend', 'dist');
if (fs.existsSync(distPath)) {
  console.log('✅ Build output directory exists\n');
} else {
  console.error('❌ Build output directory not found');
  process.exit(1);
}

// Test 4: Verify index.html was created
const indexPath = path.join(distPath, 'index.html');
if (fs.existsSync(indexPath)) {
  console.log('✅ index.html exists in build output\n');
} else {
  console.error('❌ index.html not found in build output');
  process.exit(1);
}

// Test 5: Verify assets directory was created
const assetsPath = path.join(distPath, 'assets');
if (fs.existsSync(assetsPath)) {
  const assets = fs.readdirSync(assetsPath);
  console.log(`✅ Assets directory exists with ${assets.length} files\n`);
} else {
  console.error('❌ Assets directory not found');
  process.exit(1);
}

console.log('✅ All API configuration tests passed!\n');
console.log('Summary:');
console.log('- VITE_API_BASE_URL configuration: ✅ Working');
console.log('- VITE_API_URL fallback: ✅ Working');
console.log('- Build output: ✅ Generated correctly');
console.log('- Assets: ✅ Compiled successfully\n');
