> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

t = phase_timer()
t.start()
t.stop("analysis")  # increments histogram + atlas_phase_count_analysis
<a id="observabilidad-axiom-actualizado"></a>
# AXIOM Observability (Updated)

Lightweight Prometheus-style implementation in `app/observability/metrics.py` (no external dependencies) with support for:
- Counters, Histograms, Gauges
- Optional labels (phase, domain)
- HELP / TYPE per metric
- Injectable time provider for deterministic tests
- Backward compatibility with existing flat names

Main Prometheus endpoint: `/metrics` (standard exposition format).

Temporary alias (deprecated): `/metrics_prom` (responds the same as `/metrics` and adds headers `Deprecation: true`, `Sunset: 2025-12-31`, `Warning: 299`, and `Link: </metrics>; rel=successor-version`).

Legacy JSON summary (for compatibility): `/metrics_summary`.

<a id="arquitectura-interna-resumen"></a>
## Internal Architecture (Summary)
In-memory structures protected by RLock:
```
_COUNTERS[name][labelset] = float
_HISTOGRAMS[name][labelset] = [values]
_GAUGES[name][labelset] = float
```
Where `labelset` is an ordered tuple of pairs `(k,v)` for stability.

<a id="time-provider"></a>
### Time Provider
`set_time_provider(fn)` allows injecting a fake clock in tests (advance manually without `sleep`). `reset_time_provider()` restores `time.time`.

<a id="métricas-disponibles"></a>
## Available Metrics

<a id="1-contadores-legacy--nuevos"></a>
### 1. Counters (legacy + new)
- `atlas_feedback_total`
- `atlas_phase_count_<phase>` (legacy) – kept for previous scripts
- `atlas_phase_success_total` (global + series labeled by phase / domain)
- `atlas_phase_success_<phase>` (legacy per phase)
- `atlas_refinement_iterations_total`
- `atlas_refinement_cycles_total`
- `atlas_phase_failures_total` (flat + labeled `{phase,domain}`)
- `atlas_phase_failures_<phase>` (flat compatibility per phase)

<a id="2-gauges"></a>
### 2. Gauges
- `atlas_active_cycles` (global and with label `domain`) – increments when starting `start_research_cycle` and decrements on success or failure.
- `atlas_phase_success_ratio` (global and `{phase,domain}`) – dynamic ratio `success/(success+failures)` recalculated when closing a phase or recording a failure.
- `atlas_phase_active` ( `{phase,domain}` ) – 1 while a phase is running within a cycle, 0 upon completion (allows detecting overlaps or bottlenecks in parallel).

<a id="3-histogramas"></a>
### 3. Histograms
- `atlas_phase_duration_seconds` (legacy without labels + series labeled `{phase=...,domain=?}`)
	Buckets: `[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, +Inf]`
- `atlas_convergence_time_seconds` (flat + labeled `{phase="refinement",domain}` when it converges)
- `atlas_cycle_total_duration_seconds` (flat + `{domain}`) total time of a complete cycle.
- `atlas_refinement_iterations_per_cycle` (flat + `{domain}`) distribution of refinement iterations used until converging or ending the cycle.

Histogram format:
```
<name>_bucket{le="X"[,labels...]} <cumulativo>
<name>_bucket{le="+Inf"[,labels...]} <total>
<name>_sum{labels?} <suma>
<name>_count{labels?} <n>
```

<a id="ejemplos-de-salida"></a>
## Output Examples
```
<a id="help-atlas_phase_success_total-phase-successes-count"></a>
# HELP atlas_phase_success_total Phase successes count
<a id="type-atlas_phase_success_total-counter"></a>
# TYPE atlas_phase_success_total counter
atlas_phase_success_total 3
atlas_phase_success_total{phase="analysis"} 1
atlas_phase_success_total{phase="hypothesis_generation",domain="materials_science"} 2

<a id="help-atlas_active_cycles-active-research-cycles"></a>
# HELP atlas_active_cycles Active research cycles
<a id="type-atlas_active_cycles-gauge"></a>
# TYPE atlas_active_cycles gauge
atlas_active_cycles 1
atlas_active_cycles{domain="drug_discovery"} 1
```

