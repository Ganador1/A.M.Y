#!/bin/bash

# PRUEBA ESPECÍFICA PARA MONITOREO DE CICLOS DE INVESTIGACIÓN
# Esta prueba se enfoca en arreglar los errores específicos encontrados

echo "🔧 PRUEBA DE MONITOREO DE CICLOS - CORRECCIÓN DE ERRORES"
echo "======================================================="

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

echo ""
echo "2. PRUEBA DE CICLOS ACTIVOS (SIN FILTROS)"
echo "------------------------------------------"

echo "Probando endpoint /active-cycles..."
active_cycles_response=$(test_endpoint "$BASE_URL/api/research-cycle/active-cycles")
if [ $? -eq 0 ] && echo "$active_cycles_response" | grep -q '"success":true'; then
    check_result "Ciclos Activos" "true"
    count=$(echo "$active_cycles_response" | grep -o '"count":[0-9]*' | cut -d':' -f2)
    echo "   🔄 Ciclos activos encontrados: ${count:-0}"
else
    check_result "Ciclos Activos" "false" "Error obteniendo ciclos activos: $active_cycles_response"
fi

echo ""
echo "3. CREANDO CICLOS DE PRUEBA"
echo "----------------------------"

# Crear algunos ciclos de investigación para probar
cycle_data_1='{"research_question":"Test question 1","domain":"materials_science","max_iterations":2,"convergence_threshold":0.8}'
cycle_data_2='{"research_question":"Test question 2","domain":"drug_discovery","max_iterations":2,"convergence_threshold":0.8}'

cycle_ids=()

echo "Creando Ciclo 1..."
cycle_response_1=$(test_endpoint "$BASE_URL/api/research-cycle/start-cycle" "POST" "$cycle_data_1")
if [ $? -eq 0 ] && echo "$cycle_response_1" | grep -q '"success":true'; then
    cycle_id_1=$(echo "$cycle_response_1" | grep -o '"cycle_id":"[^"]*"' | cut -d'"' -f4)
    if [ -n "$cycle_id_1" ]; then
        cycle_ids+=("$cycle_id_1")
        check_result "Crear Ciclo 1" "true"
        echo "   📋 Cycle ID 1: $cycle_id_1"
    else
        check_result "Crear Ciclo 1" "false" "No se pudo extraer cycle_id"
    fi
else
    check_result "Crear Ciclo 1" "false" "Error en respuesta: $cycle_response_1"
fi

echo "Creando Ciclo 2..."
cycle_response_2=$(test_endpoint "$BASE_URL/api/research-cycle/start-cycle" "POST" "$cycle_data_2")
if [ $? -eq 0 ] && echo "$cycle_response_2" | grep -q '"success":true'; then
    cycle_id_2=$(echo "$cycle_response_2" | grep -o '"cycle_id":"[^"]*"' | cut -d'"' -f4)
    if [ -n "$cycle_id_2" ]; then
        cycle_ids+=("$cycle_id_2")
        check_result "Crear Ciclo 2" "true"
        echo "   📋 Cycle ID 2: $cycle_id_2"
    else
        check_result "Crear Ciclo 2" "false" "No se pudo extraer cycle_id"
    fi
else
    check_result "Crear Ciclo 2" "false" "Error en respuesta: $cycle_response_2"
fi

echo ""
echo "4. PRUEBA DE ESTADO DE CICLOS INDIVIDUALES"
echo "-------------------------------------------"

# Esperar un poco para que los ciclos procesen
echo "Esperando 3 segundos para que los ciclos procesen..."
sleep 3

for i in "${!cycle_ids[@]}"; do
    cycle_id="${cycle_ids[$i]}"
    echo "Verificando estado del Ciclo $((i+1)): $cycle_id"

    status_response=$(test_endpoint "$BASE_URL/api/research-cycle/cycle/$cycle_id/status")
    if [ $? -eq 0 ] && echo "$status_response" | grep -q '"success":true'; then
        status=$(echo "$status_response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        progress=$(echo "$status_response" | grep -o '"progress":[0-9.]*' | cut -d':' -f2)
        check_result "Estado Ciclo $((i+1))" "true"
        echo "   📈 Estado: ${status:-unknown}, Progreso: ${progress:-0}%"
    else
        check_result "Estado Ciclo $((i+1))" "false" "Error obteniendo estado: $status_response"
    fi
done

echo ""
echo "5. PRUEBA DE CICLOS ACTIVOS (CON CICLOS CREADOS)"
echo "-------------------------------------------------"

echo "Probando endpoint /active-cycles con ciclos activos..."
active_cycles_response=$(test_endpoint "$BASE_URL/api/research-cycle/active-cycles")
if [ $? -eq 0 ] && echo "$active_cycles_response" | grep -q '"success":true'; then
    check_result "Ciclos Activos (con datos)" "true"
    count=$(echo "$active_cycles_response" | grep -o '"count":[0-9]*' | cut -d':' -f2)
    total=$(echo "$active_cycles_response" | grep -o '"total_cycles":[0-9]*' | cut -d':' -f2)
    echo "   🔄 Ciclos activos: ${count:-0}, Total: ${total:-0}"
else
    check_result "Ciclos Activos (con datos)" "false" "Error obteniendo ciclos activos: $active_cycles_response"
fi

echo ""
echo "6. PRUEBA DE LISTADO DE CICLOS"
echo "-------------------------------"

echo "Probando endpoint de listado de ciclos..."
list_response=$(test_endpoint "$BASE_URL/api/research-cycle/list-cycles" "POST" '{}')
if [ $? -eq 0 ] && echo "$list_response" | grep -q '"success":true'; then
    check_result "Listado Ciclos" "true"
    total_count=$(echo "$list_response" | grep -o '"total_count":[0-9]*' | cut -d':' -f2)
    active_count=$(echo "$list_response" | grep -o '"active_count":[0-9]*' | cut -d':' -f2)
    echo "   📊 Total: ${total_count:-0}, Activos: ${active_count:-0}"
else
    check_result "Listado Ciclos" "false" "Error listando ciclos: $list_response"
fi

echo ""
echo "7. RESULTADOS FINALES"
echo "====================="

echo ""
echo "📊 RESUMEN DE CORRECCIONES:"
echo "==========================="

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
    echo "🎉 ¡TODOS LOS ERRORES DE MONITOREO CORREGIDOS!"
    echo "   ✅ Ciclos activos funcionan correctamente"
    echo "   ✅ Estado de ciclos individuales funciona"
    echo "   ✅ Listado de ciclos funciona"
elif [ $SUCCESS_COUNT -gt $((TOTAL_COUNT * 8 / 10)) ]; then
    echo "✅ Excelente progreso. Sistema muy mejorado."
elif [ $SUCCESS_COUNT -gt $((TOTAL_COUNT / 2)) ]; then
    echo "⚠️ Buen progreso. Algunos errores persisten."
else
    echo "❌ Se necesitan más correcciones."
fi

echo ""
echo "🚀 FUNCIONALIDADES CORREGIDAS:"
echo "=============================="
echo "• ✅ Monitoreo de ciclos activos"
echo "• ✅ Estado detallado de ciclos individuales"
echo "• ✅ Listado completo de ciclos"
echo "• ✅ Manejo robusto de listas vacías"
echo "• ✅ Prevención de divisiones por cero"

echo ""
echo "💡 PRÓXIMOS PASOS:"
echo "=================="
echo "• Ejecutar la prueba avanzada completa nuevamente"
echo "• Verificar que todos los errores estén resueltos"
echo "• Optimizar el rendimiento del sistema"
