#!/usr/bin/env node
/**
 * Main entry point for TypeScript execution
 * Run with: npx tsx src/main.ts
 * Watch mode: npx tsx watch src/main.ts
 */

import { users, jobs } from './schema';

console.log('✅ HireMeBahamas TypeScript runtime initialized');
console.log('📦 Using tsx for ESM support');
console.log('');
console.log('Schema imports successful:');
console.log('- Users table schema: imported');
console.log('- Jobs table schema: imported');
console.log('');
console.log('💡 Ready to run TypeScript files directly!');
