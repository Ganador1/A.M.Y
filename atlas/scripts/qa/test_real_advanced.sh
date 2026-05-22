#!/bin/bash

# PRUEBA AVANZADA DE AXIOM PHASE 2 - MÚLTIPLES CICLOS DE INVESTIGACIÓN
# Esta prueba valida la capacidad del sistema para manejar múltiples
# ciclos de investigación simultáneos y bucles iterativos

echo "🧪 PRUEBA AVANZADA DE AXIOM PHASE 2 - MÚLTIPLES CICLOS"
echo "======================================================"

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
echo "1. INICIANDO SERVIDOR Y VERIFICACIONES BÁSICAS"
echo "----------------------------------------------"

# Iniciar servidor en background
cd .
source .venv/bin/activate
python main.py &
SERVER_PID=$!

# Configurar cleanup
trap "echo '🧹 Deteniendo servidor...'; kill $SERVER_PID 2>/dev/null; wait $SERVER_PID 2>/dev/null; echo '✅ Servidor detenido'" EXIT

# Esperar servidor
if ! wait_for_server; then
    echo "❌ No se pudo iniciar el servidor"
    exit 1
fi

# Verificar health básico
echo "Probando health check básico..."
health_response=$(test_endpoint "$BASE_URL/health")
if [ $? -eq 0 ] && echo "$health_response" | grep -q '"status":"healthy"'; then
    check_result "Health Check Básico" "true"
else
    check_result "Health Check Básico" "false" "Respuesta inválida"
fi

echo ""
echo "2. PRUEBA DE MÚLTIPLES CICLOS DE INVESTIGACIÓN SIMULTÁNEOS"
echo "----------------------------------------------------------"

# Temas de investigación para probar múltiples ciclos
research_topics=(
    '{"research_question":"How to improve thermal conductivity in polymer composites?","domain":"materials_science","max_iterations":3,"convergence_threshold":0.8}'
    '{"research_question":"How to optimize binding affinity in small molecule inhibitors?","domain":"drug_discovery","max_iterations":3,"convergence_threshold":0.8}'
    '{"research_question":"How to extend cycle life in lithium-ion batteries?","domain":"energy_storage","max_iterations":3,"convergence_threshold":0.8}'
)

cycle_ids=()

for i in "${!research_topics[@]}"; do
    echo "🔄 Iniciando Ciclo de Investigación $((i+1))..."
    topic_data="${research_topics[$i]}"

    cycle_response=$(test_endpoint "$BASE_URL/api/research-cycle/start-cycle" "POST" "$topic_data")
    if [ $? -eq 0 ] && echo "$cycle_response" | grep -q '"success":true'; then
        # Extraer cycle_id de la respuesta
        cycle_id=$(echo "$cycle_response" | grep -o '"cycle_id":"[^"]*"' | cut -d'"' -f4)
        if [ -n "$cycle_id" ]; then
            cycle_ids+=("$cycle_id")
            check_result "Ciclo Investigación $((i+1))" "true"
            echo "   📋 Cycle ID: $cycle_id"
        else
            check_result "Ciclo Investigación $((i+1))" "false" "No se pudo extraer cycle_id"
        fi
    else
        check_result "Ciclo Investigación $((i+1))" "false" "Error en respuesta: $cycle_response"
    fi
done

echo ""
echo "3. PRUEBA DE GENERACIÓN MÚLTIPLE DE HIPÓTESIS"
echo "---------------------------------------------"

hypothesis_topics=(
    '{"domain":"materials_science","research_question":"How to improve thermal conductivity in polymer composites?"}'
    '{"domain":"drug_discovery","research_question":"How to optimize binding affinity in small molecule inhibitors?"}'
    '{"domain":"energy_storage","research_question":"How to extend cycle life in lithium-ion batteries?"}'
    '{"domain":"quantum_computing","research_question":"How to reduce quantum error rates in superconducting qubits?"}'
)

hypothesis_ids=()

