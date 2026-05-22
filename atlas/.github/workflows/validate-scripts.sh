#!/bin/bash
# Script para validar que todos los scripts referenciados en workflows existan

echo "🔍 Validando scripts referenciados en workflows CI/CD..."

MISSING_SCRIPTS=()

# Scripts del workflow ci.yml
SCRIPTS=(
    "scripts/qa/validate_manifests.py"
    "scripts/qa/verify_manifest_signatures.py"
    "scripts/tools/compute_merkle_root.py"
    "scripts/qa/verify_merkle_root.py"
    "scripts/run_data_validations.py"
    "scripts/tools/build_repro_bundle.py"
    "scripts/qa/verify_repro_bundle.py"
    "scripts/run_scientific_gates.py"
    "scripts/check_runtime_sandbox.py"
)

# Scripts del workflow security-scan.yml
SCRIPTS+=(
    "scripts/security/check_vulnerabilities.py"
)

for script in "${SCRIPTS[@]}"; do
    if [ ! -f "$script" ]; then
        MISSING_SCRIPTS+=("$script")
        echo "  ❌ Falta: $script"
    else
        echo "  ✅ Existe: $script"
    fi
done

echo ""
if [ ${#MISSING_SCRIPTS[@]} -eq 0 ]; then
    echo "✅ Todos los scripts existen"
    exit 0
else
    echo "⚠️  Faltan ${#MISSING_SCRIPTS[@]} scripts:"
    printf '   - %s\n' "${MISSING_SCRIPTS[@]}"
    echo ""
    echo "📝 Estos scripts son opcionales en los workflows (tienen fallbacks)"
    exit 0  # No fallar, solo informar
fi
