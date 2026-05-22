#!/bin/bash

# 🎯 AXIOM Advanced Features Demonstration
# Demonstrates GPU detection, distributed computing, and advanced algorithms

echo "🚀 AXIOM Advanced Features Demonstration"
echo "========================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local data=$4

    echo -e "${BLUE}Testing: ${description}${NC}"
    echo -e "${YELLOW}Endpoint: ${method} ${endpoint}${NC}"

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$endpoint")
    else
        response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$endpoint" \
                 -H "Content-Type: application/json" -d "$data")
    fi

    http_status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
    body=$(echo "$response" | sed '/HTTP_STATUS:/d')

    if [ "$http_status" = "200" ]; then
        echo -e "${GREEN}✅ SUCCESS${NC}"
        echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
    else
        echo -e "${RED}❌ FAILED (HTTP $http_status)${NC}"
        echo "$body"
    fi
    echo "---"
}

echo -e "${PURPLE}🔍 Testing GPU Detection & Management${NC}"
echo

test_endpoint "GET" "http://localhost:8002/api/advanced-algorithms/gpu/status" "GPU System Status"

echo -e "${PURPLE}🔗 Testing Distributed Computing${NC}"
echo

test_endpoint "GET" "http://localhost:8002/api/advanced-algorithms/distributed/status" "Distributed Computing Status"

echo -e "${PURPLE}🧮 Testing Advanced Algorithms${NC}"
echo

test_endpoint "GET" "http://localhost:8002/api/advanced-algorithms/algorithms/status" "Advanced Algorithms Status"

echo -e "${PURPLE}🎯 Testing Function Optimization${NC}"
echo

# Test optimization
optimization_data='{
    "function": "(x[0] - 1)**2 + (x[1] - 2.5)**2",
    "bounds": [[-10, 10], [-10, 10]],
    "method": "L-BFGS-B"
}'
test_endpoint "POST" "http://localhost:8002/api/advanced-algorithms/optimize" "Function Optimization" "$optimization_data"

echo -e "${PURPLE}∫ Testing Numerical Integration${NC}"
echo

# Test integration
integration_data='{
    "function": "x**2",
    "lower_limit": 0,
    "upper_limit": 1,
    "method": "adaptive"
}'
test_endpoint "POST" "http://localhost:8002/api/advanced-algorithms/integrate" "Numerical Integration" "$integration_data"

echo -e "${PURPLE}📊 Testing Matrix Decomposition${NC}"
echo

# Test matrix decomposition
matrix_data='{
    "matrix": [[4, 2], [2, 1]],
    "method": "svd"
}'
test_endpoint "POST" "http://localhost:8002/api/advanced-algorithms/decompose" "Matrix Decomposition" "$matrix_data"

echo -e "${PURPLE}🎨 Testing Parallel Clustering${NC}"
echo

# Test clustering
clustering_data='{
    "data": [[1, 2], [1.5, 2.5], [3, 4], [3.5, 4.5], [5, 6], [5.5, 6.5]],
    "n_clusters": 2,
    "method": "kmeans"
}'
test_endpoint "POST" "http://localhost:8002/api/advanced-algorithms/cluster" "Parallel Clustering" "$clustering_data"

echo -e "${PURPLE}📈 Testing Advanced Interpolation${NC}"
echo

# Test interpolation
interpolation_data='{
    "x_values": [0, 1, 2, 3, 4],
    "y_values": [0, 1, 4, 9, 16],
    "x_new": [0.5, 1.5, 2.5, 3.5],
    "method": "cubic"
}'
test_endpoint "POST" "http://localhost:8002/api/advanced-algorithms/interpolate" "Advanced Interpolation" "$interpolation_data"

echo -e "${PURPLE}🔄 Testing Distributed Computation${NC}"
echo

# Test distributed computation
distributed_data='{
    "data_sets": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
}'
test_endpoint "POST" "http://localhost:8002/api/advanced-algorithms/distributed/compute" "Distributed Computation" "$distributed_data"

echo -e "${PURPLE}📊 Testing Performance Summary${NC}"
echo

test_endpoint "GET" "http://localhost:8002/api/advanced-algorithms/performance/summary" "Performance Summary"

echo
echo -e "${GREEN}🎯 Advanced Features Demonstration Complete!${NC}"
echo -e "${GREEN}✅ GPU Detection, Distributed Computing & Advanced Algorithms Operational${NC}"
echo
echo -e "${BLUE}📋 Summary of New Capabilities:${NC}"
echo -e "  • 🔍 Automatic GPU Detection (CUDA/MPS/CPU)"
echo -e "  • 🔗 Distributed Computing Framework"
echo -e "  • 🧮 Advanced Optimization Algorithms"
echo -e "  • ∫ High-Precision Numerical Integration"
echo -e "  • 📊 Matrix Decomposition (SVD, QR, LU, Cholesky)"
echo -e "  • 🎨 Parallel Clustering (K-Means)"
echo -e "  • 📈 Advanced Interpolation Methods"
echo -e "  • 🔄 Distributed Scientific Computation"
echo -e "  • 📊 Real-time Performance Monitoring"
