#!/bin/bash
# Script automatizado para ejecutar Phase 8.4 sin input manual

cd "/Volumes/Ganador disk/atlas"

echo "🚀 Iniciando Phase 8.4 - Quantum Loop con HuggingFace API"
echo "================================================"
echo ""

# Simular ENTER al principio
echo "" | .venv/bin/python run_model_comparison_phase8.py --domains quantum 2>&1 | tee phase8_4_quantum_only.log

echo ""
echo "✅ Ejecución completada. Ver resultados en:"
echo "   - phase8_4_quantum_only.log"
echo "   - model_comparison_phase8_*.json"
