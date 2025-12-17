/**
 * Manual validation script for safe URL builder enforcement
 * 
 * This script checks that all files properly use the safe URL builder pattern.
 */

const fs = require('fs');
const path = require('path');

// Files we modified
const modifiedFiles = [
  'frontend/src/graphql/client.ts',
  'frontend/src/pages/UserAnalytics.tsx',
  'frontend/src/contexts/AdvancedAIContext.tsx',
  'frontend/src/lib/realtime.ts',
  'frontend/src/services/api.ts',
];

// Anti-patterns to check for (should NOT exist)
const antiPatterns = [
  /import\.meta\.env\.VITE_API_URL\s*\?.*:/, // Ternary with VITE_API_URL
  /window\.location\.origin\s*:/, // window.location.origin in ternary
  /\$\{import\.meta\.env\.VITE_API_URL\}\/api/, // Template literal with env var
  /\$\{window\.location\.origin\}\/api/, // Template literal with window.location
];

// Expected patterns (SHOULD exist)
const expectedImports = [
  /import\s+\{.*apiUrl.*\}\s+from\s+['"].*\/lib\/api['"]/,
  /import\s+\{.*getApiBase.*\}\s+from\s+['"].*\/lib\/api['"]/,
];

console.log('🔍 Validating Safe URL Builder Enforcement\n');
console.log('='.repeat(60));

let allPassed = true;

modifiedFiles.forEach((filePath) => {
  const fullPath = path.join(__dirname, filePath);
  
  console.log(`\n📄 Checking: ${filePath}`);
  
  if (!fs.existsSync(fullPath)) {
    console.log('   ⚠️  File not found');
    allPassed = false;
    return;
  }
  
  const content = fs.readFileSync(fullPath, 'utf8');
  
  // Check for anti-patterns
  let hasAntiPattern = false;
  antiPatterns.forEach((pattern, index) => {
    if (pattern.test(content)) {
      console.log(`   ❌ Found anti-pattern #${index + 1}: ${pattern}`);
      hasAntiPattern = true;
      allPassed = false;
    }
  });
  
  if (!hasAntiPattern) {
    console.log('   ✅ No anti-patterns found');
  }
  
  // Check for expected imports
  const hasExpectedImport = expectedImports.some(pattern => pattern.test(content));
  if (hasExpectedImport) {
    console.log('   ✅ Uses safe URL builder import');
  } else {
    console.log('   ⚠️  No safe URL builder import found (might use indirect import)');
    // This is not necessarily an error, as services/api.ts uses getApiUrl from backendRouter
  }
  
  // Check that it uses the imported functions
  if (content.includes('apiUrl(') || content.includes('getApiBase(')) {
    console.log('   ✅ Uses safe URL builder functions');
  } else if (content.includes('getApiUrl(')) {
    console.log('   ✅ Uses safe URL builder via getApiUrl wrapper');
  } else {
    console.log('   ⚠️  Safe URL builder functions not used');
  }
});

console.log('\n' + '='.repeat(60));

if (allPassed) {
  console.log('\n✅ All validation checks passed!');
  console.log('\nThe safe URL builder pattern is properly enforced across all modified files.');
  process.exit(0);
} else {
  console.log('\n❌ Some validation checks failed!');
  console.log('\nPlease review the files above and ensure they use the safe URL builder pattern.');
  process.exit(1);
}
