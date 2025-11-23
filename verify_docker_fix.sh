#!/bin/bash

echo "=========================================="
echo "Docker PORT Variable Fix Verification"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

pass_count=0
fail_count=0

# Function to check and print result
check_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $2"
        ((pass_count++))
    else
        echo -e "${RED}❌ FAIL${NC}: $2"
        ((fail_count++))
    fi
}

# Test 1: Main Dockerfile CMD format
echo "Test 1: Checking main Dockerfile CMD format..."
grep -q 'CMD \["sh", "-c",' Dockerfile
check_result $? "Main Dockerfile uses exec form with shell"

# Test 2: Main Dockerfile HEALTHCHECK format
echo "Test 2: Checking main Dockerfile HEALTHCHECK format..."
grep -q "CMD sh -c 'curl.*\${PORT" Dockerfile
check_result $? "Main Dockerfile HEALTHCHECK uses shell invocation"

# Test 3: Backend Dockerfile CMD format
echo "Test 3: Checking backend Dockerfile CMD format..."
grep -q 'CMD \["sh", "-c",' backend/Dockerfile
check_result $? "Backend Dockerfile uses exec form with shell"

# Test 4: Backend Dockerfile HEALTHCHECK format
echo "Test 4: Checking backend Dockerfile HEALTHCHECK format..."
grep -q "CMD sh -c 'curl.*\${PORT" backend/Dockerfile
check_result $? "Backend Dockerfile HEALTHCHECK uses shell invocation"

# Test 5: Verify no old shell form CMD remains in main Dockerfile
echo "Test 5: Checking for old CMD patterns..."
! grep -q "^CMD gunicorn.*--bind.*\\\$" Dockerfile
check_result $? "Old shell form CMD has been replaced"

# Test 6: Verify no old HEALTHCHECK format remains
echo "Test 6: Checking for old HEALTHCHECK patterns..."
! grep -q "CMD curl.*\${PORT" Dockerfile | grep -v "sh -c"
check_result $? "Old HEALTHCHECK format has been replaced"

echo ""
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $pass_count${NC}"
echo -e "${RED}Failed: $fail_count${NC}"
echo ""

if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✅${NC}"
    echo ""
    echo "The Docker PORT variable expansion fix is correctly implemented."
    echo "Containers should now start without the '$PORT' is not a valid port number error."
    exit 0
else
    echo -e "${RED}Some tests failed! ❌${NC}"
    echo ""
    echo "Please review the Dockerfile changes."
    exit 1
fi