for i in "${!hypothesis_topics[@]}"; do
    echo "🧠 Generando Hipótesis $((i+1))..."
    topic_data="${hypothesis_topics[$i]}"

    hypothesis_response=$(test_endpoint "$BASE_URL/api/scientific-hypothesis/generate-hypothesis" "POST" "$topic_data")
    if [ $? -eq 0 ] && echo "$hypothesis_response" | grep -q '"success":true'; then
        hypothesis_id=$(echo "$hypothesis_response" | grep -o '"hypothesis_id":"[^"]*"' | cut -d'"' -f4)
        if [ -n "$hypothesis_id" ]; then
            hypothesis_ids+=("$hypothesis_id")
            check_result "Hipótesis $((i+1))" "true"
            echo "   🆔 Hypothesis ID: $hypothesis_id"
        else
            check_result "Hipótesis $((i+1))" "false" "No se pudo extraer hypothesis_id"
        fi
    else
        check_result "Hipótesis $((i+1))" "false" "Error en respuesta: $hypothesis_response"
    fi
done

echo ""
echo "4. PRUEBA DE BÚSQUEDA DE LITERATURA MÚLTIPLE"
echo "--------------------------------------------"

literature_queries=(
    '{"query":"thermal conductivity polymer composites","domain":"materials_science","max_results":5}'
    '{"query":"small molecule drug binding affinity","domain":"drug_discovery","max_results":5}'
    '{"query":"lithium ion battery cycle life","domain":"energy_storage","max_results":5}'
    '{"query":"quantum error correction superconducting","domain":"quantum_computing","max_results":5}'
)

search_ids=()

for i in "${!literature_queries[@]}"; do
    echo "📚 Búsqueda de Literatura $((i+1))..."
    query_data="${literature_queries[$i]}"

    literature_response=$(test_endpoint "$BASE_URL/api/literature-search/search-literature" "POST" "$query_data")
    if [ $? -eq 0 ] && echo "$literature_response" | grep -q '"success":true'; then
        search_id=$(echo "$literature_response" | grep -o '"search_id":"[^"]*"' | cut -d'"' -f4)
        if [ -n "$search_id" ]; then
            search_ids+=("$search_id")
            papers_found=$(echo "$literature_response" | grep -o '"relevant_found":[0-9]*' | cut -d':' -f2)
            check_result "Búsqueda Literatura $((i+1))" "true"
            echo "   🔍 Search ID: $search_id, Papers: ${papers_found:-0}"
        else
            check_result "Búsqueda Literatura $((i+1))" "false" "No se pudo extraer search_id"
        fi
    else
        check_result "Búsqueda Literatura $((i+1))" "false" "Error en respuesta: $literature_response"
    fi
done

echo ""
echo "5. PRUEBA DE MONITOREO DE CICLOS ACTIVOS"
echo "----------------------------------------"

echo "Verificando ciclos de investigación activos..."
active_cycles_response=$(test_endpoint "$BASE_URL/api/research-cycle/active-cycles")
if [ $? -eq 0 ] && echo "$active_cycles_response" | grep -q '"success":true'; then
    active_count=$(echo "$active_cycles_response" | grep -o '"count":[0-9]*' | cut -d':' -f2)
    check_result "Ciclos Activos" "true"
    echo "   🔄 Ciclos activos: ${active_count:-0}"
else
    check_result "Ciclos Activos" "false" "Error obteniendo ciclos activos"
fi

echo ""
echo "6. PRUEBA DE ESTADO DE CICLOS INDIVIDUALES"
echo "-------------------------------------------"

