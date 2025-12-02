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
console.log('Database Schema:');
console.log('- Users table:', users ? '✓' : '✗');
console.log('- Jobs table:', jobs ? '✓' : '✗');
console.log('');
console.log('💡 Ready to run TypeScript files directly!');
