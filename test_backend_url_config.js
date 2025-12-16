/**
 * Test Backend URL Configuration
 */

const fs = require('fs');
const path = require('path');

const results = [];

// Files to check
const filesToCheck = [
  'frontend/src/services/api.ts',
  'frontend/src/services/api_ai_enhanced.ts',
  'frontend/src/lib/realtime.ts',
  'frontend/src/graphql/client.ts',
  'frontend/src/utils/connectionTest.ts',
];

// Anti-patterns to detect
const antiPatterns = [
  {
    pattern: /return\s+['"]http:\/\/localhost:8000['"]/,
    message: '❌ Found hardcoded localhost:8000 return statement (should throw error or use fallback)',
  },
  {
    pattern: /=\s+['"]http:\/\/localhost:8000['"](?!;?\s*\/\/)/,
    message: '❌ Found hardcoded localhost:8000 assignment outside of comments',
  },
  {
    pattern: /process\.env\.BACKEND_URL(?!.*\/\/)/,
    message: '❌ Found process.env.BACKEND_URL (not exposed to browser, use import.meta.env.VITE_API_URL)',
  },
  {
    pattern: /process\.env\.NEXT_PUBLIC_BACKEND_URL/,
    message: '❌ Found NEXT_PUBLIC_BACKEND_URL (this is a Vite project, use VITE_API_URL)',
  },
  {
    pattern: /fetch\(['"](localhost|127\.0\.0\.1):8000/,
    message: '❌ Found direct fetch to localhost (should use environment variable)',
  },
  {
    pattern: /\$\{[^}]+\}\/\/api/,
    message: '❌ Found double slash in URL construction',
  },
];

// Good patterns to verify
const goodPatterns = [
  {
    pattern: /import\.meta\.env\.VITE_API_URL/,
    message: '✅ Uses VITE_API_URL environment variable',
    required: true,
  },
  {
    pattern: /throw new Error\(['"].*could not be determined/i,
    message: '✅ Throws error when URL cannot be determined',
    required: true,
  },
];

console.log('🔍 Testing Backend URL Configuration...\n');

for (const filePath of filesToCheck) {
  const fullPath = path.join(process.cwd(), filePath);
  const result = {
    file: filePath,
    passed: true,
    issues: [],
  };

  if (!fs.existsSync(fullPath)) {
    result.passed = false;
    result.issues.push('⚠️  File not found');
    results.push(result);
    continue;
  }

  const content = fs.readFileSync(fullPath, 'utf-8');

  // Check for anti-patterns
  for (const { pattern, message } of antiPatterns) {
    if (pattern.test(content)) {
      result.passed = false;
      result.issues.push(message);
    }
  }

  // Check for good patterns
  for (const { pattern, message, required } of goodPatterns) {
    if (pattern.test(content)) {
      result.issues.push(message);
    } else if (required) {
      result.passed = false;
      result.issues.push(`❌ Missing: ${message}`);
    }
  }

  results.push(result);
}

// Print results
console.log('='.repeat(70));
console.log('Test Results');
console.log('='.repeat(70));

let allPassed = true;
for (const result of results) {
  const status = result.passed ? '✅ PASS' : '❌ FAIL';
  console.log(`\n${status}: ${result.file}`);
  
  if (result.issues.length > 0) {
    for (const issue of result.issues) {
      console.log(`  ${issue}`);
    }
  }
  
  if (!result.passed) {
    allPassed = false;
  }
}

console.log('\n' + '='.repeat(70));
console.log(`\nOverall: ${allPassed ? '✅ ALL TESTS PASSED' : '❌ SOME TESTS FAILED'}\n`);

// Exit with appropriate code
process.exit(allPassed ? 0 : 1);
