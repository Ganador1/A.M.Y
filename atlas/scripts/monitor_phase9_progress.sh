#!/bin/bash
# Monitor Phase 9 execution progress without interrupting

echo "🔍 Monitoring Phase 9 Execution Progress"
echo "=========================================="
echo ""

while true; do
    # Check if process is still running
    if ps aux | grep -q "[r]un_model_comparison_phase8.py"; then
        echo "⏳ Process is running..."
        
        # Get latest log file
        LATEST_LOG=$(ls -t phase9_all_domains_complete_*.log 2>/dev/null | head -1)
        
        if [ -n "$LATEST_LOG" ]; then
            echo "📂 Log file: $LATEST_LOG"
            echo "📊 File size: $(du -h "$LATEST_LOG" | cut -f1)"
            echo ""
            echo "🔬 Last completed iterations:"
            tail -100 "$LATEST_LOG" | grep -E "Completado en|DOMINIO:|Config" | tail -10
            echo ""
        fi
        
        # Check for results JSON
        LATEST_JSON=$(ls -t model_comparison_phase8_*.json 2>/dev/null | head -1)
        if [ -n "$LATEST_JSON" ]; then
            echo "💾 Latest results: $LATEST_JSON ($(stat -f%z "$LATEST_JSON" 2>/dev/null || stat -c%s "$LATEST_JSON" 2>/dev/null) bytes)"
        fi
        
        echo "⏰ $(date)"
        echo "---"
        echo ""
        
        sleep 30
    else
        echo "✅ Process completed!"
        echo ""
        
        # Show final results
        LATEST_JSON=$(ls -t model_comparison_phase8_*.json 2>/dev/null | head -1)
        if [ -n "$LATEST_JSON" ]; then
            echo "🎉 Results saved to: $LATEST_JSON"
            echo "📊 File size: $(du -h "$LATEST_JSON" | cut -f1)"
        fi
        
        break
    fi
done
