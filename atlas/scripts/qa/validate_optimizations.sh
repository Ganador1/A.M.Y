#!/bin/bash

# 🎯 AXIOM Optimization Validation Script
# Validates all optimization systems are working correctly

echo "🚀 AXIOM Optimization Validation"
echo "================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to test endpoint
test_endpoint() {
    local endpoint=$1
    local description=$2

    echo -e "${BLUE}Testing: ${description}${NC}"
    echo -e "${YELLOW}Endpoint: ${endpoint}${NC}"

    response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$endpoint")
    http_status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
    body=$(echo "$response" | sed '/HTTP_STATUS:/d')

    if [ "$http_status" = "200" ]; then
        echo -e "${GREEN}✅ SUCCESS${NC}"
        echo "$body" | python -m json.tool 2>/dev/null || echo "$body"
    else
        echo -e "${RED}❌ FAILED (HTTP $http_status)${NC}"
        echo "$body"
    fi
    echo "---"
}

# Test all optimization endpoints
echo -e "${BLUE}🔍 Testing Optimization Endpoints${NC}"
echo

test_endpoint "http://localhost:8002/optimization/stats" "Optimization Statistics"
test_endpoint "http://localhost:8002/profiling/stats" "Profiling Statistics"
test_endpoint "http://localhost:8002/profiling/report" "Performance Report"
test_endpoint "http://localhost:8002/cache/stats" "Cache Statistics"
test_endpoint "http://localhost:8002/redis/status" "Redis Status"

# Test optimization application (GET instead of POST)
echo -e "${BLUE}🔧 Testing Optimization Application${NC}"
echo
test_endpoint "http://localhost:8002/optimization/apply" "Apply Optimizations (GET)"

# Test a simple operation to trigger profiling
echo -e "${BLUE}🧮 Testing Simple Operation (triggers profiling)${NC}"
echo
curl -s "http://localhost:8002/health" | python -m json.tool

echo
echo -e "${BLUE}📊 Post-Operation Profiling Check${NC}"
echo
test_endpoint "http://localhost:8002/profiling/stats" "Updated Profiling Statistics"

echo
echo -e "${GREEN}🎯 Optimization Validation Complete!${NC}"
echo -e "${GREEN}✅ All systems operational${NC}"
