#!/bin/bash
# AXIOM Redis Cache Testing Script
# Inicia el servidor y prueba la funcionalidad de Redis

echo "🚀 AXIOM Redis Cache Testing"
echo "============================"

# Activar entorno virtual
echo "📦 Activando entorno virtual..."
source .venv/bin/activate

# Iniciar servidor en background
echo "🖥️  Iniciando servidor AXIOM..."
python main.py &
SERVER_PID=$!

# Esperar que el servidor se inicie
echo "⏳ Esperando que el servidor se inicie..."
sleep 15

# Verificar que el servidor esté corriendo
echo "🔍 Verificando conexión al servidor..."
if ! curl -s http://localhost:8002/health > /dev/null; then
    echo "❌ Servidor no responde"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

echo "✅ Servidor está corriendo correctamente"

# Probar endpoint de caché
echo "📊 Probando endpoint de estadísticas de caché..."
CACHE_STATS=$(curl -s http://localhost:8002/cache/stats)
if [ $? -eq 0 ]; then
    echo "✅ Endpoint de caché funcionando"
    echo "📈 Estadísticas de caché:"
    echo "$CACHE_STATS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data, indent=2))"
else
    echo "❌ Error en endpoint de caché"
fi

# Probar endpoint de status de Redis
echo ""
echo "🔴 Probando endpoint de status de Redis..."
REDIS_STATUS=$(curl -s http://localhost:8002/redis/status)
if [ $? -eq 0 ]; then
    echo "✅ Endpoint de Redis funcionando"
    echo "🔗 Status de Redis:"
    echo "$REDIS_STATUS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data, indent=2))"
else
    echo "❌ Error en endpoint de Redis"
fi

# Probar un endpoint científico para generar caché
echo ""
echo "🧪 Probando endpoint científico para generar caché..."
SCIENTIFIC_RESULT=$(curl -s "http://localhost:8002/api/computational-chemistry/analyze-molecule?smiles=CCO")
if [ $? -eq 0 ]; then
    echo "✅ Endpoint científico funcionando"
    echo "🔬 Resultado científico cached:"
    echo "$SCIENTIFIC_RESULT" | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data, indent=2))" 2>/dev/null || echo "Resultado: $SCIENTIFIC_RESULT"
else
    echo "❌ Error en endpoint científico"
fi

# Verificar caché después de la petición
echo ""
echo "📊 Verificando caché después de petición científica..."
CACHE_STATS_AFTER=$(curl -s http://localhost:8002/cache/stats)
echo "📈 Estadísticas de caché actualizadas:"
echo "$CACHE_STATS_AFTER" | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data, indent=2))"

# Limpiar
echo ""
echo "🧹 Limpiando procesos..."
kill $SERVER_PID 2>/dev/null

echo ""
echo "✅ Testing de Redis completado"
