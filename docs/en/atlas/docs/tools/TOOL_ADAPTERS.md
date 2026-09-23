> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="tool-adapters-y-ejecución-unificada"></a>
# Tool adapters and unified execution

<a id="objetivo"></a>
## Objective
Normalize the execution of services/tools under a common interface, with:
- `timeout`
- `retry`
- `circuit breaker`
- caching (when applicable)
- auto-discovery of capabilities

<a id="ubicación-en-el-código"></a>
## Location in the code
- `app/adapters/unified_tool_adapter.py` (unified interface + circuit breaker)
- `app/adapters/async_tool_adapter.py` (async execution)
- `app/adapters/tool_adapter.py` (base/compat)
- `app/adapters/tool_adapter_cache.py` (cache)

<a id="conceptos-clave"></a>
## Key concepts
- `UnifiedToolInterface`: minimal contract to execute a tool with `run(payload)`.
- `ToolCapability`: describes a capability (name, input/output schema, tags, dependencies).
- `ExecutionConfig`: configures resilience (timeouts, retries, circuit breaker, concurrency).
- `ExecutionResult`: standardized output.
- `BaseServiceAdapter`: adapts services that inherit from `BaseService` to the unified interface.

<a id="patrón-recomendado-para-agregar-una-herramienta"></a>
## Recommended pattern for adding a tool
1) Implement/use a `BaseService` (if applicable)
2) Create an adapter (if it does not fit in `BaseServiceAdapter`)
3) Define minimal capabilities (or allow auto-discovery)
4) Ensure health check

<a id="riesgos-comunes"></a>
## Common risks
- Heavy imports: prefer lazy imports inside methods.
- Timeouts: adjust per action/service.
- Circuit breaker: prevent it from opening due to "expected" failures (e.g. optional dependencies).
