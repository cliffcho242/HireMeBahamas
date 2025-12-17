#!/bin/bash
# =============================================================================
# Neon Pooler Compatibility Check
# =============================================================================
# This script verifies that the codebase doesn't contain patterns that would
# break Neon pooled connections (PgBouncer compatibility).
#
# Run this in CI/CD to prevent regressions.
#
# Usage:
#   ./scripts/check_neon_compatibility.sh
#
# Exit codes:
#   0 = All checks passed
#   1 = Found violations
# =============================================================================

set -e

ERRORS=0
WARNINGS=0

echo "🔍 Checking Neon Pooler Compatibility..."
echo ""

# =============================================================================
# CHECK 1: No sslmode in database configuration
# =============================================================================
echo "CHECK 1: Verifying sslmode is not added to URLs..."

# Check for sslmode=require being added (not just in comments or strings)
# Focus on primary application paths (app/ and api/), exclude legacy backend/ paths
if grep -r "sslmode=require" app/ api/ --include="*.py" | \
   grep -v "^[[:space:]]*#" | \
   grep -v '"""' | \
   grep -v "Example:" | \
   grep -v "Format:" | \
   grep -v "Required format:" | \
   grep -v "OLD:" | \
   grep -v "WRONG:" | \
   grep -v "DEPRECATED:" | \
   grep -v "❌" | \
   grep -v "Before:" | \
   grep -v "backend_app" > /dev/null 2>&1; then
    echo "❌ FAIL: Found sslmode=require in code (outside comments)"
    echo "         This will crash Neon pooler connections!"
    echo ""
    grep -rn "sslmode=require" app/ api/ --include="*.py" | \
        grep -v "^[[:space:]]*#" | \
        grep -v '"""' | \
        grep -v "Example:" | \
        grep -v "Format:" | \
        grep -v "Required format:" | \
        grep -v "OLD:" | \
        grep -v "WRONG:" | \
        grep -v "DEPRECATED:" | \
        grep -v "❌" | \
        grep -v "Before:" | \
        grep -v "backend_app"
    echo ""
    ERRORS=$((ERRORS + 1))
else
    echo "✅ PASS: No sslmode=require found in active code"
fi

# Check for ensure_sslmode() calls that actually modify URLs (in primary paths only)
if grep -r "ensure_sslmode" app/ api/ --include="*.py" | \
   grep -v "def ensure_sslmode" | \
   grep -v "^[[:space:]]*#" | \
   grep -v "import" | \
   grep -v "DEPRECATED" | \
   grep -v "deprecated" | \
   grep -v "no longer" | \
   grep -v "backend_app" > /dev/null 2>&1; then
    echo "⚠️  WARNING: Found ensure_sslmode() calls"
    echo "            Verify these don't actually add sslmode"
    echo ""
    grep -rn "ensure_sslmode" app/ api/ --include="*.py" | \
        grep -v "def ensure_sslmode" | \
        grep -v "^[[:space:]]*#" | \
        grep -v "import" | \
        grep -v "DEPRECATED" | \
        grep -v "deprecated" | \
        grep -v "no longer" | \
        grep -v "backend_app"
    echo ""
    WARNINGS=$((WARNINGS + 1))
else
    echo "✅ PASS: No active ensure_sslmode() calls found"
fi

echo ""

# =============================================================================
# CHECK 2: No startup DB options in connect_args
# =============================================================================
echo "CHECK 2: Verifying no startup DB options in connect_args..."

# Check for options parameter with -c flag (startup options)
if grep -r "options.*-c" app/ api/ backend/app/ --include="*.py" | \
   grep -v "^[[:space:]]*#" | \
   grep -v "WRONG:" | \
   grep -v "NOT SUPPORTED" > /dev/null 2>&1; then
    echo "❌ FAIL: Found startup DB options (-c flag)"
    echo "         PgBouncer doesn't support startup options!"
    echo ""
    grep -rn "options.*-c" app/ api/ backend/app/ --include="*.py" | \
        grep -v "^[[:space:]]*#" | \
        grep -v "WRONG:" | \
        grep -v "NOT SUPPORTED"
    echo ""
    ERRORS=$((ERRORS + 1))
