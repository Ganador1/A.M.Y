#!/bin/bash
# Script para procesar múltiples routers en batch
# Usage: bash scripts/maintenance/batch_process_routers.sh

set -e

# Lista de routers a procesar (ordenados por prioridad)
routers=(
    "synthetic_data.py"
    "stress_testing.py"
    "multimodal_reasoning.py"
    "advanced_cloud_lab.py"
    "literature_search.py"
    "experimental_toolkit.py"
    "metrics.py"
    "massive_automl.py"
    "iterative_improvement.py"
    "federated_learning.py"
    "workflow_orchestration.py"
    "performance_profiler.py"
    "advanced_nmr.py"
    "system.py"
    "scalability.py"
    "experiment_scheduler.py"
    "security.py"
    "publications.py"
    "neuroscience_light.py"
    "mathematical_verification_router.py"
)

echo "=========================================="
echo "Batch Processing Type Hints - Phase 2"
echo "=========================================="
echo ""
echo "Processing ${#routers[@]} routers..."
echo ""

processed=0
skipped=0
errors=0

for router in "${routers[@]}"; do
    echo "----------------------------------------"
    echo "Processing: $router"
    echo "----------------------------------------"

    if python3 scripts/maintenance/quick_fix_dict_any.py \
        --file "app/routers/$router" \
        --execute 2>&1 | grep -q "Created:"; then

        echo "✅ Successfully processed $router"
        ((processed++))
    elif python3 scripts/maintenance/quick_fix_dict_any.py \
        --file "app/routers/$router" \
        --execute 2>&1 | grep -q "No functions"; then

        echo "⏭️  Skipped $router (no Dict[str, Any] in returns)"
        ((skipped++))
    else
        echo "❌ Error processing $router"
        ((errors++))
    fi

    echo ""
done

echo "=========================================="
echo "Batch Processing Complete"
echo "=========================================="
echo ""
echo "Summary:"
echo "  Processed: $processed"
echo "  Skipped:   $skipped"
echo "  Errors:    $errors"
echo "  Total:     ${#routers[@]}"
echo ""
echo "Next steps:"
echo "  1. Review generated TypedDicts in app/types/"
echo "  2. Run: python3 scripts/maintenance/measure_type_hint_improvement.py"
echo "  3. Run: mypy app/routers/ --show-error-codes"
echo ""
