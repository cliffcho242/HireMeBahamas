#!/usr/bin/env node
/**
 * Verification script to ensure all required dependencies for UserProfile page are installed
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🔍 Verifying UserProfile page dependencies...\n');

// Required dependencies for UserProfile component
const requiredDeps = {
  'framer-motion': '^12.0.0',
  '@heroicons/react': '^2.0.0',
  'react-hot-toast': '^2.0.0',
  'react-router-dom': '^6.0.0 || ^7.0.0',
  'react': '^18.0.0',
  'react-dom': '^18.0.0'
};

// Read package.json
const packageJsonPath = path.join(__dirname, 'package.json');
const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));

let allDepsPresent = true;
let issues = [];

console.log('Required dependencies for UserProfile page:\n');

// Check each required dependency
for (const [dep, versionRange] of Object.entries(requiredDeps)) {
  const installedVersion = packageJson.dependencies?.[dep];
  
  if (!installedVersion) {
    console.log(`❌ ${dep}: MISSING`);
    allDepsPresent = false;
    issues.push(`Missing dependency: ${dep} (required: ${versionRange})`);
  } else {
    console.log(`✅ ${dep}: ${installedVersion}`);
  }
}

// Check if node_modules exists
const nodeModulesPath = path.join(__dirname, 'node_modules');
if (!fs.existsSync(nodeModulesPath)) {
  console.log('\n⚠️  Warning: node_modules directory not found. Run "npm install".');
  allDepsPresent = false;
  issues.push('node_modules directory not found');
} else {
  console.log('\n✅ node_modules directory exists');
  
  // Verify each package is actually installed in node_modules
  console.log('\nVerifying installation in node_modules:\n');
  for (const dep of Object.keys(requiredDeps)) {
    const depPath = path.join(nodeModulesPath, dep);
    if (fs.existsSync(depPath)) {
      console.log(`✅ ${dep} is installed`);
    } else {
      console.log(`❌ ${dep} is NOT installed in node_modules`);
      allDepsPresent = false;
      issues.push(`${dep} missing from node_modules`);
    }
  }
}

// Check TypeScript compilation
console.log('\n📋 Additional checks:\n');

const userProfilePath = path.join(__dirname, 'src', 'pages', 'UserProfile.tsx');
if (fs.existsSync(userProfilePath)) {
  console.log('✅ UserProfile.tsx exists');
  
  // Read and verify imports
  const userProfileContent = fs.readFileSync(userProfilePath, 'utf8');
  const requiredImports = [
    'framer-motion',
    '@heroicons/react',
    'react-hot-toast',
    'react-router-dom'
  ];
  
  console.log('\nVerifying imports in UserProfile.tsx:\n');
  for (const importPkg of requiredImports) {
    if (userProfileContent.includes(importPkg)) {
      console.log(`✅ ${importPkg} is imported`);
    } else {
      console.log(`⚠️  ${importPkg} is NOT imported (may not be used)`);
    }
  }
} else {
  console.log('❌ UserProfile.tsx NOT found');
  allDepsPresent = false;
  issues.push('UserProfile.tsx file missing');
}

// Final summary
console.log('\n' + '='.repeat(60));
if (allDepsPresent && issues.length === 0) {
  console.log('✅ SUCCESS: All UserProfile page dependencies are properly installed!');
  console.log('='.repeat(60));
  process.exit(0);
} else {
  console.log('❌ ISSUES FOUND:');
  issues.forEach(issue => console.log(`  - ${issue}`));
  console.log('='.repeat(60));
  console.log('\n💡 To fix: Run "npm install" in the frontend directory');
  process.exit(1);
}
