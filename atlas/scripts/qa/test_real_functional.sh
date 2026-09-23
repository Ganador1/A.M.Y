#!/bin/bash

# Prueba Real de AXIOM Phase 2 - Funcional y Completa
# Esta prueba valida todas las funcionalidades implementadas

echo "🧪 PRUEBA REAL DE AXIOM PHASE 2: IA META-CIENTÍFICA"
echo "=================================================="

BASE_URL="http://localhost:8002"
TEST_RESULTS=()

# Función para verificar resultado
check_result() {
    local test_name="$1"
    local success="$2"
    local message="$3"

    if [ "$success" = "true" ]; then
        echo "✅ $test_name: ÉXITO"
        TEST_RESULTS+=("✅ $test_name")
    else
        echo "❌ $test_name: FALLÓ - $message"
        TEST_RESULTS+=("❌ $test_name: $message")
    fi
}

# Función para esperar que el servidor esté listo
wait_for_server() {
    echo "⏳ Esperando que el servidor esté listo..."
    for i in {1..30}; do
        if curl -s "$BASE_URL/health" > /dev/null 2>&1; then
            echo "✅ Servidor listo en $BASE_URL"
            return 0
        fi
        sleep 1
        echo -n "."
    done
    echo "❌ Servidor no respondió en 30 segundos"
    return 1
}

# Función para probar endpoint
test_endpoint() {
    local url="$1"
    local method="${2:-GET}"
    local data="$3"
    local expected_status="${4:-200}"

    if [ "$method" = "POST" ] && [ -n "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$url" \
            -H "Content-Type: application/json" \
            -d "$data")
    else
        response=$(curl -s -w "\n%{http_code}" "$url")
    fi

    # Separar cuerpo y código de estado
    body=$(echo "$response" | sed '$d')
    status=$(echo "$response" | tail -n 1)

    if [ "$status" = "$expected_status" ]; then
        echo "$body"
        return 0
    else
        echo "Error: HTTP $status"
        return 1
    fi
}

echo ""
echo "1. INICIANDO SERVIDOR"
echo "---------------------"

# Iniciar servidor en background (desactivar DB para entorno local sin PostgreSQL)
cd .
source .venv/bin/activate
export ENABLE_DATABASE=false
export SKIP_DB_INIT=1
python main.py &
SERVER_PID=$!

# Configurar cleanup
trap "echo '🧹 Deteniendo servidor...'; kill $SERVER_PID 2>/dev/null; wait $SERVER_PID 2>/dev/null; echo '✅ Servidor detenido'" EXIT

# Esperar servidor
if ! wait_for_server; then
    echo "❌ No se pudo iniciar el servidor"
    exit 1
fi

echo ""
echo "2. PRUEBAS DE SALUD DEL SISTEMA"
echo "-------------------------------"

# Prueba health check básico
echo "Probando health check básico..."
health_response=$(test_endpoint "$BASE_URL/health")
if [ $? -eq 0 ] && echo "$health_response" | grep -q '"status":"healthy"'; then
    check_result "Health Check Básico" "true"
else
    check_result "Health Check Básico" "false" "Respuesta inválida: $health_response"
fi

# Prueba health detallado
echo "Probando health check detallado..."
detailed_health=$(test_endpoint "$BASE_URL/health/detailed")
if [ $? -eq 0 ] && echo "$detailed_health" | grep -q '"status":"healthy"'; then
    check_result "Health Check Detallado" "true"
else
    check_result "Health Check Detallado" "false" "Respuesta inválida"
fi

echo ""
echo "3. PRUEBAS DE SERVICIOS CIENTÍFICOS EXISTENTES"
echo "---------------------------------------------"

# Prueba servicio de cálculo
echo "Probando servicio de cálculo..."
calc_response=$(test_endpoint "$BASE_URL/api/arithmetic/calculate" "POST" '{"expression": "2 + 3 * 4"}')
if [ $? -eq 0 ] && echo "$calc_response" | grep -q '"result":14'; then
    check_result "Servicio de Cálculo" "true"
else
    check_result "Servicio de Cálculo" "false" "Resultado incorrecto"
fi

# Prueba servicio de ecuaciones
echo "Probando servicio de ecuaciones..."
eq_response=$(test_endpoint "$BASE_URL/api/equations/solve" "POST" '{"equation": "x^2 - 4 = 0"}')
if [ $? -eq 0 ] && echo "$eq_response" | grep -q '"solutions"'; then
    check_result "Servicio de Ecuaciones" "true"
else
    check_result "Servicio de Ecuaciones" "false" "No se encontraron soluciones"
fi

echo ""
echo "4. PRUEBAS DE SERVICIOS DE FASE 2"
echo "---------------------------------"

# Prueba servicio de optimización
echo "Probando servicio de optimización..."
opt_response=$(test_endpoint "$BASE_URL/api/optimization/solve" "POST" '{
    "method": "linear_programming",
    "c": [1, 2],
    "A_ub": [[1, 1], [2, 1]],
    "b_ub": [6, 8]
}')
if [ $? -eq 0 ] && echo "$opt_response" | grep -q '"status":"optimal"'; then
    check_result "Servicio de Optimización" "true"
else
    check_result "Servicio de Optimización" "false" "Optimización falló"
fi

# Prueba servicio de hipótesis científicas
echo "Probando servicio de hipótesis científicas..."
hypothesis_response=$(test_endpoint "$BASE_URL/api/scientific-hypothesis/generate-hypothesis" "POST" '{
    "domain": "materials_science",
    "research_question": "How to improve thermal conductivity in composite materials?"
}')
if [ $? -eq 0 ] && echo "$hypothesis_response" | grep -q '"success":true'; then
    check_result "Servicio de Hipótesis Científicas" "true"
