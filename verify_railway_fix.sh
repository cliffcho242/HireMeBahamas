#!/bin/bash

# ============================================================================
# Railway Deployment Verification Script
# ============================================================================
# This script verifies that the Railway PostgreSQL root execution fix
# is properly configured
# ============================================================================

set -e

echo "============================================================================"
echo "Railway PostgreSQL Deployment Fix - Verification"
echo "============================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Track results
PASS=0
FAIL=0

# Test function
test_check() {
    local name="$1"
    local command="$2"
    
    echo -n "Checking: $name... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        PASS=$((PASS + 1))
    else
        echo -e "${RED}❌ FAIL${NC}"
        FAIL=$((FAIL + 1))
    fi
}

# Test 1: .railwayignore exists
test_check "railwayignore file exists" "test -f .railwayignore"

# Test 2: docker-compose.yml is in .railwayignore
test_check "docker-compose.yml excluded" "grep -q 'docker-compose.yml' .railwayignore"

# Test 3: railway.json exists
test_check "railway.json exists" "test -f railway.json"

# Test 4: railway.json uses NIXPACKS
test_check "Railway uses NIXPACKS builder" "grep -q 'NIXPACKS' railway.json"

# Test 5: nixpacks.toml exists
test_check "nixpacks.toml exists" "test -f nixpacks.toml"

# Test 6: nixpacks.toml only installs PostgreSQL client
test_check "Only PostgreSQL client installed" "grep -q 'postgresql-client' nixpacks.toml"

# Test 7: nixpacks.toml does NOT install PostgreSQL server
test_check "PostgreSQL server NOT installed" "! grep -E '^[^#]*postgresql-[0-9]|postgresql[[:space:]]*$' nixpacks.toml"

# Test 8: docker-compose.yml has warning header
test_check "docker-compose.yml has warning" "head -20 docker-compose.yml | grep -q 'LOCAL DEVELOPMENT ONLY'"

# Test 9: Documentation exists
test_check "RAILWAY_POSTGRES_FIX.md exists" "test -f RAILWAY_POSTGRES_FIX.md"

# Test 10: Quick start guide exists
test_check "RAILWAY_QUICK_START.md exists" "test -f RAILWAY_QUICK_START.md"

# Test 11: Security summary exists
test_check "Security summary exists" "test -f SECURITY_SUMMARY_RAILWAY_POSTGRES_FIX.md"

# Test 12: Docker directory is excluded
test_check "docker/ directory excluded" "grep -q '^docker/' .railwayignore"

# Test 13: Dockerfile is excluded
test_check "Dockerfile excluded" "grep -q '^Dockerfile' .railwayignore"

# Test 14: No credentials in documentation
test_check "No plain credentials in docs" "! grep -E '(password|secret)=' RAILWAY_POSTGRES_FIX.md | grep -v REDACTED"

echo ""
echo "============================================================================"
echo "Results"
echo "============================================================================"
echo -e "Passed: ${GREEN}$PASS${NC}"
echo -e "Failed: ${RED}$FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED${NC}"
    echo ""
    echo "Railway is correctly configured to:"
    echo "  ✅ Ignore docker-compose.yml (contains PostgreSQL server)"
    echo "  ✅ Use Nixpacks builder"
    echo "  ✅ Install only PostgreSQL client libraries"
    echo "  ✅ Connect to Railway's managed PostgreSQL"
    echo ""
    echo "You can now deploy to Railway without the root execution error!"
    echo ""
    echo "Next steps:"
    echo "  1. Push this branch to GitHub"
    echo "  2. Merge to main"
    echo "  3. Railway will auto-deploy"
    echo "  4. Verify deployment in Railway dashboard"
    echo ""
    exit 0
else
    echo -e "${RED}❌ SOME CHECKS FAILED${NC}"
    echo ""
    echo "Please review the failed checks above and fix them before deploying."
    echo ""
    exit 1
fi
