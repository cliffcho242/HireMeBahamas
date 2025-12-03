#!/usr/bin/env node

/**
 * Verify that React types are properly installed and accessible
 * This script helps diagnose TypeScript module resolution issues
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Verifying React type declarations...\n');

// Check if node_modules exists
const nodeModulesPath = path.join(__dirname, 'node_modules');
if (!fs.existsSync(nodeModulesPath)) {
  console.error('❌ node_modules directory not found!');
  console.error('   Run: npm install');
  process.exit(1);
}
console.log('✅ node_modules directory exists');

// Check for react package
const reactPath = path.join(nodeModulesPath, 'react');
if (!fs.existsSync(reactPath)) {
  console.error('❌ react package not found!');
  console.error('   Run: npm install react');
  process.exit(1);
}
console.log('✅ react package is installed');

// Check for react-dom package
const reactDomPath = path.join(nodeModulesPath, 'react-dom');
if (!fs.existsSync(reactDomPath)) {
  console.error('❌ react-dom package not found!');
  console.error('   Run: npm install react-dom');
  process.exit(1);
}
console.log('✅ react-dom package is installed');

// Check for @types/react
const typesReactPath = path.join(nodeModulesPath, '@types', 'react');
if (!fs.existsSync(typesReactPath)) {
  console.error('❌ @types/react package not found!');
  console.error('   Run: npm install --save-dev @types/react');
  process.exit(1);
}
console.log('✅ @types/react package is installed');

// Check for @types/react-dom
const typesReactDomPath = path.join(nodeModulesPath, '@types', 'react-dom');
if (!fs.existsSync(typesReactDomPath)) {
  console.error('❌ @types/react-dom package not found!');
  console.error('   Run: npm install --save-dev @types/react-dom');
  process.exit(1);
}
console.log('✅ @types/react-dom package is installed');

// Check TypeScript configuration
const tsconfigPath = path.join(__dirname, 'tsconfig.json');
if (!fs.existsSync(tsconfigPath)) {
  console.error('❌ tsconfig.json not found!');
  process.exit(1);
}
console.log('✅ tsconfig.json exists');

try {
  const tsconfigContent = fs.readFileSync(tsconfigPath, 'utf8');
  
  // Try to parse with comment removal
  let withoutComments = tsconfigContent
    // Remove multi-line comments
    .replace(/\/\*[\s\S]*?\*\//g, ' ')
    // Remove single-line comments  
    .replace(/\/\/[^\n]*/g, '')
    // Normalize whitespace
    .replace(/\s+/g, ' ')
    // Remove trailing commas
    .replace(/,\s*([}\]])/g, '$1');
  
  let tsconfig;
  let usedFallback = false;
  
  try {
    tsconfig = JSON.parse(withoutComments);
  } catch (parseError) {
    // Fallback: Use string-based validation (which is sufficient for our needs)
    usedFallback = true;
    
    const hasJsx = tsconfigContent.includes('"jsx"');
    const hasReactJsx = tsconfigContent.includes('react-jsx');
    const hasInclude = tsconfigContent.includes('"include"');
    const hasSrc = tsconfigContent.includes('"src"');
    const hasModuleRes = tsconfigContent.includes('"moduleResolution"');
    
    if (!hasJsx || !hasReactJsx) {
      console.warn('⚠️  JSX configuration might not be set to "react-jsx"');
      process.exit(1);
    } else {
      console.log('✅ JSX configuration is correct (react-jsx)');
    }
    
    if (!hasModuleRes) {
      console.warn('⚠️  moduleResolution might not be configured');
    } else {
      console.log('✅ Module resolution configuration found');
    }
    
    if (!hasInclude || !hasSrc) {
      console.warn('⚠️  src directory might not be included in TypeScript compilation');
      process.exit(1);
    } else {
      console.log('✅ src directory is included in compilation');
    }
  }
  
  // If we successfully parsed, do detailed validation
  if (!usedFallback) {
    // Check JSX configuration
    if (tsconfig.compilerOptions?.jsx !== 'react-jsx') {
      console.warn('⚠️  JSX is not set to "react-jsx". Current value:', tsconfig.compilerOptions?.jsx || 'not set');
      process.exit(1);
    } else {
      console.log('✅ JSX configuration is correct (react-jsx)');
    }
    
    // Check module resolution
    const moduleRes = tsconfig.compilerOptions?.moduleResolution;
    if (moduleRes !== 'bundler' && moduleRes !== 'node' && moduleRes !== 'node16' && moduleRes !== 'nodenext') {
      console.warn('⚠️  moduleResolution might need adjustment. Current value:', moduleRes || 'not set');
    } else {
      console.log('✅ Module resolution configuration is valid (' + moduleRes + ')');
    }
    
    // Check if src directory is included
    if (!Array.isArray(tsconfig.include) || !tsconfig.include.includes('src')) {
      console.warn('⚠️  src directory is not included in TypeScript compilation');
      if (Array.isArray(tsconfig.include)) {
        console.warn('   Current include:', tsconfig.include);
      }
      process.exit(1);
    } else {
      console.log('✅ src directory is included in compilation');
    }
  }
} catch (error) {
  console.error('❌ Error reading tsconfig.json:', error.message);
  process.exit(1);
}

// Check vite-env.d.ts
const viteEnvPath = path.join(__dirname, 'src', 'vite-env.d.ts');
if (!fs.existsSync(viteEnvPath)) {
  console.warn('⚠️  vite-env.d.ts not found. Vite types might not be available.');
} else {
  console.log('✅ vite-env.d.ts exists');
}

console.log('\n✨ All React type declaration checks passed!');
console.log('   Your TypeScript configuration should work correctly.\n');
