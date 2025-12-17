#!/usr/bin/env node

/**
 * 🔒 PRE-BUILD SAFETY CHECK
 * 
 * This script validates environment variables before build to catch
 * configuration errors early and prevent broken production deploys.
 * 
 * For Vite projects, environment variables must be prefixed with VITE_
 * to be exposed to the frontend.
 * 
 * RULES:
 * 1. Frontend variables must use VITE_* prefix (not NEXT_PUBLIC_*)
 * 2. Sensitive variables must NEVER have VITE_ prefix
 * 3. Production builds must use HTTPS URLs (not HTTP)
 * 4. Required variables must be set when VITE_REQUIRE_BACKEND_URL=true
 */

/**
 * List of environment variables that should NEVER have VITE_ prefix
 * (these are sensitive and should only be on the backend)
 */
const FORBIDDEN_VITE_VARS = [
  'DATABASE_URL',
  'POSTGRES_URL',
  'JWT_SECRET',
  'SECRET_KEY',
  'PRIVATE_KEY',
  'API_SECRET',
  'DB_PASSWORD',
];

/**
 * List of environment variables that are incorrectly prefixed
 * (wrong framework - Next.js vs Vite)
 */
const WRONG_PREFIX_VARS = [
  'NEXT_PUBLIC_API_URL',
  'NEXT_PUBLIC_BACKEND_URL',
  'NEXT_PUBLIC_SOCKET_URL',
];

/**
 * Validate URL format
 */
function isValidUrl(url) {
  if (!url || typeof url !== 'string') return false;
  return url.startsWith('http://') || url.startsWith('https://');
}

/**
 * Check if URL is secure (HTTPS or localhost)
 */
function isSecureUrl(url) {
  if (!url || typeof url !== 'string') return false;
  
  // Allow HTTP for localhost in development
  if (url.startsWith('http://localhost') || url.startsWith('http://127.0.0.1')) {
    return true;
  }
  
  // In production, require HTTPS
  if (process.env.NODE_ENV === 'production') {
    return url.startsWith('https://');
  }
  
  // In development, allow HTTP
  return true;
}

/**
 * Main validation function
 */
function validateEnvironment() {
  console.log('\n🔍 Running Pre-Build Safety Check...\n');
  
  let hasErrors = false;
  const errors = [];
  const warnings = [];
  
  // Check for forbidden variables with VITE_ prefix
  FORBIDDEN_VITE_VARS.forEach(forbiddenVar => {
    const viteVar = `VITE_${forbiddenVar}`;
    if (process.env[viteVar] !== undefined) {
      hasErrors = true;
      errors.push(
        `❌ CRITICAL SECURITY ERROR: ${viteVar} is exposed to the frontend!\n` +
        `   This is a sensitive variable that should NEVER have VITE_ prefix.\n` +
        `   Remove this from your environment variables immediately.`
      );
    }
  });
  
  // Check for wrong framework prefix
  WRONG_PREFIX_VARS.forEach(wrongVar => {
    if (process.env[wrongVar] !== undefined) {
      hasErrors = true;
      errors.push(
        `❌ WRONG FRAMEWORK PREFIX: ${wrongVar}\n` +
        `   This is a Next.js variable name. This is a VITE project.\n` +
        `   Use VITE_API_URL instead of NEXT_PUBLIC_API_URL`
      );
    }
  });
  
  // Check for required variables
  if (process.env.VITE_REQUIRE_BACKEND_URL === 'true') {
    if (!process.env.VITE_API_URL) {
      hasErrors = true;
      errors.push(
        `❌ MISSING REQUIRED VARIABLE: VITE_API_URL\n` +
        `   VITE_REQUIRE_BACKEND_URL is set to 'true', but VITE_API_URL is not set.\n` +
        `   Either set VITE_API_URL or set VITE_REQUIRE_BACKEND_URL to 'false'.`
      );
    }
  }
  
  // Validate API URL format if set
  if (process.env.VITE_API_URL) {
    const apiUrl = process.env.VITE_API_URL;
    
    if (!isValidUrl(apiUrl)) {
      hasErrors = true;
      errors.push(
        `❌ INVALID URL FORMAT: VITE_API_URL="${apiUrl}"\n` +
        `   URL must start with http:// or https://\n` +
        `   Example: VITE_API_URL=https://api.yourdomain.com`
      );
    } else if (!isSecureUrl(apiUrl) && process.env.NODE_ENV === 'production') {
      hasErrors = true;
      errors.push(
        `❌ INSECURE URL IN PRODUCTION: VITE_API_URL="${apiUrl}"\n` +
        `   Production builds must use HTTPS.\n` +
        `   HTTP is only allowed for localhost in development.\n` +
        `   Change to: VITE_API_URL=https://your-domain.com`
      );
    }
  }
  
  // Validate Socket URL if set
  if (process.env.VITE_SOCKET_URL) {
    const socketUrl = process.env.VITE_SOCKET_URL;
    
    if (!isValidUrl(socketUrl)) {
      hasErrors = true;
      errors.push(
        `❌ INVALID URL FORMAT: VITE_SOCKET_URL="${socketUrl}"\n` +
        `   URL must start with http:// or https://`
      );
    } else if (!isSecureUrl(socketUrl) && process.env.NODE_ENV === 'production') {
      hasErrors = true;
      errors.push(
        `❌ INSECURE URL IN PRODUCTION: VITE_SOCKET_URL="${socketUrl}"\n` +
        `   Production builds must use HTTPS.`
      );
    }
  }
  
  // Report results
  if (errors.length > 0) {
    console.error('❌ Pre-Build Safety Check FAILED\n');
    errors.forEach(error => console.error(error + '\n'));
  }
  
  if (warnings.length > 0) {
    console.warn('⚠️  Pre-Build Warnings:\n');
    warnings.forEach(warning => console.warn(warning + '\n'));
  }
  
  if (!hasErrors) {
    console.log('✅ Pre-Build Safety Check Passed!\n');
    
    // Show configured variables
    const viteVars = Object.keys(process.env).filter(key => key.startsWith('VITE_'));
    if (viteVars.length > 0) {
      console.log('📋 Configured frontend variables:');
      viteVars.forEach(key => {
        const value = process.env[key];
        // Mask long values for security
        const displayValue = typeof value === 'string' && value.length > 30
          ? value.substring(0, 30) + '...'
          : value;
        console.log(`   ✓ ${key} = ${displayValue}`);
      });
      console.log('');
    } else {
      console.log('ℹ️  No VITE_* environment variables configured.');
      console.log('   This is OK if using same-origin for API calls.\n');
    }
  }
  
  if (hasErrors) {
    console.error('💥 Build aborted due to environment configuration errors.');
    console.error('   Fix the errors above and try again.\n');
    process.exit(1);
  }
}

// Run validation
try {
  validateEnvironment();
} catch (error) {
  console.error('❌ Pre-build check failed with error:', error.message);
  process.exit(1);
}