else
    echo "✅ PASS: No startup DB options found"
fi

# Check for server_settings parameter (in primary paths only)
if grep -r "server_settings" app/ api/ --include="*.py" | \
   grep -v "^[[:space:]]*#" | \
   grep -v "WRONG:" | \
   grep -v "NOT SUPPORTED" | \
   grep -v "NO server_settings" | \
   grep -v "backend_app" > /dev/null 2>&1; then
    echo "❌ FAIL: Found server_settings parameter"
    echo "         PgBouncer doesn't support server settings!"
    echo ""
    grep -rn "server_settings" app/ api/ --include="*.py" | \
        grep -v "^[[:space:]]*#" | \
        grep -v "WRONG:" | \
        grep -v "NOT SUPPORTED" | \
        grep -v "NO server_settings" | \
        grep -v "backend_app"
    echo ""
    ERRORS=$((ERRORS + 1))
else
    echo "✅ PASS: No server_settings found"
fi

echo ""

# =============================================================================
# CHECK 3: No index creation on startup
# =============================================================================
echo "CHECK 3: Verifying no index creation on startup..."

# Check for create_indexes in startup code
if grep -r "create_indexes" app/main.py backend/app/main.py api/main.py --include="*.py" 2>/dev/null | \
   grep -v "^[[:space:]]*#" > /dev/null 2>&1; then
    echo "❌ FAIL: Found create_indexes() call in startup code"
    echo "         Index creation must be manual via migrations!"
    echo ""
    grep -n "create_indexes" app/main.py backend/app/main.py api/main.py --include="*.py" 2>/dev/null | \
        grep -v "^[[:space:]]*#"
    echo ""
    ERRORS=$((ERRORS + 1))
else
    echo "✅ PASS: No index creation in startup code"
fi

# Check for Base.metadata.create_all in startup
if grep -r "Base.metadata.create_all" app/main.py backend/app/main.py --include="*.py" 2>/dev/null | \
   grep -v "^[[:space:]]*#" | \
   grep -v "WRONG:" | \
   grep -v "NOT SUPPORTED" > /dev/null 2>&1; then
    echo "❌ FAIL: Found Base.metadata.create_all() in startup code"
    echo "         Table creation must be via migrations!"
    echo ""
    grep -n "Base.metadata.create_all" app/main.py backend/app/main.py --include="*.py" 2>/dev/null | \
        grep -v "^[[:space:]]*#" | \
        grep -v "WRONG:" | \
        grep -v "NOT SUPPORTED"
    echo ""
    ERRORS=$((ERRORS + 1))
else
    echo "✅ PASS: No table creation in startup code"
fi

echo ""

# =============================================================================
# CHECK 4: Health endpoint doesn't access database
# =============================================================================
echo "CHECK 4: Verifying health endpoint is database-free..."

# Look for health endpoint that accesses database
if grep -A 10 '@app.get("/health"' app/main.py backend/app/main.py 2>/dev/null | \
   grep -E "get_db|test_connection|engine|SessionLocal" > /dev/null 2>&1; then
    echo "⚠️  WARNING: Health endpoint may access database"
    echo "            Health checks should be instant without DB access"
    echo ""
    WARNINGS=$((WARNINGS + 1))
else
    echo "✅ PASS: Health endpoint appears database-free"
fi

echo ""

# =============================================================================
# SUMMARY
# =============================================================================
echo "========================================="
echo "Neon Pooler Compatibility Check Complete"
echo "========================================="
echo ""
echo "Errors:   $ERRORS"
echo "Warnings: $WARNINGS"
echo ""

if [ $ERRORS -gt 0 ]; then
    echo "❌ FAILED: Fix errors before deploying to Neon"
    echo ""
    echo "See NEON_POOLER_RULES.md for details"
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo "⚠️  WARNINGS: Review warnings to ensure compatibility"
    echo ""
    echo "See NEON_POOLER_RULES.md for best practices"
    exit 0
else
    echo "✅ SUCCESS: All compatibility checks passed!"
    echo ""
    echo "Your app is Neon pooler compatible 🎉"
    exit 0
fi
