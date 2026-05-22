#!/usr/bin/env bash
#
# Ejecución Batch de Loops en Producción
# ========================================
#
# Ejecuta todos los loops disponibles secuencialmente
# y recopila resultados en production_results/
#

set -euo pipefail

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}"
echo "========================================"
echo "  AXIOM ATLAS - Production Loops Batch  "
echo "========================================"
echo -e "${NC}"

PYTHON_BIN=".venv_new/bin/python3"
SCRIPT="run_production_loops_simple.py"

# Verificar script existe
if [ ! -f "$SCRIPT" ]; then
    echo -e "${RED}❌ Script $SCRIPT no encontrado${NC}"
    exit 1
fi

# Crear directorio de resultados
mkdir -p production_results

# Loops disponibles
LOOPS=("quantum" "biology" "chemistry" "materials" "mathematics")

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
SUMMARY_FILE="production_results/batch_summary_${TIMESTAMP}.txt"

echo -e "${YELLOW}📋 Loops a ejecutar: ${#LOOPS[@]}${NC}"
echo ""

# Ejecutar cada loop
for loop in "${LOOPS[@]}"; do
    echo -e "${GREEN}🚀 Ejecutando: $loop${NC}"
    echo "   Inicio: $(date '+%H:%M:%S')"
    
    # Ejecutar y capturar salida
    if $PYTHON_BIN "$SCRIPT" --loop "$loop" > "production_results/${loop}_${TIMESTAMP}.log" 2>&1; then
        echo -e "   ✅ Completado"
        
        # Extraer métricas del resultado JSON (capitalizar primera letra)
        loop_capitalized=$(echo "${loop:0:1}" | tr '[:lower:]' '[:upper:]')$(echo "${loop:1}")
        JSON_FILE=$(ls -t production_results/${loop_capitalized}Loop_*.json 2>/dev/null | head -1)
        if [ -f "$JSON_FILE" ]; then
            echo "   📊 Resultados:"
            
            # Usar python para extraer métricas
            $PYTHON_BIN -c "
import json
import sys
try:
    with open('$JSON_FILE') as f:
        data = json.load(f)
    if 'metrics' in data:
        m = data['metrics']
        print(f\"      Support Score: {m.get('avg_support_score', 0):.3f}\")
        print(f\"      Novedad: {m.get('avg_novelty', 0):.3f}\")
        print(f\"      Seleccionados: {m.get('selected', 0)}\")
except Exception as e:
    print(f\"      Error leyendo métricas: {e}\", file=sys.stderr)
"
        fi
    else
        echo -e "   ${RED}❌ Error${NC}"
    fi
    
    echo "   Fin: $(date '+%H:%M:%S')"
    echo ""
    
    # Pausa entre loops
    sleep 2
done

echo -e "${GREEN}"
echo "========================================"
echo "  Batch Completado"
echo "========================================"
echo -e "${NC}"

# Generar resumen
echo "📊 Generando resumen..."
echo "AXIOM ATLAS - Production Loops Batch Results" > "$SUMMARY_FILE"
echo "=============================================" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"
echo "Timestamp: $(date)" >> "$SUMMARY_FILE"
echo "Loops ejecutados: ${#LOOPS[@]}" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"

# Agregar estadísticas de cada loop
for loop in "${LOOPS[@]}"; do
    echo "Loop: $loop" >> "$SUMMARY_FILE"
    
    loop_capitalized=$(echo "${loop:0:1}" | tr '[:lower:]' '[:upper:]')$(echo "${loop:1}")
    JSON_FILE=$(ls -t production_results/${loop_capitalized}Loop_*.json 2>/dev/null | head -1)
    if [ -f "$JSON_FILE" ]; then
        $PYTHON_BIN -c "
import json
with open('$JSON_FILE') as f:
    data = json.load(f)
print(f\"  Success: {data.get('success', False)}\")
if 'metrics' in data:
    m = data['metrics']
    print(f\"  Support Score: {m.get('avg_support_score', 0):.3f}\")
    print(f\"  Novedad: {m.get('avg_novelty', 0):.3f}\")
    print(f\"  Seleccionados: {m.get('selected', 0)}\")
if 'elapsed_seconds' in data:
    print(f\"  Tiempo: {data['elapsed_seconds']:.1f}s\")
" >> "$SUMMARY_FILE"
    else
        echo "  No result file found" >> "$SUMMARY_FILE"
    fi
    echo "" >> "$SUMMARY_FILE"
done

echo ""
echo -e "${GREEN}✅ Resumen guardado en: $SUMMARY_FILE${NC}"
echo ""
echo "📂 Archivos generados:"
ls -lh production_results/*_${TIMESTAMP}* 2>/dev/null || echo "  (ninguno)"

echo ""
echo -e "${YELLOW}🎯 Ver resultados detallados:${NC}"
echo "   cat $SUMMARY_FILE"
