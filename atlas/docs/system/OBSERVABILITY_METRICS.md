t = phase_timer()
t.start()
t.stop("analysis")  # incrementa histogram + atlas_phase_count_analysis
# Observabilidad AXIOM (Actualizado)

Implementación ligera tipo Prometheus en `app/observability/metrics.py` (sin dependencias externas) con soporte de:
- Counters, Histograms, Gauges
- Labels opcionales (fase, dominio)
- HELP / TYPE por métrica
- Proveedor de tiempo inyectable para tests deterministas
- Compatibilidad retro con nombres planos existentes

Endpoint principal Prometheus: `/metrics` (formato exposition estándar).

Alias temporal (deprecado): `/metrics_prom` (responde igual que `/metrics` y añade cabeceras `Deprecation: true`, `Sunset: 2025-12-31`, `Warning: 299` y `Link: </metrics>; rel=successor-version`).

Resumen JSON legacy (para compatibilidad): `/metrics_summary`.

## Arquitectura Interna (Resumen)
Estructuras en memoria protegidas por RLock:
```
_COUNTERS[name][labelset] = float
_HISTOGRAMS[name][labelset] = [values]
_GAUGES[name][labelset] = float
```
Donde `labelset` es tupla ordenada de pares `(k,v)` para estabilidad.

### Time Provider
`set_time_provider(fn)` permite inyectar un reloj falso en tests (avanzar manualmente sin `sleep`). `reset_time_provider()` restaura `time.time`.

## Métricas Disponibles

### 1. Contadores (legacy + nuevos)
- `atlas_feedback_total`
- `atlas_phase_count_<phase>` (legacy) – se mantiene para scripts previos
- `atlas_phase_success_total` (global + series etiquetadas por fase / dominio)
- `atlas_phase_success_<phase>` (legacy por fase)
- `atlas_refinement_iterations_total`
- `atlas_refinement_cycles_total`
- `atlas_phase_failures_total` (plano + etiquetado `{phase,domain}`)
- `atlas_phase_failures_<phase>` (compat plano por fase)

### 2. Gauges
- `atlas_active_cycles` (global y con label `domain`) – incrementa al iniciar `start_research_cycle` y decrementa en éxito o fallo.
- `atlas_phase_success_ratio` (global y `{phase,domain}`) – ratio dinámico `success/(success+failures)` recalculado al cerrar una fase o registrar fallo.
- `atlas_phase_active` ( `{phase,domain}` ) – 1 mientras una fase está en ejecución dentro de un ciclo, 0 al finalizar (permite detectar solapamientos o cuellos de botella en paralelo).

### 3. Histogramas
- `atlas_phase_duration_seconds` (legacy sin labels + serie etiquetada `{phase=...,domain=?}`)
	Buckets: `[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, +Inf]`
- `atlas_convergence_time_seconds` (plano + etiquetado `{phase="refinement",domain}` cuando converge)
- `atlas_cycle_total_duration_seconds` (plano + `{domain}`) tiempo total de un ciclo completo.
- `atlas_refinement_iterations_per_cycle` (plano + `{domain}`) distribución de iteraciones de refinamiento empleadas hasta converger o terminar el ciclo.

Formato de histogramas:
```
<name>_bucket{le="X"[,labels...]} <cumulativo>
<name>_bucket{le="+Inf"[,labels...]} <total>
<name>_sum{labels?} <suma>
<name>_count{labels?} <n>
```

## Ejemplos de Salida
```
# HELP atlas_phase_success_total Phase successes count
# TYPE atlas_phase_success_total counter
atlas_phase_success_total 3
atlas_phase_success_total{phase="analysis"} 1
atlas_phase_success_total{phase="hypothesis_generation",domain="materials_science"} 2

# HELP atlas_active_cycles Active research cycles
# TYPE atlas_active_cycles gauge
atlas_active_cycles 1
atlas_active_cycles{domain="drug_discovery"} 1
```