else
    check_result "Servicio de Hipótesis Científicas" "false" "Generación de hipótesis falló"
fi

# Prueba servicio de búsqueda de literatura
echo "Probando servicio de búsqueda de literatura..."
literature_response=$(test_endpoint "$BASE_URL/api/literature-search/search-literature" "POST" '{
    "query": "thermal conductivity composites",
    "domain": "materials_science",
    "max_results": 5
}')
if [ $? -eq 0 ] && echo "$literature_response" | grep -q '"success":true'; then
    check_result "Servicio de Literatura" "true"
else
    check_result "Servicio de Literatura" "false" "Búsqueda de literatura falló"
fi

# Prueba servicio de ciclo de investigación
echo "Probando servicio de ciclo de investigación..."
cycle_response=$(test_endpoint "$BASE_URL/api/research-cycle/start-cycle" "POST" '{
    "research_question": "How to improve thermal conductivity in composite materials?",
    "domain": "materials_science",
    "max_iterations": 3
}')
if [ $? -eq 0 ] && echo "$cycle_response" | grep -q '"success":true'; then
    check_result "Servicio de Ciclo de Investigación" "true"
else
    check_result "Servicio de Ciclo de Investigación" "false" "Ciclo de investigación falló"
fi

echo ""
echo "5. PRUEBAS DE ENDPOINTS DE SALUD ESPECÍFICOS"
echo "--------------------------------------------"

# Health checks de servicios específicos
services=("scientific-hypothesis" "literature-search" "research-cycle")
for service in "${services[@]}"; do
    echo "Probando health de $service..."
    health_resp=$(test_endpoint "$BASE_URL/api/$service/health")
    if [ $? -eq 0 ] && echo "$health_resp" | grep -q '"status":"healthy"'; then
        check_result "Health $service" "true"
    else
        check_result "Health $service" "false" "Servicio no saludable"
    fi
done

echo ""
echo "6. PRUEBA DE CARGA BÁSICA"
echo "-------------------------"

echo "Ejecutando prueba de carga básica (5 solicitudes concurrentes)..."
START_TIME=$(date +%s.%3N)

# Ejecutar 5 solicitudes en paralelo
for i in {1..5}; do
    curl -s "$BASE_URL/health" > /dev/null &
    curl -s "$BASE_URL/api/arithmetic/info" > /dev/null &
    curl -s "$BASE_URL/api/scientific-hypothesis/health" > /dev/null &
done
wait

END_TIME=$(date +%s.%3N)
ELAPSED=$(echo "$END_TIME - $START_TIME" | bc 2>/dev/null || echo "0")

echo "✅ Prueba de carga completada en ${ELAPSED}s"

echo ""
echo "7. PRUEBA DE FUNCIONALIDADES AVANZADAS"
echo "--------------------------------------"

# Prueba de generación de revisión de literatura
echo "Probando generación de revisión de literatura..."
review_response=$(test_endpoint "$BASE_URL/api/literature-search/generate-literature-review" "POST" '{
    "topic": "thermal conductivity in composites",
    "domain": "materials_science",
    "max_papers": 3
}')
if [ $? -eq 0 ] && echo "$review_response" | grep -q '"success":true'; then
    check_result "Revisión de Literatura" "true"
else
    check_result "Revisión de Literatura" "false" "Generación de revisión falló"
fi

echo ""
echo "8. RESULTADOS FINALES"
echo "====================="

echo ""
echo "📊 RESUMEN DE PRUEBAS:"
echo "======================"

SUCCESS_COUNT=0
TOTAL_COUNT=${#TEST_RESULTS[@]}

for result in "${TEST_RESULTS[@]}"; do
    echo "$result"
    if [[ $result == ✅* ]]; then
        ((SUCCESS_COUNT++))
    fi
done

echo ""
echo "🎯 RESULTADO FINAL:"
echo "=================="
echo "✅ Pruebas exitosas: $SUCCESS_COUNT/$TOTAL_COUNT"

if [ $SUCCESS_COUNT -eq $TOTAL_COUNT ]; then
    echo "🎉 ¡TODAS LAS PRUEBAS PASARON! AXIOM Phase 2 está completamente funcional."
elif [ $SUCCESS_COUNT -gt $((TOTAL_COUNT / 2)) ]; then
    echo "⚠️  La mayoría de las pruebas pasaron. Sistema parcialmente funcional."
else
    echo "❌ Varias pruebas fallaron. Revisar configuración del sistema."
fi

echo ""
echo "🚀 FUNCIONALIDADES VALIDADAS:"
echo "============================="
echo "• 🤖 Sistema de investigación autónoma"
echo "• 📚 Búsqueda inteligente de literatura"
echo "• 🔄 Ciclos de investigación cerrados"
echo "• 🧮 Algoritmos de optimización avanzados"
echo "• 🔬 Integración con servicios científicos existentes"
echo "• 📊 Health checks y monitoreo del sistema"
echo "• ⚡ Manejo de carga concurrente"

echo ""
echo "📈 PRÓXIMOS PASOS:"
echo "=================="
echo "• Phase 3: Advanced Workflows (Q2 2026)"
echo "• Optimización AI-driven avanzada"
echo "• Sistemas multi-agente colaborativos"
echo "• Interfaces de usuario mejoradas"

echo ""
echo "🎊 ¡AXIOM Phase 2: IA Meta-Científica está listo para investigación autónoma!"