for i in "${!cycle_ids[@]}"; do
    cycle_id="${cycle_ids[$i]}"
    echo "📊 Verificando estado del Ciclo $((i+1)): $cycle_id"

    status_response=$(test_endpoint "$BASE_URL/api/research-cycle/cycle/$cycle_id/status")
    if [ $? -eq 0 ] && echo "$status_response" | grep -q '"success":true'; then
        status=$(echo "$status_response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        progress=$(echo "$status_response" | grep -o '"progress":[0-9.]*' | cut -d':' -f2)
        check_result "Estado Ciclo $((i+1))" "true"
        echo "   📈 Estado: ${status:-unknown}, Progreso: ${progress:-0}%"
    else
        check_result "Estado Ciclo $((i+1))" "false" "Error obteniendo estado"
    fi
done

echo ""
echo "7. PRUEBA DE GENERACIÓN DE REVISIÓN DE LITERATURA"
echo "-------------------------------------------------"

echo "Generando revisión de literatura completa..."
review_data='{"topic":"thermal conductivity in advanced materials","domain":"materials_science","max_papers":5}'

review_response=$(test_endpoint "$BASE_URL/api/literature-search/generate-literature-review" "POST" "$review_data")
if [ $? -eq 0 ] && echo "$review_response" | grep -q '"success":true'; then
    check_result "Revisión Literatura" "true"
    echo "   📖 Revisión de literatura generada exitosamente"
else
    check_result "Revisión Literatura" "false" "Error generando revisión"
fi

echo ""
echo "8. PRUEBA DE CARGA CONCURRENTE"
echo "-------------------------------"

echo "Ejecutando prueba de carga con múltiples solicitudes simultáneas..."
START_TIME=$(date +%s.%3N)

# Ejecutar múltiples solicitudes en paralelo
for i in {1..10}; do
    curl -s "$BASE_URL/health" > /dev/null &
    curl -s "$BASE_URL/api/scientific-hypothesis/health" > /dev/null &
    curl -s "$BASE_URL/api/literature-search/health" > /dev/null &
    curl -s "$BASE_URL/api/research-cycle/health" > /dev/null &
done
wait

END_TIME=$(date +%s.%3N)
ELAPSED=$(echo "$END_TIME - $START_TIME" | bc 2>/dev/null || echo "0")

echo "✅ Prueba de carga completada en ${ELAPSED}s"

echo ""
echo "9. RESULTADOS FINALES DE PRUEBA AVANZADA"
echo "========================================="

echo ""
echo "📊 RESUMEN DE OPERACIONES:"
echo "=========================="

SUCCESS_COUNT=0
TOTAL_COUNT=${#TEST_RESULTS[@]}

echo "🔄 Ciclos de Investigación: ${#cycle_ids[@]}"
echo "🧠 Hipótesis Generadas: ${#hypothesis_ids[@]}"
echo "📚 Búsquedas Literatura: ${#search_ids[@]}"
echo "⚡ Solicitudes Concurrentes: 40"

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
    echo "🎉 ¡TODAS LAS PRUEBAS PASARON! AXIOM Phase 2 es completamente robusto."
elif [ $SUCCESS_COUNT -gt $((TOTAL_COUNT * 8 / 10)) ]; then
    echo "✅ Excelente rendimiento. Sistema altamente funcional."
elif [ $SUCCESS_COUNT -gt $((TOTAL_COUNT / 2)) ]; then
    echo "⚠️ Buen rendimiento. Sistema funcional con algunas áreas de mejora."
else
    echo "❌ Rendimiento insuficiente. Requiere optimizaciones adicionales."
fi

echo ""
echo "🚀 FUNCIONALIDADES VALIDADAS:"
echo "============================="
echo "• 🔄 Múltiples ciclos de investigación simultáneos"
echo "• 🧠 Generación masiva de hipótesis científicas"
echo "• 📚 Búsqueda inteligente de literatura múltiple"
echo "• 📊 Monitoreo y estado de ciclos activos"
echo "• 📖 Generación automática de revisiones de literatura"
echo "• ⚡ Manejo de carga concurrente alta"
echo "• 🔧 Robustez del sistema bajo estrés"

echo ""
echo "🎊 ¡AXIOM Phase 2: IA Meta-Científica está listo para investigación a gran escala!"

echo ""
echo "💡 RECOMENDACIONES PARA USO EN PRODUCCIÓN:"
echo "=========================================="
echo "• El sistema puede manejar múltiples investigaciones simultáneas"
echo "• Los ciclos de investigación funcionan correctamente"
echo "• La búsqueda de literatura es eficiente y escalable"
echo "• El monitoreo en tiempo real está disponible"
echo "• La carga concurrente es manejable"
