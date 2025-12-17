#!/bin/bash
#
# 8️⃣ VERCEL ENV LOCK (MANDATORY): Environment Variable Verification Script
#
# This script verifies that environment variables are correctly configured
# according to the VERCEL ENV LOCK mandatory rules.
#
# 🚫 No backend secrets (DATABASE_URL, JWT_SECRET, etc.)
# 🚫 No DATABASE_URL in Vercel frontend environment
# 🚫 No localhost URLs in production
#
# See: VERCEL_ENV_LOCK.md for complete documentation
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

# Array of forbidden unprefixed variables that commonly cause issues
FORBIDDEN_UNPREFIXED_VARS=("API_URL" "DATABASE_URL" "BACKEND_URL")

# Array of wrong framework prefixes
WRONG_PREFIXES=("NEXT_PUBLIC_")

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
    
    # Check for forbidden unprefixed variables
    FOUND_FORBIDDEN=false
    for var in "${FORBIDDEN_UNPREFIXED_VARS[@]}"; do
        if grep -q "^${var}=" frontend/.env.example; then
            if [ "$FOUND_FORBIDDEN" = false ]; then
                echo -e "${RED}❌ ERROR: frontend/.env.example contains unprefixed variables:${NC}"
                FOUND_FORBIDDEN=true
                ERRORS=$((ERRORS + 1))
            fi
            echo "   - ${var} (should be VITE_${var})"
        fi
    done
    
    if [ "$FOUND_FORBIDDEN" = false ]; then
        echo -e "${GREEN}✓${NC} No forbidden unprefixed variables found"
    else
        echo "   Frontend variables must have VITE_ prefix to be exposed by Vercel."
    fi
    
    # 🚫 VERCEL ENV LOCK: Check for forbidden backend secrets with VITE_ prefix
    # NOTE: This list is also defined in frontend/src/config/envValidator.ts
    # Keep both lists synchronized when adding new forbidden variables.
    FORBIDDEN_SECRETS=("DATABASE_URL" "POSTGRES_URL" "JWT_SECRET" "JWT_SECRET_KEY" "SECRET_KEY" "PRIVATE_KEY" "CRON_SECRET" "API_SECRET" "DB_PASSWORD")
    FOUND_SECRET=false
    for secret in "${FORBIDDEN_SECRETS[@]}"; do
        if grep -q "^VITE_${secret}=" frontend/.env.example; then
            if [ "$FOUND_SECRET" = false ]; then
                echo -e "${RED}❌ CRITICAL SECURITY ERROR: Backend secrets exposed with VITE_ prefix:${NC}"
                echo "   🚫 VERCEL ENV LOCK VIOLATION: No backend secrets"
                FOUND_SECRET=true
                ERRORS=$((ERRORS + 1))
            fi
            echo "   - VITE_${secret} (NEVER expose backend secrets to frontend!)"
        fi
    done
    
    if [ "$FOUND_SECRET" = false ]; then
        echo -e "${GREEN}✓${NC} No backend secrets exposed (VERCEL ENV LOCK compliant)"
    else
        echo "   Remove these immediately! See VERCEL_ENV_LOCK.md for security rules."
    fi
    
    # 🚫 VERCEL ENV LOCK: Check for localhost URLs in example (warning only)
    if grep -q "localhost\|127\.0\.0\.1" frontend/.env.example; then
        echo -e "${YELLOW}⚠️  INFO: localhost URLs found in .env.example${NC}"
        echo "   This is OK for local development, but remember:"
        echo "   🚫 No localhost URLs in production (Vercel Dashboard)"
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
if [ -f "VERCEL_ENV_LOCK.md" ]; then
    echo -e "${GREEN}✓${NC} VERCEL_ENV_LOCK.md exists (MANDATORY)"
else
    echo -e "${RED}❌ ERROR: VERCEL_ENV_LOCK.md not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

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
    echo "Your environment variable configuration is VERCEL ENV LOCK compliant."
    echo ""
    echo "Next steps:"
    echo "  1. Configure environment variables in Vercel Dashboard"
    echo "     - Use VITE_API_URL=https://your-backend.onrender.com"
    echo "     - 🚫 NO backend secrets (DATABASE_URL, JWT_SECRET, etc.)"
    echo "     - 🚫 NO localhost URLs in production"
    echo "  2. Deploy and verify in browser console"
    echo "  3. See VERCEL_ENV_LOCK.md for complete requirements"
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
