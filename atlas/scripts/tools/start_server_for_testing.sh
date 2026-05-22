#!/bin/bash
# ⚠️ Advertencia: inicia un servidor local sin autenticación.
# Úsalo solo en entorno controlado. No exponer públicamente sin TLS/ACL.
# Revisa ETHICS_AND_SAFETY.md.
# AXIOM Scientific Testing - Simple Version
# Inicia el servidor y espera para testing manual

echo "🚀 Iniciando AXIOM Server para Testing Científico"
echo "================================================="

# Activar entorno virtual
echo "📦 Activando entorno virtual..."
source .venv/bin/activate

# Iniciar servidor
echo "🖥️  Iniciando servidor AXIOM..."
python main.py &
SERVER_PID=$!

# Esperar que el servidor se inicie
echo "⏳ Esperando que el servidor se inicie..."
sleep 10

# Verificar que el servidor esté corriendo
echo "🔍 Verificando conexión al servidor..."
if curl -s http://localhost:8002/health > /dev/null; then
    echo "✅ Servidor está corriendo correctamente en http://localhost:8002"
    echo ""
    echo "📋 Instrucciones para testing:"
    echo "1. Abre una nueva terminal"
    echo "2. Ejecuta: source .venv/bin/activate"
    echo "3. Ejecuta: python test_scientific_endpoints.py"
    echo ""
    echo "🛑 Para detener el servidor presiona Ctrl+C"
    echo ""
    echo "Esperando... (Ctrl+C para salir)"
    wait $SERVER_PID
else
    echo "❌ Servidor no responde"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi
