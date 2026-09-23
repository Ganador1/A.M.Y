#!/bin/bash
# AXIOM Scientific Testing - Sequential Version
# Ejecuta todo en secuencia sin procesos en background

echo "🚀 AXIOM Scientific Testing - Versión Secuencial"
echo "================================================"

# Activar entorno virtual
echo "📦 Activando entorno virtual..."
source .venv/bin/activate

# Verificar que el servidor no esté corriendo
echo "🔍 Verificando que no haya servidores corriendo..."
pkill -f "python main.py" 2>/dev/null || true
sleep 2

# Iniciar servidor en background
echo "🖥️  Iniciando servidor AXIOM..."
python main.py &
SERVER_PID=$!

# Función para cleanup
cleanup() {
    echo ""
    echo "🧹 Limpiando procesos..."
    kill $SERVER_PID 2>/dev/null || true
    exit
}

# Configurar trap para cleanup
trap cleanup SIGINT SIGTERM

# Esperar que el servidor se inicie
echo "⏳ Esperando que el servidor se inicie..."
sleep 15

# Verificar que el servidor esté corriendo
echo "🔍 Verificando conexión al servidor..."
if ! curl -s http://localhost:8002/health > /dev/null; then
    echo "❌ Servidor no responde"
    cleanup
fi

echo "✅ Servidor está corriendo correctamente"

# Ejecutar testing
echo "🧪 Ejecutando testing de endpoints científicos..."
python test_scientific_endpoints.py

# Cleanup
cleanup
