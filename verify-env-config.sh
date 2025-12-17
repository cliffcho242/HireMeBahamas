#!/bin/bash
#
# 🔒 FOREVER FIX: Environment Variable Verification Script
#
# This script verifies that environment variables are correctly configured
# according to the FOREVER FIX law.
#
# Usage:
#   ./verify-env-config.sh
#

set -e

echo ""
echo "🔍 Environment Variable Configuration Verifier"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# Check if we're in the right directory
if [ ! -f "frontend/package.json" ]; then
    echo -e "${RED}❌ ERROR: Must run this script from the repository root${NC}"
    exit 1
fi

echo "📋 Checking frontend environment configuration..."
echo ""

# Check .env.example exists
if [ ! -f "frontend/.env.example" ]; then
    echo -e "${RED}❌ ERROR: frontend/.env.example is missing${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓${NC} frontend/.env.example exists"
fi

# Check .env.example has VITE_ prefix variables
if [ -f "frontend/.env.example" ]; then
    if grep -q "^VITE_" frontend/.env.example; then
        echo -e "${GREEN}✓${NC} frontend/.env.example contains VITE_ variables"
    else
        echo -e "${RED}❌ ERROR: frontend/.env.example missing VITE_ variables${NC}"
        ERRORS=$((ERRORS + 1))
    fi
    
    # Check for incorrect NEXT_PUBLIC_ prefix
    if grep -q "^NEXT_PUBLIC_" frontend/.env.example; then
        echo -e "${RED}❌ ERROR: frontend/.env.example contains NEXT_PUBLIC_ variables${NC}"
        echo "   This is a Vite project, not Next.js. Use VITE_ prefix instead."
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}✓${NC} No incorrect NEXT_PUBLIC_ variables found"
    fi
    
    # Check for unprefixed API_URL or DATABASE_URL
    if grep -q "^API_URL=" frontend/.env.example || grep -q "^DATABASE_URL=" frontend/.env.example; then
        echo -e "${RED}❌ ERROR: frontend/.env.example contains unprefixed API_URL or DATABASE_URL${NC}"
        echo "   Frontend variables must have VITE_ prefix to be exposed by Vercel."
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}✓${NC} No unprefixed API_URL or DATABASE_URL found"
    fi
fi

# Check .gitignore
if [ -f "frontend/.gitignore" ]; then
    if grep -q "^\.env$" frontend/.gitignore; then
        echo -e "${GREEN}✓${NC} .env files are properly ignored"
    else
        echo -e "${YELLOW}⚠️  WARNING: .env might not be properly ignored${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${RED}❌ ERROR: frontend/.gitignore is missing${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check if envValidator.ts exists
if [ -f "frontend/src/config/envValidator.ts" ]; then
    echo -e "${GREEN}✓${NC} Environment validator exists"
else
    echo -e "${YELLOW}⚠️  WARNING: frontend/src/config/envValidator.ts not found${NC}"
    echo "   Runtime validation will not be performed."
    WARNINGS=$((WARNINGS + 1))
fi

# Check if main.tsx imports envValidator
if [ -f "frontend/src/main.tsx" ]; then
    if grep -q "envValidator" frontend/src/main.tsx; then
        echo -e "${GREEN}✓${NC} Environment validator is imported in main.tsx"
    else
        echo -e "${YELLOW}⚠️  WARNING: envValidator not imported in main.tsx${NC}"
        echo "   Runtime validation will not be performed."
        WARNINGS=$((WARNINGS + 1))
    fi
fi

# Check documentation
if [ -f "FOREVER_FIX_ENV_VARIABLES.md" ]; then
    echo -e "${GREEN}✓${NC} FOREVER_FIX_ENV_VARIABLES.md exists"
else
    echo -e "${YELLOW}⚠️  WARNING: FOREVER_FIX_ENV_VARIABLES.md not found${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""
echo "=============================================="

# Summary
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo ""
    echo "Your environment variable configuration follows the FOREVER FIX law."
    echo ""
    echo "Next steps:"
    echo "  1. Configure environment variables in Vercel Dashboard"
    echo "  2. Ensure all frontend variables have VITE_ prefix"
    echo "  3. Deploy and verify in browser console"
    echo ""
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  ${WARNINGS} warning(s) found${NC}"
    echo ""
    echo "Configuration is mostly correct but could be improved."
    echo "Review the warnings above."
    echo ""
    exit 0
else
    echo -e "${RED}❌ ${ERRORS} error(s) found${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠️  ${WARNINGS} warning(s) found${NC}"
    fi
    echo ""
    echo "Your configuration does NOT follow the FOREVER FIX law."
    echo "Review the errors above and fix them before deploying."
    echo ""
    echo "Documentation: FOREVER_FIX_ENV_VARIABLES.md"
    echo ""
    exit 1
fi
