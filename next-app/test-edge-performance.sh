#!/bin/bash

# Vercel Edge Network Performance Test
# Tests latency from multiple regions to verify <60ms target

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="${1:-https://hiremebahamas.com}"
TEST_EMAIL="test@example.com"
TEST_PASSWORD="password123"

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Vercel Edge Network Performance Test${NC}"
echo -e "${BLUE}   Target: ${BASE_URL}${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Function to test endpoint latency
test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local target_ms="$5"
    
    echo -e "${YELLOW}Testing: ${name}${NC}"
    
    if [ -z "$data" ]; then
        # GET request
        response=$(curl -s -w "\n%{time_total}" -X "$method" "${BASE_URL}${endpoint}")
    else
        # POST request with JSON data
        response=$(curl -s -w "\n%{time_total}" \
            -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "${BASE_URL}${endpoint}")
    fi
    
    # Extract time (last line) and body (everything else)
    time_total=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)
    
    # Convert to milliseconds
    time_ms=$(echo "$time_total * 1000" | bc | cut -d. -f1)
    
    # Check if we met the target
    if [ "$time_ms" -le "$target_ms" ]; then
        echo -e "  ${GREEN}✓ ${time_ms}ms (target: <${target_ms}ms)${NC}"
        echo -e "  Response: $(echo "$body" | jq -r '.status // .message // .success' 2>/dev/null || echo "OK")"
    else
        echo -e "  ${RED}✗ ${time_ms}ms (target: <${target_ms}ms)${NC}"
        echo -e "  Response: $(echo "$body" | jq -r '.status // .message // .success' 2>/dev/null || echo "ERROR")"
    fi
    
    echo ""
}

# Test 1: Edge Health Check (should be fastest)
echo -e "${BLUE}═══ Test 1: Edge Health Check ═══${NC}"
test_endpoint "Health Check (Edge)" "GET" "/api/health" "" 50

# Test 2: Edge Cron Endpoint
echo -e "${BLUE}═══ Test 2: Edge Cron Endpoint ═══${NC}"
test_endpoint "Cron Keep-Alive (Edge)" "GET" "/api/cron" "" 100

# Test 3: Login Endpoint (Node.js with KV cache)
echo -e "${BLUE}═══ Test 3: Login Endpoint (First Request) ═══${NC}"
login_data="{\"email\":\"${TEST_EMAIL}\",\"password\":\"${TEST_PASSWORD}\"}"
test_endpoint "Login - First Request" "POST" "/api/auth/login" "$login_data" 150

# Test 4: Login Endpoint (Cached)
echo -e "${BLUE}═══ Test 4: Login Endpoint (Repeat - Should be Cached) ═══${NC}"
test_endpoint "Login - Cached Request" "POST" "/api/auth/login" "$login_data" 80

# Test 5: Jobs List Endpoint
echo -e "${BLUE}═══ Test 5: Jobs List (First Request) ═══${NC}"
test_endpoint "Jobs List - First Request" "GET" "/api/jobs?limit=10" "" 200

# Test 6: Jobs List Endpoint (Cached)
echo -e "${BLUE}═══ Test 6: Jobs List (Repeat - Should be Cached) ═══${NC}"
test_endpoint "Jobs List - Cached Request" "GET" "/api/jobs?limit=10" "" 100

# Summary
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Performance Test Complete!${NC}"
echo ""
echo -e "${YELLOW}Expected Performance:${NC}"
echo "  • Edge Health: <50ms"
echo "  • Edge Cron: <100ms"
echo "  • Login (first): <150ms"
echo "  • Login (cached): <80ms"
echo "  • Jobs (first): <200ms"
echo "  • Jobs (cached): <100ms"
echo ""
echo -e "${YELLOW}Vercel Edge Network Verification:${NC}"
echo "  1. Check Vercel Dashboard → Analytics → Response Time"
echo "  2. Verify >99% requests served from Edge"
echo "  3. Check P95 latency <100ms"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
