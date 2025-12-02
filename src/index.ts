#!/usr/bin/env node
/**
 * Alternative entry point for TypeScript execution
 * Run with: npx tsx src/index.ts
 * Watch mode: npx tsx watch src/index.ts
 */

import { users, jobs } from './schema';

console.log('🚀 Running from src/index.ts');
console.log('✅ HireMeBahamas TypeScript runtime initialized');
console.log('📦 Using tsx for ESM support');
console.log('');
console.log('Schema imports successful:');
console.log('- Users table schema: imported');
console.log('- Jobs table schema: imported');
console.log('');
console.log('💡 Ready to run TypeScript files directly!');
