# Tool adapters y ejecución unificada

## Objetivo
Normalizar la ejecución de servicios/herramientas bajo una interfaz común, con:
- `timeout`
- `retry`
- `circuit breaker`
- caching (cuando aplica)
- auto-discovery de capacidades

## Ubicación en el código
- `app/adapters/unified_tool_adapter.py` (interfaz unificada + circuit breaker)
- `app/adapters/async_tool_adapter.py` (ejecución async)
- `app/adapters/tool_adapter.py` (base/compat)
- `app/adapters/tool_adapter_cache.py` (cache)

## Conceptos clave
- `UnifiedToolInterface`: contrato mínimo para ejecutar una herramienta con `run(payload)`.
- `ToolCapability`: describe una capacidad (nombre, input/output schema, tags, dependencias).
- `ExecutionConfig`: configura resiliencia (timeouts, retries, circuit breaker, concurrencia).
- `ExecutionResult`: salida estandarizada.
- `BaseServiceAdapter`: adapta servicios que heredan de `BaseService` a la interfaz unificada.

## Patrón recomendado para agregar una herramienta
1) Implementar/usar un `BaseService` (si aplica)
2) Crear un adapter (si no encaja en `BaseServiceAdapter`)
3) Definir capabilities mínimas (o permitir auto-discovery)
4) Asegurar health check

## Riesgos comunes
- Imports pesados: preferir lazy imports dentro de métodos.
- Timeouts: ajustar por acción/servicio.
- Circuit breaker: evitar que abra por fallos “esperados” (p.ej. dependencias opcionales).
