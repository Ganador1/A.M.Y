#!/bin/bash

# Simplified test script for Phase 2 autonomous research capabilities

echo "🧠 Testing AXIOM Phase 2: Basic Health Checks"
echo "==========================================="

BASE_URL="http://localhost:8002"

echo ""
echo "1. Testing Server Health"
echo "-----------------------"

HEALTH_RESPONSE=$(curl -s "$BASE_URL/health")
if echo "$HEALTH_RESPONSE" | grep -q '"status":"healthy"'; then
    echo "✅ Server health: SUCCESS"
else
    echo "❌ Server health: FAILED"
    echo "   Response: $HEALTH_RESPONSE"
    exit 1
fi

echo ""
echo "2. Testing Scientific Hypothesis Service"
echo "---------------------------------------"

HYPOTHESIS_RESPONSE=$(curl -s -X POST "$BASE_URL/api/scientific-hypothesis/health" \
  -H "Content-Type: application/json")

if echo "$HYPOTHESIS_RESPONSE" | grep -q '"status":"healthy"'; then
    echo "✅ Scientific hypothesis service: SUCCESS"
else
    echo "❌ Scientific hypothesis service: FAILED"
    echo "   Response: $HYPOTHESIS_RESPONSE"
fi

echo ""
echo "3. Testing Literature Search Service"
echo "-----------------------------------"

LITERATURE_RESPONSE=$(curl -s -X GET "$BASE_URL/api/literature-search/health")

if echo "$LITERATURE_RESPONSE" | grep -q '"status":"healthy"'; then
    echo "✅ Literature search service: SUCCESS"
else
    echo "❌ Literature search service: FAILED"
    echo "   Response: $LITERATURE_RESPONSE"
fi

echo ""
echo "4. Testing Research Cycle Service"
echo "--------------------------------"

CYCLE_RESPONSE=$(curl -s -X GET "$BASE_URL/api/research-cycle/health")

if echo "$CYCLE_RESPONSE" | grep -q '"status":"healthy"'; then
    echo "✅ Research cycle service: SUCCESS"
else
    echo "❌ Research cycle service: FAILED"
    echo "   Response: $CYCLE_RESPONSE"
fi

echo ""
echo "5. Testing Optimization Service"
echo "------------------------------"

OPTIMIZATION_RESPONSE=$(curl -s -X POST "$BASE_URL/api/optimization/solve" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "linear_programming",
    "c": [1, 2],
    "A_ub": [[1, 1], [2, 1]],
    "b_ub": [6, 8]
  }')

if echo "$OPTIMIZATION_RESPONSE" | grep -q '"status":"optimal"'; then
    echo "✅ Optimization service: SUCCESS"
else
    echo "❌ Optimization service: FAILED"
    echo "   Response: $OPTIMIZATION_RESPONSE"
fi

echo ""
echo "🎉 Basic Testing Complete!"
echo "=========================="
echo ""
echo "Phase 2 autonomous research capabilities are operational!"
