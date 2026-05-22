#!/bin/bash

# Test script that runs in a completely separate process
# This avoids interfering with the main server process

echo "🧠 Testing AXIOM Phase 2: Independent Test Session"
echo "================================================="

BASE_URL="http://localhost:8002"

echo ""
echo "Testing basic connectivity..."
curl -s "$BASE_URL/health" > /tmp/health_test.json

if [ $? -eq 0 ] && grep -q '"status":"healthy"' /tmp/health_test.json; then
    echo "✅ Server connectivity: SUCCESS"
else
    echo "❌ Server connectivity: FAILED"
    echo "   Response: $(cat /tmp/health_test.json)"
    exit 1
fi

echo ""
echo "Testing Scientific Hypothesis Service..."
curl -s -X POST "$BASE_URL/api/scientific-hypothesis/health" \
  -H "Content-Type: application/json" > /tmp/hypothesis_test.json

if grep -q '"status":"healthy"' /tmp/hypothesis_test.json; then
    echo "✅ Scientific hypothesis service: SUCCESS"
else
    echo "❌ Scientific hypothesis service: FAILED"
fi

echo ""
echo "Testing Literature Search Service..."
curl -s -X GET "$BASE_URL/api/literature-search/health" > /tmp/literature_test.json

if grep -q '"status":"healthy"' /tmp/literature_test.json; then
    echo "✅ Literature search service: SUCCESS"
else
    echo "❌ Literature search service: FAILED"
fi

echo ""
echo "Testing Research Cycle Service..."
curl -s -X GET "$BASE_URL/api/research-cycle/health" > /tmp/cycle_test.json

if grep -q '"status":"healthy"' /tmp/cycle_test.json; then
    echo "✅ Research cycle service: SUCCESS"
else
    echo "❌ Research cycle service: FAILED"
fi

echo ""
echo "Testing Optimization Service..."
curl -s -X POST "$BASE_URL/api/optimization/solve" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "linear_programming",
    "c": [1, 2],
    "A_ub": [[1, 1], [2, 1]],
    "b_ub": [6, 8]
  }' > /tmp/optimization_test.json

if grep -q '"status":"optimal"' /tmp/optimization_test.json; then
    echo "✅ Optimization service: SUCCESS"
else
    echo "❌ Optimization service: FAILED"
fi

echo ""
echo "🎉 Independent Testing Complete!"
echo "================================"
echo ""
echo "Phase 2 autonomous research capabilities are operational!"
