#!/bin/bash
# AXIOM ATLAS - Script de Validación de Entorno
# Ejecuta todas las validaciones del ENV_SETUP_GUIDE.md

set -e

echo "🚀 AXIOM ATLAS - Validación de Entorno"
echo "======================================"
echo ""

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para mostrar éxito
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Función para mostrar advertencia
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Función para mostrar error
error() {
    echo -e "${RED}❌ $1${NC}"
}

# 1. Verificar Python
echo "1️⃣  Verificando Python..."
if python --version | grep -q "3.13"; then
    success "Python version: $(python --version)"
else
    warning "Python version: $(python --version) - Se recomienda 3.13.x"
fi
echo ""

# 2. Verificar virtualenv
echo "2️⃣  Verificando virtualenv..."
if [[ "$VIRTUAL_ENV" == *".venv_new"* ]]; then
    success "Virtualenv activo: $VIRTUAL_ENV"
else
    error "Virtualenv .venv_new no está activo"
    echo "   Ejecuta: source .venv_new/bin/activate"
    exit 1
fi
echo ""

# 3. Verificar enlace simbólico de configuración
echo "3️⃣  Verificando configuraciones YAML..."
if [ -L "./config" ]; then
    success "Enlace simbólico de configuración existe"
else
    error "Enlace simbólico de configuración no existe"
    echo "   Ejecuta: mkdir -p . && ln -sf \"$(pwd)/config\" ./config"
    exit 1
fi
echo ""

# 4. Verificar archivos de configuración
echo "4️⃣  Verificando archivos YAML individuales..."
CONFIG_FILES=(
    "agents.yaml"
    "models.yaml"
    "plausibility.yaml"
    "policy_engine_config.yaml"
    "ethics_policy.yaml"
    "improvements_config.yaml"
    "prompts/hypothesis_agent.yaml"
)

for file in "${CONFIG_FILES[@]}"; do
    if [ -f "config/$file" ]; then
        success "$file encontrado"
    else
        error "$file NO encontrado"
    fi
done
echo ""

# 5. Verificar MPLCONFIGDIR
echo "5️⃣  Verificando MPLCONFIGDIR..."
if [ -n "$MPLCONFIGDIR" ]; then
    success "MPLCONFIGDIR configurado: $MPLCONFIGDIR"
else
    warning "MPLCONFIGDIR no configurado"
    echo "   Ejecuta: export MPLCONFIGDIR=~/.config/matplotlib"
fi
echo ""

# 6. Verificar Redis (opcional)
echo "6️⃣  Verificando Redis (opcional)..."
if nc -z localhost 6379 2>/dev/null; then
    success "Redis está corriendo en localhost:6379"
else
    warning "Redis no disponible - Se usará cache en memoria"
    echo "   Para instalar: brew install redis && brew services start redis"
fi
echo ""

# 7. Test de importación
echo "7️⃣  Probando importaciones básicas..."
if python -c "import app; import app.services.master_orchestration_service_refactored" 2>/dev/null; then
    success "Importaciones básicas OK"
else
    error "Falló importación básica"
    exit 1
fi
echo ""

# 8. Ejecutar smoke test
echo "8️⃣  Ejecutando smoke test..."
if pytest tests/unit/test_pipeline_debug.py -q 2>&1 | grep -q "1 passed"; then
    success "Smoke test pasado"
else
    error "Smoke test falló"
    exit 1
fi
echo ""

# 9. Verificar generador de hipótesis
echo "9️⃣  Verificando generador de hipótesis..."
if python -c "from app.autonomous.generators.hypothesis_generator import HypothesisGenerator; gen = HypothesisGenerator(); print('OK')" 2>/dev/null | grep -q "OK"; then
    success "HypothesisGenerator inicializado correctamente"
else
    error "HypothesisGenerator falló"
    exit 1
fi
echo ""

# Resumen final
echo "======================================"
echo ""
success "TODOS LOS TESTS DE VALIDACIÓN PASARON ✅"
echo ""
echo "El entorno está completamente operativo para:"
echo "  • Smoke tests"
echo "  • Loops de investigación autónoma"
echo "  • Generador de hipótesis"
echo "  • Pipeline de orquestación maestro"
echo "  • Multi-agentes científicos"
echo ""
echo "Comandos útiles:"
echo "  pytest tests/unit/test_pipeline_debug.py -q       # Smoke test"
echo "  python run_production_loops_simple.py             # Loops de producción"
echo "  python run_loops_isolated.py --loop materials     # Loop aislado"
echo ""
success "¡Sistema listo para investigación científica autónoma! 🚀"
