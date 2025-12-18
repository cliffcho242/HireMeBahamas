#!/bin/bash
# Test frontend credentials configuration for cross-origin support

echo "Testing frontend credentials configuration..."
echo "======================================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

errors=0
warnings=0

# Check api.ts file
API_FILE="frontend/src/services/api.ts"

if [ ! -f "$API_FILE" ]; then
    echo -e "${RED}❌ File not found: $API_FILE${NC}"
    exit 1
fi

echo -e "\n📁 Checking: $API_FILE"
echo "----------------------------------------------------------------------"

# Check withCredentials setting in axios
if grep -q "withCredentials: true" "$API_FILE"; then
    echo -e "${GREEN}✓ axios withCredentials is set to true (cross-origin cookies)${NC}"
else
    echo -e "${RED}❌ axios withCredentials must be true for cross-origin cookies${NC}"
    ((errors++))
fi

# Check credentials: 'include' in apiFetch
if grep -q 'credentials: "include"' "$API_FILE"; then
    echo -e "${GREEN}✓ apiFetch uses credentials: 'include' (cross-origin cookies)${NC}"
else
    echo -e "${RED}❌ apiFetch must use credentials: 'include'${NC}"
    ((errors++))
fi

# Check auth.ts file
AUTH_FILE="frontend/src/services/auth.ts"

if [ -f "$AUTH_FILE" ]; then
    echo -e "\n📁 Checking: $AUTH_FILE"
    echo "----------------------------------------------------------------------"
    
    # Check credentials: 'include' in auth functions
    if grep -q 'credentials: "include"' "$AUTH_FILE"; then
        echo -e "${GREEN}✓ auth.ts uses credentials: 'include' (cross-origin cookies)${NC}"
    else
        echo -e "${YELLOW}⚠️  auth.ts should use credentials: 'include'${NC}"
        ((warnings++))
    fi
fi

# Summary
echo ""
echo "======================================================================"

if [ $warnings -gt 0 ]; then
    echo -e "\n${YELLOW}⚠️  Warnings: $warnings${NC}"
fi

if [ $errors -gt 0 ]; then
    echo -e "\n${RED}❌ FAILED - Frontend credentials configuration has issues${NC}"
    echo "Errors: $errors"
    exit 1
else
    echo -e "\n${GREEN}✅ PASSED - Frontend credentials configuration is correct!${NC}"
    echo ""
    echo "📱 Frontend is configured for cross-origin authentication:"
    echo "  • axios withCredentials: true - sends cookies to backend"
    echo "  • fetch credentials: 'include' - sends cookies to backend"
    echo "  • Compatible with Vercel (frontend) → Render (backend)"
    echo "  • Works on Safari/iPhone with backend SameSite=None"
    exit 0
fi