## Uso en Código
```python
from app.observability.metrics import phase_timer, inc, observe, gauge_inc

# Medir fase con labels
timer = phase_timer(domain="materials_science")
timer.start()
# ... trabajo ...
timer.stop("analysis")  # registra histogram (plano + etiquetado) y contadores de éxito

# Contadores explícitos
inc("atlas_refinement_iterations_total")

# Gauge (p.ej. workers en cola)
gauge_inc("atlas_active_cycles", 1, labels={"domain": "drug_discovery"})
gauge_inc("atlas_active_cycles", -1, labels={"domain": "drug_discovery"})

# Histograma custom (si se agregaran nuevos)
observe("atlas_convergence_time_seconds", 2.34)
```

## Reset en Tests
`reset_metrics()` limpia counters / gauges / histograms y restablece el time provider.

## Compatibilidad Retro
- Se conservan nombres planos originales (`atlas_phase_count_<phase>`, histogram plano, contadores de fallo por fase) para no romper dashboards o parsers previos.
- Nuevos usuarios deben preferir series etiquetadas (`atlas_phase_success_total{phase="...",domain="..."}`).
- Futuro: se introducirán variantes etiquetadas para failures y convergence; luego se podrá deprecar gradualmente el formato plano.

## Estrategia de Tests
Cobertura actual (sept 2025):
- `test_observability_metrics_endpoint.py`: valida endpoint `/metrics`, formato Prometheus, HELP/TYPE y alias deprecado.
- `test_observability_phase_active.py`: valida gauge `atlas_phase_active` para fase única y concurrencia.
- `test_observability_histograms.py`: valida histogramas `atlas_cycle_total_duration_seconds` y `atlas_refinement_iterations_per_cycle` (count, sum, bucket +Inf).
- `test_observability_convergence.py`: valida histogram `atlas_convergence_time_seconds` (count, sum, bucket +Inf).
- `test_observability_success_ratio.py` (preexistente): ratio de éxito por fase.

Infra de soporte:
- Fixture `reset_metrics` (en `tests/conftest.py`) asegura aislamiento entre pruebas limpiando counters/gauges/histograms.

Planned improvements:
- Uso de `set_time_provider` para tests deterministas de duración de fases (evitar dependencia de tiempo real).
- (Completado) Test de cardinalidad / stress para confirmar límite de series por métrica.
- Explorar export OTLP (bridge) si se integra con OpenTelemetry.

## Política de Deprecación
| Elemento | Estado | Retiro Objetivo | Sustituto |
|----------|-------|-----------------|-----------|
| Endpoint `/metrics_prom` | Deprecated | 2025-12-31 (Sunset) | `/metrics` |
| Métricas planas `atlas_phase_count_<phase>` | Legacy | 2026-03-31 (propuesto) | `atlas_phase_success_total{phase="..."}` |
| Métricas planas `atlas_phase_success_<phase>` | Legacy | 2026-03-31 (propuesto) | `atlas_phase_success_total{phase="..."}` |
| Métricas planas de fallos por fase | Pending Deprecation | 2026-06-30 (tentativo) | `atlas_phase_failures_total{phase="..."}` |

Headers aplicados a `/metrics_prom`:
- `Deprecation: true`
- `Sunset: 2025-12-31`
- `Warning: 299 - "Endpoint /metrics_prom deprecado; usar /metrics antes de la fecha Sunset"`
- `Link: </metrics>; rel=successor-version`

## Control de Cardinalidad
Para prevenir explosión de series en Prometheus se fija un límite duro de 50 combinaciones de labels por métrica (`_MAX_SERIES_PER_METRIC = 50`).
Cuando se excede, los nuevos labelsets se redirigen a una serie de overflow con la etiqueta `{overflow="true"}`.

Ejemplo:
```
atlas_test_counter{overflow="true"} 17
```
Esto indica que se superó el límite y los incrementos adicionales se agregan ahí.

Beneficios:
- Evita crecimiento no acotado de RAM.
- Protege tiempos de scrape.
- Simplifica reglas de alerting (no hay cascada de series efímeras).

Buenas Prácticas de Diseño de Labels:
- Mantener cardinalidad de `phase` y `domain` << 10 cada uno.
- Evitar incluir IDs únicos (UUIDs, timestamps). Usar buckets o categorías.
- Auditar dashboards para no depender de valores overflow.

