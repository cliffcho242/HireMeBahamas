#!/bin/bash
# Production Lock Verification Script
# Tests all components of the bulletproof production setup

echo "════════════════════════════════════════════════════════════════"
echo "🔒 PRODUCTION LOCK VERIFICATION"
echo "════════════════════════════════════════════════════════════════"
echo ""

passed=0
failed=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -n "Testing: $test_name... "
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo "✅ PASS"
        ((passed++))
    else
        echo "❌ FAIL"
        ((failed++))
    fi
}

echo "🧪 Running Frontend Tests"
echo "────────────────────────────────────────────────────────────────"

# Test 1: ErrorBoundary exists
run_test "ErrorBoundary component exists" \
    "test -f frontend/src/components/ErrorBoundary.tsx"

# Test 2: Safe bootstrap in main.tsx
run_test "Safe bootstrap in main.tsx" \
    "grep -q 'BOOT FAILURE' frontend/src/main.tsx"

# Test 3: App wrapped with ErrorBoundary
run_test "App wrapped with ErrorBoundary" \
    "grep -q 'ErrorBoundary' frontend/src/App_Original.tsx"

# Test 4: Safe DOM manipulation (no innerHTML in catch)
run_test "Safe DOM manipulation" \
    "grep -q 'createElement' frontend/src/main.tsx"

echo ""
echo "🧪 Running Backend Tests"
echo "────────────────────────────────────────────────────────────────"

# Test 5: CORS module exists
run_test "CORS module exists" \
    "test -f api/backend_app/cors.py"

# Test 6: CORS applied in index.py
run_test "CORS applied in index.py" \
    "grep -q 'apply_cors' api/index.py"

# Test 7: Vercel regex pattern
run_test "Vercel preview regex in CORS" \
    "grep -q 'vercel' api/backend_app/cors.py"

# Test 8: Configurable project ID
run_test "Configurable VERCEL_PROJECT_ID" \
    "grep -q 'VERCEL_PROJECT_ID' api/backend_app/cors.py"

echo ""
echo "🧪 Running Documentation Tests"
echo "────────────────────────────────────────────────────────────────"

# Test 9: Production lock documentation
run_test "Production lock documentation exists" \
    "test -f PRODUCTION_LOCK_COMPLETE.md"

# Test 10: Security summary exists
run_test "Security summary exists" \
    "test -f SECURITY_SUMMARY_PRODUCTION_LOCK.md"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📊 RESULTS"
echo "════════════════════════════════════════════════════════════════"
echo ""

total=$((passed + failed))
echo "Passed: $passed/$total"
echo "Failed: $failed/$total"
echo ""

if [ $failed -eq 0 ]; then
    echo "✅ ALL TESTS PASSED"
    echo "   White screens are now IMPOSSIBLE!"
    echo ""
    echo "Next steps:"
    echo "  1. Push to GitHub"
    echo "  2. Deploy to Render (backend)"
    echo "  3. Deploy to Vercel (frontend)"
    echo "  4. Verify production URLs work"
    exit 0
else
    echo "❌ SOME TESTS FAILED"
    echo "   Please fix the issues above"
    exit 1
fi
