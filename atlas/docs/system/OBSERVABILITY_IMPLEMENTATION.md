# Observabilidad Inicial AXIOM / ATLAS

Esta iteración introduce capa ligera de métricas y correlación de trazas sin dependencias externas pesadas.

## Componentes
- `app/observability/metrics.py`: almacenamiento in-memory de counters e histogramas (buckets fijos) y export en formato Prometheus (`/metrics_prom`).
- `app/observability/trace.py`: util `get_or_create_trace` para asignar `trace_id` estable (usa `cycle_id` como fallback) a feedback y logs.
- Integración en `research_cycle_manager._record_phase_feedback`: incrementa `atlas_feedback_total` por cada métrica registrada (accuracy/coherence/validity).
- Endpoint `/metrics_prom`: expone registros en texto Prometheus (`text/plain; version=0.0.4`).

## Métricas Expuestas
- `atlas_feedback_total` (counter): número total de feedback events (sumando tipos).
- `atlas_phase_duration_seconds` (histogram placeholder): pendiente de instrumentar start/stop por fase (timer util disponible `PhaseTimer`).
- `atlas_phase_count_<phase>` (counter): recuento de fases cronometradas (cuando se integre el timer en cada fase).

## Próximos Pasos Sugeridos
1. Instrumentar duración de cada fase (`_phase_hypothesis_generation`, `_phase_analysis`, etc.) usando `PhaseTimer`.
2. Añadir gauges de ciclos activos vs completados.
3. Exportar métricas del policy engine (decisiones approve/reject por estado).
4. Evaluar migración a cliente oficial `prometheus_client` si se requiere recolección externa avanzada.
5. Añadir trace_id a logs estructurados (logger extra fields) y potencial futura migración a OpenTelemetry.

## 🌐 OpenTelemetry (opcional)
- Habilitación por settings/env: `ENABLE_OTEL=true` o variables OTEL estándar (`OTEL_ENABLED=true`).
- `main.py` inicializa OTEL defensivamente (`init_tracing(app)`), instrumentando FastAPI y httpx cuando las dependencias están disponibles.
- Exportador recomendado: OTLP HTTP (`OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318`).

### Variables de entorno sugeridas
```
OTEL_ENABLED=true
OTEL_SERVICE_NAME=axiom-meta4
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
```

## 📊 Dashboard base en Grafana (sugerido)
Paneles mínimos:
- Latencia p50/p95/p99 por endpoint (histograma/summary de `http_server_request_duration_seconds` si usa OTEL->Prometheus o métricas equivalentes propias).
- Error rate (5xx/4xx por endpoint y global).
- Cache hit ratio (si expuesto; de `app/observability/metrics.py` o Redis stats).
- Active cycles y success ratio (`atlas_phase_active`, `atlas_phase_success_ratio`).

Pasos rápidos:
1. Configurar Prometheus para scrapear `/metrics`.
2. Importar dashboard JSON de ejemplo: `docs/dashboards/grafana_base.json`.
3. Añadir anotaciones de despliegue para correlacionar cambios con métricas.

## Uso Rápido
GET `/metrics_prom` devuelve texto Prometheus; ejemplo parcial:
```
# HELP atlas_feedback_total Total feedback events
# TYPE atlas_feedback_total counter
atlas_feedback_total 3
# HELP atlas_phase_duration_seconds Duration of research cycle phases (seconds)
# TYPE atlas_phase_duration_seconds histogram
atlas_phase_duration_seconds_bucket{le="0.01"} 0
...
```

## Limitaciones
- Persistencia in-memory (reinicio reinicia contadores).
- Sin etiquetas (labels) aún; se puede extender con convención `name__labelValue` si se necesita antes de librería oficial.
- Histograma manual: buckets fijos; no adaptativo.

---
Última actualización: instrumentación inicial (trace + feedback counter + endpoint Prometheus).