## Próximos Pasos (Roadmap Observabilidad)
- (Completado) Endpoint estándar `/metrics` (Prometheus exposition) + alias `/metrics_prom` deprecado.
- (Completado) Labels en failures y convergencia; histogramas ciclo e iteraciones de refinamiento.
- (Completado) Métricas derivadas: gauge `atlas_phase_success_ratio`.
- (Completado) Gauge de actividad por fase `atlas_phase_active`.
- (Completado) Tests histogramas (`atlas_cycle_total_duration_seconds`, `atlas_refinement_iterations_per_cycle`) y gauge `atlas_phase_active`.
- (Completado) Test de cardinalidad y límite de series + overflow.
- (Pendiente) Límite configurable de retención de valores en histogramas (actual: 5000 últimos por serie).
- (Pendiente) Integración con Prometheus Server / scraping externo y ejemplo de alertas (SLOs de éxito por fase).
- (Pendiente) Trazabilidad (trace_id) enlazando spans/fases y metrics.

## Trace ID / Trazabilidad de Requests

Estado: PARCIAL - middleware+endpoint+logging listo, feedback pipeline COMPLETADO básico, decisiones científicas CON trace_id.

Componentes:
- `TraceIdMiddleware` (`app/middleware/trace_id_middleware.py`):
	- Extrae `X-Trace-Id` si viene en la petición o genera un UUID v4.
	- Almacena el valor en `contextvars` y en `request.state.trace_id`.
	- Inyecta siempre el header `X-Trace-Id` en la respuesta.
- Endpoint `/trace_id`: devuelve `{ "trace_id": <valor> }` para debugging.
- Logging: `LoggingMiddleware` añade `trace_id=<id>` al final de cada línea de log de request (ver cambio en `log_api_request`).

Decisión de Diseño (NO usar trace_id como label métrico):
- Un trace por request sería cardinalidad no acotada → violaría el límite de 50 series/metric.
- Métricas agregan valor en agregación; la correlación per-request se resuelve en logs / tracing, no en time series.
- Futuro: si se requiere tracing distribuido se podría añadir puente OpenTelemetry (export OTLP) sin introducir `trace_id` como label Prometheus.

Propagación a Feedback y Decision Logs (COMPLETADA):
- Helper `log_decision_event()` en `logging_config.py` con parámetro `trace_id` opcional.
- `ResearchCycleManager._record_phase_feedback` incluye trace_id vía `get_current_trace_id()`.
- `PlausibilityScoringService.score_hypothesis` registra decisión de scoring con trace_id.
- `hypothesis_prompt_ab_test.py` registra eventos de A/B testing con correlación trace.
- Tests añadidos en `test_feedback_decision_trace_id.py` que verifican propagación.

Uso recomendado:
- Clientes pueden pasar un `X-Trace-Id` propio para correlacionar flujos externos.
- Si no lo envían reciben uno generado y pueden leerlo de la respuesta / logs.
- Buscar `DecisionEvent:` en logs para encontrar decisiones científicas correlacionadas.

Tests añadidos:
- `test_trace_id.py`: generación y propagación de header.
- `test_logging_trace_id.py`: asegura que la línea de log contiene `trace_id=`.
- `test_feedback_decision_trace_id.py`: verifica propagación en feedback/plausibility/A/B logs.

Próximos pasos trazabilidad:
1. ~~Propagar `trace_id` automáticamente a hooks de feedback~~ ✅ COMPLETADO
2. ~~Añadir un campo estructurado opcional en logs científicos~~ ✅ COMPLETADO
3. (Opcional) Span ligero por fase (inicio/fin) para puente futuro con un tracer estándar.
4. (Opcional) Panel/dashboard de trace debugging unificando logs estructurados con trace_id.

## Relación con Roadmap General
La capa de métricas etiquetadas habilita análisis multi-dominio, cálculo de KPIs (tiempo medio por fase, tasa de éxito), visibilidad de simultaneidad (`atlas_phase_active`) y cimientos para bucles de auto-optimización del sistema.
