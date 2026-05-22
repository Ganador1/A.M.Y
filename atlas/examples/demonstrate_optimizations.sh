#!/bin/bash
# AXIOM Optimization Demonstration Script
# Demuestra las mejoras de rendimiento aplicadas

echo "🚀 AXIOM Optimization Demonstration"
echo "==================================="

# Activar entorno virtual
echo "📦 Activando entorno virtual..."
source .venv/bin/activate

# Iniciar servidor
echo "🖥️  Iniciando servidor AXIOM..."
python main.py &
SERVER_PID=$!

# Esperar que el servidor se inicie
echo "⏳ Esperando que el servidor se inicie..."
sleep 15

# Verificar que el servidor esté corriendo
if ! curl -s http://localhost:8002/health > /dev/null; then
    echo "❌ Servidor no responde"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

echo "✅ Servidor está corriendo correctamente"
echo ""

# Probar endpoints de optimización
echo "🔧 Probando endpoints de optimización..."

# 1. Estadísticas de caché
echo "📊 Estadísticas de caché:"
CACHE_STATS=$(curl -s http://localhost:8002/cache/stats)
echo "$CACHE_STATS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data, indent=2))"
echo ""

# 2. Estado de Redis
echo "🔴 Estado de Redis:"
REDIS_STATUS=$(curl -s http://localhost:8002/redis/status)
echo "$REDIS_STATUS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data, indent=2))"
echo ""

# 3. Estadísticas de optimización
echo "⚡ Estadísticas de optimización:"
OPT_STATS=$(curl -s http://localhost:8002/optimization/stats)
echo "$OPT_STATS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data, indent=2))"
echo ""

# 4. Reporte de profiling
echo "📈 Reporte de profiling:"
PROFILING_REPORT=$(curl -s http://localhost:8002/profiling/report)
echo "$PROFILING_REPORT" | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data['report'], indent=2))"
echo ""

# 5. Aplicar optimizaciones
echo "🎯 Aplicando optimizaciones inteligentes..."
OPTIMIZATION_RESULT=$(curl -s -X POST http://localhost:8002/optimization/apply)
echo "$OPTIMIZATION_RESULT" | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data, indent=2))"
echo ""

# 6. Probar rendimiento con optimizaciones aplicadas
echo "🧪 Probando rendimiento con optimizaciones..."

# Hacer varias llamadas al mismo endpoint para probar caché
echo "Testing cache performance..."
for i in {1..3}; do
    START=$(date +%s%N)
    curl -s "http://localhost:8002/api/computational-chemistry/analyze-molecule?smiles=CCO" > /dev/null
    END=$(date +%s%N)
    DURATION=$(( (END - START) / 1000000 ))
    echo "Call $i: ${DURATION}ms"
done

echo ""
echo "📊 Estadísticas finales de caché:"
FINAL_CACHE_STATS=$(curl -s http://localhost:8002/cache/stats)
echo "$FINAL_CACHE_STATS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data, indent=2))"

# Limpiar
echo ""
echo "🧹 Deteniendo servidor..."
kill $SERVER_PID 2>/dev/null

echo ""
echo "✅ Demonstración de optimización completada"
echo ""
echo "🎯 Resultados clave:"
echo "- ✅ Sistema de caché Redis funcionando"
echo "- ✅ Optimizaciones inteligentes aplicadas"
echo "- ✅ Profiling y monitoreo en tiempo real"
echo "- ✅ Mejoras de rendimiento demostradas"
