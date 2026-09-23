#!/bin/bash
# AXIOM Scientific Testing Script
# Inicia el servidor y ejecuta testing de endpoints científicos

echo "🚀 Iniciando AXIOM Server y Testing Científico"
echo "=============================================="

# Activar entorno virtual
echo "📦 Activando entorno virtual..."
source .venv/bin/activate

# Iniciar servidor en background
echo "🖥️  Iniciando servidor AXIOM..."
python3 main.py &
SERVER_PID=$!

# Esperar que el servidor se inicie
echo "⏳ Esperando que el servidor se inicie..."
sleep 15

# Verificar que el servidor esté corriendo
echo "🔍 Verificando conexión al servidor..."
if curl -s http://localhost:8002/health > /dev/null; then
    echo "✅ Servidor está corriendo correctamente"
else
    echo "❌ Servidor no responde"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

# Ejecutar testing de endpoints científicos
echo "🧪 Ejecutando testing de endpoints científicos..."
python3 scripts/qa/test_scientific_endpoints.py

# Detener servidor
echo "🛑 Deteniendo servidor..."
kill $SERVER_PID 2>/dev/null

echo "✅ Testing completado"
