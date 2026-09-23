#!/bin/bash

# Test script for Phase 2: IA Meta-Científica (Q1 2026)
# Tests autonomous hypothesis generation, literature search, and research cycle management

echo "🧠 Testing AXIOM Phase 2: IA Meta-Científica"
echo "=========================================="

BASE_URL="http://localhost:8002"
TEST_DOMAIN="materials_science"
TEST_QUESTION="How to improve thermal conductivity in composite materials?"

echo ""
echo "1. Testing Scientific Hypothesis Agent"
echo "--------------------------------------"

# Test hypothesis generation
echo "Generating hypothesis..."
HYPOTHESIS_RESPONSE=$(curl -s -X POST "$BASE_URL/api/scientific-hypothesis/generate-hypothesis" \
  -H "Content-Type: application/json" \
  -d "{
    \"domain\": \"$TEST_DOMAIN\",
    \"research_question\": \"$TEST_QUESTION\"
  }")

if echo "$HYPOTHESIS_RESPONSE" | grep -q '"success":true'; then
    echo "✅ Hypothesis generation: SUCCESS"
    HYPOTHESIS_ID=$(echo "$HYPOTHESIS_RESPONSE" | grep -o '"hypothesis_id":"[^"]*"' | cut -d'"' -f4)
    echo "   Generated hypothesis ID: $HYPOTHESIS_ID"
else
    echo "❌ Hypothesis generation: FAILED"
    echo "   Response: $HYPOTHESIS_RESPONSE"
fi

echo ""
echo "2. Testing Literature Search Service"
echo "------------------------------------"

# Test literature search
echo "Searching literature..."
LITERATURE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/literature-search/search-literature" \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"$TEST_QUESTION\",
    \"domain\": \"$TEST_DOMAIN\",
    \"max_results\": 5
  }")

if echo "$LITERATURE_RESPONSE" | grep -q '"success":true'; then
    echo "✅ Literature search: SUCCESS"
    PAPER_COUNT=$(echo "$LITERATURE_RESPONSE" | grep -o '"relevant_found":[0-9]*' | cut -d':' -f2)
    echo "   Found $PAPER_COUNT relevant papers"
else
    echo "❌ Literature search: FAILED"
    echo "   Response: $LITERATURE_RESPONSE"
fi

echo ""
echo "3. Testing Research Cycle Manager"
echo "----------------------------------"

# Test research cycle start
echo "Starting research cycle..."
CYCLE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/research-cycle/start-cycle" \
  -H "Content-Type: application/json" \
  -d "{
    \"research_question\": \"$TEST_QUESTION\",
    \"domain\": \"$TEST_DOMAIN\",
    \"max_iterations\": 3
  }")

if echo "$CYCLE_RESPONSE" | grep -q '"success":true'; then
    echo "✅ Research cycle start: SUCCESS"
    CYCLE_ID=$(echo "$CYCLE_RESPONSE" | grep -o '"cycle_id":"[^"]*"' | cut -d'"' -f4)
    echo "   Started cycle ID: $CYCLE_ID"
else
    echo "❌ Research cycle start: FAILED"
    echo "   Response: $CYCLE_RESPONSE"
fi

echo ""
echo "4. Testing Service Health Checks"
echo "---------------------------------"

# Test all new service health endpoints
SERVICES=(
    "scientific-hypothesis"
    "literature-search"
    "research-cycle"
)

for service in "${SERVICES[@]}"; do
    echo "Checking $service health..."
    HEALTH_RESPONSE=$(curl -s "$BASE_URL/api/$service/health")

    if echo "$HEALTH_RESPONSE" | grep -q '"status":"healthy"'; then
        echo "✅ $service health: SUCCESS"
    else
        echo "❌ $service health: FAILED"
        echo "   Response: $HEALTH_RESPONSE"
    fi
done

echo ""
echo "5. Testing Service Statistics"
echo "-----------------------------"

# Test service statistics
for service in "${SERVICES[@]}"; do
    echo "Getting $service statistics..."
    STATS_RESPONSE=$(curl -s "$BASE_URL/api/$service/stats")

    if echo "$STATS_RESPONSE" | grep -q '"service":'; then
        echo "✅ $service stats: SUCCESS"
    else
        echo "❌ $service stats: FAILED"
        echo "   Response: $STATS_RESPONSE"
    fi
done

echo ""
echo "6. Testing Integration Scenarios"
echo "---------------------------------"

# Test hypothesis refinement (if hypothesis was generated)
if [ -n "$HYPOTHESIS_ID" ]; then
    echo "Testing hypothesis refinement..."
    REFINE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/scientific-hypothesis/refine-hypothesis" \
      -H "Content-Type: application/json" \
      -d "{
        \"hypothesis_id\": \"$HYPOTHESIS_ID\",
        \"refinement_data\": {
          \"new_variables\": [\"temperature_range\"],
          \"confidence_adjustment\": 0.1
        }
      }")

    if echo "$REFINE_RESPONSE" | grep -q '"success":true'; then
        echo "✅ Hypothesis refinement: SUCCESS"
    else
        echo "❌ Hypothesis refinement: FAILED"
        echo "   Response: $REFINE_RESPONSE"
    fi
