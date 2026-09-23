#!/bin/bash
# Monitor test_all_autonomous_loops.py execution

LOG_FILE="./test_output.log"
RESULT_FILE="./test_all_loops_results.json"

echo "🔍 Monitoreando test E2E - iniciado $(date)"
echo ""

while true; do
    # Check if process is still running
    if ! ps aux | grep "test_all_autonomous_loops.py" | grep python | grep -v grep > /dev/null; then
        echo "✅ Proceso terminado - $(date)"
        echo ""
        
        # Check results
        if [ -f "$RESULT_FILE" ]; then
            echo "✅ Archivo de resultados generado:"
            ls -lh "$RESULT_FILE"
            echo ""
            echo "📊 Resumen:"
            cat "$RESULT_FILE" | jq -r '.timestamp, .total_loops_tested, .results | keys'
            echo ""
        else
            echo "❌ Archivo de resultados NO generado"
            echo ""
            echo "📝 Últimas 50 líneas del log:"
            tail -50 "$LOG_FILE"
        fi
        
        break
    fi
    
    # Show progress
    LINES=$(wc -l < "$LOG_FILE" 2>/dev/null || echo "0")
    LAST_EVENT=$(tail -20 "$LOG_FILE" 2>/dev/null | grep -E "(Fase|✓|E2E|Loop completado)" | tail -1 || echo "Inicializando...")
    
    echo "[$(date +%H:%M:%S)] Líneas: $LINES | Último: $LAST_EVENT"
    
    sleep 30
done

echo ""
echo "🎯 Monitoreo completado"
