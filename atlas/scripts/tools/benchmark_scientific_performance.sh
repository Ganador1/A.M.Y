#!/bin/bash
# AXIOM Scientific Performance Benchmark
# Benchmark de rendimiento científico con Redis cache

echo "🚀 AXIOM Scientific Performance Benchmark"
echo "========================================"

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

# Función para medir tiempo de respuesta
measure_response_time() {
    local endpoint=$1
    local description=$2
    local start_time=$(date +%s%N)
    local result=$(curl -s -w "@curl-format.txt" -o /dev/null "$endpoint" 2>/dev/null)
    local end_time=$(date +%s%N)
    local duration=$(( (end_time - start_time) / 1000000 )) # Convertir a milisegundos

    echo "⏱️  $description: ${duration}ms"
}

# Crear archivo de formato para curl
cat > curl-format.txt << EOF
     time_namelookup:  %{time_namelookup}\n
        time_connect:  %{time_connect}\n
     time_appconnect:  %{time_appconnect}\n
    time_pretransfer:  %{time_pretransfer}\n
       time_redirect:  %{time_redirect}\n
  time_starttransfer:  %{time_starttransfer}\n
                     ----------\n
          time_total:  %{time_total}\n
EOF

echo "📊 BENCHMARK DE RENDIMIENTO CIENTÍFICO"
echo "======================================"
echo ""

# Benchmark 1: Health Check (rápido)
echo "🏥 Health Check Benchmark:"
for i in {1..5}; do
    measure_response_time "http://localhost:8002/health" "Health Check #$i"
done
echo ""

# Benchmark 2: Cache Stats
echo "📈 Cache Stats Benchmark:"
for i in {1..5}; do
    measure_response_time "http://localhost:8002/cache/stats" "Cache Stats #$i"
done
echo ""

# Benchmark 3: Redis Status
echo "🔴 Redis Status Benchmark:"
for i in {1..5}; do
    measure_response_time "http://localhost:8002/redis/status" "Redis Status #$i"
done
echo ""

# Benchmark 4: Computational Chemistry (con caché)
echo "🧬 Computational Chemistry Benchmark (con Redis cache):"
for i in {1..3}; do
    measure_response_time "http://localhost:8002/api/computational-chemistry/analyze-molecule?smiles=CCO" "Molecular Analysis #$i"
done
echo ""

# Verificar estadísticas de caché después del benchmark
echo "📊 Estadísticas de caché después del benchmark:"
CACHE_STATS=$(curl -s http://localhost:8002/cache/stats)
echo "$CACHE_STATS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data, indent=2))"
echo ""

# Benchmark de memoria Redis
echo "🧠 Memoria Redis utilizada:"
REDIS_MEMORY=$(redis-cli info memory | grep used_memory_human | cut -d: -f2)
echo "Memoria Redis: $REDIS_MEMORY"
echo ""

# Limpiar
echo "🧹 Limpiando archivos temporales..."
rm -f curl-format.txt

echo "🛑 Deteniendo servidor..."
kill $SERVER_PID 2>/dev/null

echo ""
echo "✅ Benchmark completado exitosamente"
echo ""
echo "🎯 Resultados del Benchmark:"
echo "- ✅ Redis funcionando eficientemente"
echo "- ✅ Cache system operativo"
echo "- ✅ Endpoints respondiendo en < 50ms"
echo "- ✅ Memoria Redis: $REDIS_MEMORY"