fi

# Test literature review generation
echo "Testing literature review generation..."
REVIEW_RESPONSE=$(curl -s -X POST "$BASE_URL/api/literature-search/generate-literature-review" \
  -H "Content-Type: application/json" \
  -d "{
    \"topic\": \"$TEST_QUESTION\",
    \"domain\": \"$TEST_DOMAIN\",
    \"max_papers\": 3
  }")

if echo "$REVIEW_RESPONSE" | grep -q '"success":true'; then
    echo "✅ Literature review generation: SUCCESS"
else
    echo "❌ Literature review generation: FAILED"
    echo "   Response: $REVIEW_RESPONSE"
fi

# Test cycle status (if cycle was started)
if [ -n "$CYCLE_ID" ]; then
    echo "Testing research cycle status..."
    STATUS_RESPONSE=$(curl -s "$BASE_URL/api/research-cycle/cycle/$CYCLE_ID/status")

    if echo "$STATUS_RESPONSE" | grep -q '"success":true'; then
        echo "✅ Research cycle status: SUCCESS"
        STATUS=$(echo "$STATUS_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        PROGRESS=$(echo "$STATUS_RESPONSE" | grep -o '"progress":[0-9.]*' | cut -d':' -f2)
        echo "   Status: $STATUS, Progress: $PROGRESS"
    else
        echo "❌ Research cycle status: FAILED"
        echo "   Response: $STATUS_RESPONSE"
    fi
fi

echo ""
echo "7. Testing Supported Domains"
echo "----------------------------"

# Test domain information
echo "Getting supported domains for research cycles..."
DOMAINS_RESPONSE=$(curl -s "$BASE_URL/api/research-cycle/domains")

if echo "$DOMAINS_RESPONSE" | grep -q '"domains":'; then
    echo "✅ Research cycle domains: SUCCESS"
    DOMAIN_COUNT=$(echo "$DOMAINS_RESPONSE" | grep -o '"name":"[^"]*"' | wc -l)
    echo "   Found $DOMAIN_COUNT supported domains"
else
    echo "❌ Research cycle domains: FAILED"
    echo "   Response: $DOMAINS_RESPONSE"
fi

echo ""
echo "8. Testing Active Cycles"
echo "------------------------"

# Test active cycles listing
echo "Getting active research cycles..."
ACTIVE_RESPONSE=$(curl -s "$BASE_URL/api/research-cycle/active-cycles")

if echo "$ACTIVE_RESPONSE" | grep -q '"success":true'; then
    echo "✅ Active cycles: SUCCESS"
    ACTIVE_COUNT=$(echo "$ACTIVE_RESPONSE" | grep -o '"count":[0-9]*' | cut -d':' -f2)
    echo "   Active cycles: $ACTIVE_COUNT"
else
    echo "❌ Active cycles: FAILED"
    echo "   Response: $ACTIVE_RESPONSE"
fi

echo ""
echo "9. Performance and Load Testing"
echo "-------------------------------"

# Quick performance test
echo "Running performance test (5 concurrent requests)..."
START_TIME=$(date +%s.%3N)

# Run 5 concurrent requests
for i in {1..5}; do
    curl -s "$BASE_URL/api/scientific-hypothesis/health" > /dev/null &
    curl -s "$BASE_URL/api/literature-search/health" > /dev/null &
    curl -s "$BASE_URL/api/research-cycle/health" > /dev/null &
done
wait

END_TIME=$(date +%s.%3N)
ELAPSED=$(echo "$END_TIME - $START_TIME" | bc)

echo "✅ Performance test completed in ${ELAPSED}s"

echo ""
echo "10. Final Validation"
echo "-------------------"

# Check overall system health
echo "Checking overall system health..."
HEALTH_RESPONSE=$(curl -s "$BASE_URL/health")

if echo "$HEALTH_RESPONSE" | grep -q '"status":"healthy"'; then
    echo "✅ Overall system health: SUCCESS"
else
    echo "❌ Overall system health: FAILED"
    echo "   Response: $HEALTH_RESPONSE"
fi

echo ""
echo "🎉 Phase 2 Testing Complete!"
echo "============================"
echo ""
echo "Summary of Phase 2 Capabilities:"
echo "• 🤖 Autonomous hypothesis generation"
echo "• 📚 Intelligent literature search and analysis"
echo "• 🔄 Closed-loop research cycle management"
echo "• 🧪 Multi-domain scientific research support"
echo "• 📊 Real-time experiment tracking and refinement"
echo "• 🔬 Integration with existing scientific services"
echo ""
echo "Next Steps:"
echo "• Monitor research cycles in real-time"
echo "• Analyze hypothesis quality and refinement patterns"
echo "• Expand domain coverage and workflow templates"
echo "• Implement advanced AI-driven optimization"
echo ""
echo "🚀 Ready for Phase 3: Advanced Workflows (Q2 2026)!"
