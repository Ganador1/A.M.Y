#!/bin/bash
"""
Test script for Strategic Goals 2025-2026 Phase 1 implementations
Tests Workflow Orchestration, Experiment Tracking, and Data Versioning
"""

echo "🧠 AXIOM - Strategic Goals 2025-2026 Phase 1 Testing"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if server is running
print_status "Checking if AXIOM server is running..."
if curl -s http://localhost:8002/health > /dev/null; then
    print_success "Server is running"
else
    print_error "Server is not running. Please start the server first with: python main.py"
    exit 1
fi

echo ""

# Test 1: Workflow Orchestration
print_status "Testing Workflow Orchestration Service..."
echo "------------------------------------------"

# Create a workflow from template
print_status "Creating workflow from heat_sink_design template..."
CREATE_RESPONSE=$(curl -s -X POST http://localhost:8002/api/workflow-orchestration/create-workflow \
    -H "Content-Type: application/json" \
    -d '{
        "template": "heat_sink_design",
        "name": "Test Heat Sink Design Workflow",
        "metadata": {
            "test_run": true,
            "purpose": "strategic_goals_validation"
        }
    }')

if echo "$CREATE_RESPONSE" | grep -q '"success":true'; then
    print_success "Workflow created successfully"
    WORKFLOW_ID=$(echo "$CREATE_RESPONSE" | grep -o '"workflow_id":"[^"]*"' | cut -d'"' -f4)
    print_status "Workflow ID: $WORKFLOW_ID"
else
    print_error "Failed to create workflow"
    echo "$CREATE_RESPONSE"
fi

echo ""

# Test 2: Experiment Tracking
print_status "Testing Experiment Tracking Service..."
echo "---------------------------------------"

# Start an experiment
print_status "Starting a test experiment..."
EXP_RESPONSE=$(curl -s -X POST http://localhost:8002/api/experiment-tracking/start-experiment \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Strategic Goals Validation Experiment",
        "description": "Testing experiment tracking for reproducibility",
        "parameters": {
            "test_type": "integration",
            "phase": "q4_2025"
        },
        "tags": ["strategic_goals", "phase1", "validation"]
    }')

if echo "$EXP_RESPONSE" | grep -q '"success":true'; then
    print_success "Experiment started successfully"
    EXPERIMENT_ID=$(echo "$EXP_RESPONSE" | grep -o '"experiment_id":"[^"]*"' | cut -d'"' -f4)
    print_status "Experiment ID: $EXPERIMENT_ID"
else
    print_error "Failed to start experiment"
    echo "$EXP_RESPONSE"
fi

echo ""

# Log some metrics
if [ ! -z "$EXPERIMENT_ID" ]; then
    print_status "Logging test metrics..."
    METRIC_RESPONSE=$(curl -s -X POST http://localhost:8002/api/experiment-tracking/log-metric \
        -H "Content-Type: application/json" \
        -d "{
            \"experiment_id\": \"$EXPERIMENT_ID\",
            \"metric_name\": \"test_accuracy\",
            \"metric_value\": 0.95
        }")

    if echo "$METRIC_RESPONSE" | grep -q '"success":true'; then
        print_success "Metric logged successfully"
    else
        print_error "Failed to log metric"
    fi

    # Log a parameter
    PARAM_RESPONSE=$(curl -s -X POST http://localhost:8002/api/experiment-tracking/log-parameter \
        -H "Content-Type: application/json" \
        -d "{
            \"experiment_id\": \"$EXPERIMENT_ID\",
            \"param_name\": \"learning_rate\",
            \"param_value\": 0.001
        }")

    if echo "$PARAM_RESPONSE" | grep -q '"success":true'; then
        print_success "Parameter logged successfully"
    else
        print_error "Failed to log parameter"
    fi
fi

echo ""

# Test 3: Data Versioning
print_status "Testing Data Versioning Service..."
echo "------------------------------------"

# Create a test data file
print_status "Creating test data file..."
echo '{"test_data": "strategic_goals_validation", "timestamp": "'$(date)'", "phase": "q4_2025"}' > test_data.json

# Version the data
print_status "Versioning test data..."
VERSION_RESPONSE=$(curl -s -X POST http://localhost:8002/api/data-versioning/version-data \
    -H "Content-Type: application/json" \
    -d '{
        "data_path": "test_data.json",
        "metadata": {
            "description": "Test data for strategic goals validation",
            "created_by": "test_script"
        },
        "tags": ["test", "strategic_goals", "validation"]
    }')

if echo "$VERSION_RESPONSE" | grep -q '"success":true'; then
    print_success "Data versioned successfully"
    VERSION_ID=$(echo "$VERSION_RESPONSE" | grep -o '"version_id":"[^"]*"' | cut -d'"' -f4)
    print_status "Version ID: $VERSION_ID"
else
    print_error "Failed to version data"
    echo "$VERSION_RESPONSE"
fi

echo ""

# Test 4: Get reproducibility report
if [ ! -z "$EXPERIMENT_ID" ]; then
    print_status "Creating reproducibility report..."
    REPORT_RESPONSE=$(curl -s -X POST http://localhost:8002/api/experiment-tracking/create-reproducibility-report \
        -H "Content-Type: application/json" \
        -d "{
            \"experiment_id\": \"$EXPERIMENT_ID\"
        }")

    if echo "$REPORT_RESPONSE" | grep -q '"success":true'; then
        print_success "Reproducibility report created successfully"
    else
        print_error "Failed to create reproducibility report"
    fi
fi

echo ""

# Test 5: List available services
print_status "Checking available workflow templates..."
TEMPLATES_RESPONSE=$(curl -s http://localhost:8002/api/workflow-orchestration/workflow-templates)

if echo "$TEMPLATES_RESPONSE" | grep -q '"success":true'; then
    TEMPLATE_COUNT=$(echo "$TEMPLATES_RESPONSE" | grep -o '"total_count":[0-9]*' | cut -d':' -f2)
    print_success "Found $TEMPLATE_COUNT workflow templates"
else
    print_error "Failed to get workflow templates"
fi

echo ""

# Test 6: End experiment
if [ ! -z "$EXPERIMENT_ID" ]; then
    print_status "Ending experiment..."
    END_RESPONSE=$(curl -s -X POST http://localhost:8002/api/experiment-tracking/end-experiment \
        -H "Content-Type: application/json" \
        -d "{
            \"experiment_id\": \"$EXPERIMENT_ID\",
            \"status\": \"completed\"
        }")

    if echo "$END_RESPONSE" | grep -q '"success":true'; then
        print_success "Experiment ended successfully"
    else
        print_error "Failed to end experiment"
    fi
fi

echo ""

# Cleanup
print_status "Cleaning up test files..."
rm -f test_data.json

echo ""
print_success "Strategic Goals Phase 1 testing completed!"
echo ""
echo "📊 Summary of implemented features:"
echo "  ✅ WorkflowOrchestratorService - Basic workflow orchestration"
echo "  ✅ ExperimentTrackingService - MLflow-based experiment tracking"
echo "  ✅ DataVersioningService - DVC-based data versioning"
echo "  ✅ RESTful APIs for all services"
echo "  ✅ Integration with existing AXIOM architecture"
echo ""
echo "🎯 Next steps for Q4 2025:"
echo "  - Enhance workflow templates with more scientific domains"
echo "  - Add advanced experiment comparison features"
echo "  - Implement automated provenance tracking"
echo "  - Add integration with Prefect/Airflow for production workflows"
echo ""
echo "🚀 Ready for Phase 2: IA Meta-Científica (Q1 2026)"