<a id="uso-en-código"></a>
## Usage in Code
```python
from app.observability.metrics import phase_timer, inc, observe, gauge_inc

<a id="medir-fase-con-labels"></a>
# Medir fase con labels
timer = phase_timer(domain="materials_science")
timer.start()
<a id="-trabajo-"></a>
# ... trabajo ...
timer.stop("analysis")  # registra histogram (plano + etiquetado) y contadores de éxito

<a id="contadores-explícitos"></a>
# Contadores explícitos
inc("atlas_refinement_iterations_total")

<a id="gauge-pej-workers-en-cola"></a>
# Gauge (p.ej. workers en cola)
gauge_inc("atlas_active_cycles", 1, labels={"domain": "drug_discovery"})
gauge_inc("atlas_active_cycles", -1, labels={"domain": "drug_discovery"})

<a id="histograma-custom-si-se-agregaran-nuevos"></a>
# Histograma custom (si se agregaran nuevos)
observe("atlas_convergence_time_seconds", 2.34)
```

<a id="reset-en-tests"></a>
## Reset in Tests
`reset_metrics()` clears counters / gauges / histograms and resets the time provider.

<a id="compatibilidad-retro"></a>
## Backward Compatibility
- Original flat names are preserved (`atlas_phase_count_<phase>`, flat histogram, failure counters per phase) to avoid breaking previous dashboards or parsers.
- New users should prefer labeled series (`atlas_phase_success_total{phase="...",domain="..."}`).
- Future: labeled variants for failures and convergence will be introduced; then the flat format can be gradually deprecated.

<a id="estrategia-de-tests"></a>
## Testing Strategy
Current coverage (Sept 2025):
- `test_observability_metrics_endpoint.py`: validates endpoint `/metrics`, Prometheus format, HELP/TYPE, and deprecated alias.
- `test_observability_phase_active.py`: validates gauge `atlas_phase_active` for single phase and concurrency.
- `test_observability_histograms.py`: validates histograms `atlas_cycle_total_duration_seconds` and `atlas_refinement_iterations_per_cycle` (count, sum, bucket +Inf).
- `test_observability_convergence.py`: validates histogram `atlas_convergence_time_seconds` (count, sum, bucket +Inf).
- `test_observability_success_ratio.py` (preexisting): success ratio per phase.

Supporting infrastructure:
- Fixture `reset_metrics` (in `tests/conftest.py`) ensures isolation between tests by clearing counters/gauges/histograms.

Planned improvements:
- Use of `set_time_provider` for deterministic phase duration tests (avoid dependence on real time).
- (Completed) Cardinality / stress test to confirm the series limit per metric.
- Explore OTLP export (bridge) if integrated with OpenTelemetry.

<a id="política-de-deprecación"></a>
## Deprecation Policy
| Element | Status | Target Retirement | Replacement |
|----------|-------|-----------------|-----------|
| Endpoint `/metrics_prom` | Deprecated | 2025-12-31 (Sunset) | `/metrics` |
| Flat metrics `atlas_phase_count_<phase>` | Legacy | 2026-03-31 (proposed) | `atlas_phase_success_total{phase="..."}` |
| Flat metrics `atlas_phase_success_<phase>` | Legacy | 2026-03-31 (proposed) | `atlas_phase_success_total{phase="..."}` |
| Flat failure metrics per phase | Pending Deprecation | 2026-06-30 (tentative) | `atlas_phase_failures_total{phase="..."}` |

Headers applied to `/metrics_prom`:
- `Deprecation: true`
- `Sunset: 2025-12-31`
- `Warning: 299 - "Endpoint /metrics_prom deprecado; usar /metrics antes de la fecha Sunset"`
- `Link: </metrics>; rel=successor-version`

<a id="control-de-cardinalidad"></a>
## Cardinality Control
To prevent series explosion in Prometheus, a hard limit of 50 label combinations per metric is set (`_MAX_SERIES_PER_METRIC = 50`).
When exceeded, new labelsets are redirected to an overflow series with the label `{overflow="true"}`.

Example:
```
atlas_test_counter{overflow="true"} 17
```
This indicates that the limit was exceeded and additional increments are aggregated there.

