> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="observabilidad-inicial-axiom--atlas"></a>
# Initial AXIOM / ATLAS Observability

This iteration introduces a lightweight layer of metrics and trace correlation without heavy external dependencies.

<a id="componentes"></a>
## Components
- `app/observability/metrics.py`: in-memory storage of counters and histograms (fixed buckets) and export in Prometheus format (`/metrics_prom`).
- `app/observability/trace.py`: util `get_or_create_trace` to assign a stable `trace_id` (uses `cycle_id` as fallback) to feedback and logs.
- Integration in `research_cycle_manager._record_phase_feedback`: increments `atlas_feedback_total` for each recorded metric (accuracy/coherence/validity).
- Endpoint `/metrics_prom`: exposes records in Prometheus text (`text/plain; version=0.0.4`).

<a id="métricas-expuestas"></a>
## Exposed Metrics
- `atlas_feedback_total` (counter): total number of feedback events (summing types).
- `atlas_phase_duration_seconds` (histogram placeholder): pending instrumentation of start/stop per phase (timer util available `PhaseTimer`).
- `atlas_phase_count_<phase>` (counter): count of timed phases (when the timer is integrated into each phase).

<a id="próximos-pasos-sugeridos"></a>
## Suggested Next Steps
1. Instrument the duration of each phase (`_phase_hypothesis_generation`, `_phase_analysis`, etc.) using `PhaseTimer`.
2. Add gauges for active vs completed cycles.
3. Export policy engine metrics (approve/reject decisions by state).
4. Evaluate migration to the official `prometheus_client` client if advanced external collection is required.
5. Add trace_id to structured logs (logger extra fields) and potential future migration to OpenTelemetry.

<a id="-opentelemetry-opcional"></a>
## 🌐 OpenTelemetry (optional)
- Enablement via settings/env: `ENABLE_OTEL=true` or standard OTEL variables (`OTEL_ENABLED=true`).
- `main.py` initializes OTEL defensively (`init_tracing(app)`), instrumenting FastAPI and httpx when the dependencies are available.
- Recommended exporter: OTLP HTTP (`OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318`).

<a id="variables-de-entorno-sugeridas"></a>
### Suggested environment variables
```
OTEL_ENABLED=true
OTEL_SERVICE_NAME=axiom-meta4
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
```

<a id="-dashboard-base-en-grafana-sugerido"></a>
## 📊 Base dashboard in Grafana (suggested)
Minimum panels:
- p50/p95/p99 latency per endpoint (histogram/summary of `http_server_request_duration_seconds` if using OTEL->Prometheus or equivalent own metrics).
- Error rate (5xx/4xx per endpoint and global).
- Cache hit ratio (if exposed; from `app/observability/metrics.py` or Redis stats).
- Active cycles and success ratio (`atlas_phase_active`, `atlas_phase_success_ratio`).

Quick steps:
1. Configure Prometheus to scrape `/metrics`.
2. Import example dashboard JSON: `docs/dashboards/grafana_base.json`.
3. Add deployment annotations to correlate changes with metrics.

<a id="uso-rápido"></a>
## Quick Use
GET `/metrics_prom` returns Prometheus text; partial example:
```
<a id="help-atlas_feedback_total-total-feedback-events"></a>
# HELP atlas_feedback_total Total feedback events
<a id="type-atlas_feedback_total-counter"></a>
# TYPE atlas_feedback_total counter
atlas_feedback_total 3
<a id="help-atlas_phase_duration_seconds-duration-of-research-cycle-phases-seconds"></a>
# HELP atlas_phase_duration_seconds Duration of research cycle phases (seconds)
<a id="type-atlas_phase_duration_seconds-histogram"></a>
# TYPE atlas_phase_duration_seconds histogram
atlas_phase_duration_seconds_bucket{le="0.01"} 0
...
```

<a id="limitaciones"></a>
## Limitations
- In-memory persistence (restart resets counters).
- No labels yet; it can be extended with the `name__labelValue` convention if needed before the official library.
- Manual histogram: fixed buckets; not adaptive.

---
Last updated: initial instrumentation (trace + feedback counter + Prometheus endpoint).