Benefits:
- Prevents unbounded RAM growth.
- Protects scrape times.
- Simplifies alerting rules (no cascade of ephemeral series).

Label Design Best Practices:
- Keep cardinality of `phase` and `domain` << 10 each.
- Avoid including unique IDs (UUIDs, timestamps). Use buckets or categories.
- Audit dashboards to avoid depending on overflow values.

<a id="próximos-pasos-roadmap-observabilidad"></a>
## Next Steps (Observability Roadmap)
- (Completed) Standard endpoint `/metrics` (Prometheus exposition) + deprecated alias `/metrics_prom`.
- (Completed) Labels on failures and convergence; cycle and refinement iteration histograms.
- (Completed) Derived metrics: gauge `atlas_phase_success_ratio`.
- (Completed) Phase activity gauge `atlas_phase_active`.
- (Completed) Histogram tests (`atlas_cycle_total_duration_seconds`, `atlas_refinement_iterations_per_cycle`) and gauge `atlas_phase_active`.
- (Completed) Cardinality and series limit test + overflow.
- (Pending) Configurable retention limit for histogram values (current: 5000 last per series).
- (Pending) Integration with Prometheus Server / external scraping and example alerts (success SLOs per phase).
- (Pending) Traceability (trace_id) linking spans/phases and metrics.

<a id="trace-id--trazabilidad-de-requests"></a>
## Trace ID / Request Traceability

Status: PARTIAL - middleware+endpoint+logging ready, feedback pipeline COMPLETED basic, scientific decisions WITH trace_id.

Components:
- `TraceIdMiddleware` (`app/middleware/trace_id_middleware.py`):
	- Extracts `X-Trace-Id` if it comes in the request or generates a UUID v4.
	- Stores the value in `contextvars` and in `request.state.trace_id`.
	- Always injects the header `X-Trace-Id` in the response.
- Endpoint `/trace_id`: returns `{ "trace_id": <valor> }` for debugging.
- Logging: `LoggingMiddleware` adds `trace_id=<id>` at the end of each request log line (see change in `log_api_request`).

Design Decision (DO NOT use trace_id as a metric label):
- One trace per request would be unbounded cardinality → would violate the limit of 50 series/metric.
- Metrics add value in aggregation; per-request correlation is resolved in logs / tracing, not in time series.
- Future: if distributed tracing is required, an OpenTelemetry bridge (OTLP export) could be added without introducing `trace_id` as a Prometheus label.

Propagation to Feedback and Decision Logs (COMPLETED):
- Helper `log_decision_event()` in `logging_config.py` with optional parameter `trace_id`.
- `ResearchCycleManager._record_phase_feedback` includes trace_id via `get_current_trace_id()`.
- `PlausibilityScoringService.score_hypothesis` records scoring decision with trace_id.
- `hypothesis_prompt_ab_test.py` records A/B testing events with trace correlation.
- Tests added in `test_feedback_decision_trace_id.py` that verify propagation.

Recommended usage:
- Clients can pass their own `X-Trace-Id` to correlate external flows.
- If they do not send it, they receive a generated one and can read it from the response / logs.
- Search for `DecisionEvent:` in logs to find correlated scientific decisions.

Added tests:
- `test_trace_id.py`: header generation and propagation.
- `test_logging_trace_id.py`: ensures the log line contains `trace_id=`.
- `test_feedback_decision_trace_id.py`: verifies propagation in feedback/plausibility/A/B logs.

Next traceability steps:
1. ~~Propagate `trace_id` automatically to feedback hooks~~ ✅ COMPLETED
2. ~~Add an optional structured field in scientific logs~~ ✅ COMPLETED
3. (Optional) Lightweight span per phase (start/end) for a future bridge with a standard tracer.
4. (Optional) Trace debugging panel/dashboard unifying structured logs with trace_id.

<a id="relación-con-roadmap-general"></a>
## Relationship with the General Roadmap
The labeled metrics layer enables multi-domain analysis, KPI calculation (average time per phase, success rate), concurrency visibility (`atlas_phase_active`), and foundations for the system's self-optimization loops.
