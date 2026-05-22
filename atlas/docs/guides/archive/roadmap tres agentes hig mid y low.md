### Roadmap unificado (fusión de planes) y dividido para 3 agentes concurrentes: high, mid, low

Objetivo: convertir AXIOM META 4 en un laboratorio autónomo multidominio, con seguridad de clase producción, reproducibilidad verificable, orquestación inteligente y publicación automática, manteniendo SLO/SLI y gobernanza científica.

Principios
- Seguridad/observabilidad primero; reproducibilidad por defecto; contratos y linaje como gates.
- APIs versionadas y estables; validaciones de datos y artefactos; CI/CD con “calidad-ciencia-seguridad”.
- Trabajo en paralelo sin colisiones: ownership claro por componente, PRs pequeños y contratos previamente acordados.

KPIs/SLOs (meta)
- Seguridad: 100% endpoints con OAuth2/JWT; 0 findings críticos en bandit/pip-audit.
- Reproducibilidad: ≥90% experimentos con bundle completo y hash verificado; ≥95% hash‑match en réplicas.
- Observabilidad: 100% requests con trace_id; p99 < 500 ms (core); MTTR < 30 min.
- Coste: −20% coste medio/job con SLOs estables.
- Ciencia: ≥3 workflows multidominio/mes con publicación reproducible firmada.

Reglas de colaboración y anti‑conflicto
- Branches por agente: `feature/high-*`, `feature/mid-*`, `feature/low-*`.
- Ownership por directorio:
  - high: `app/middleware/`, `app/observability/` y `app/metrics*`, `app/security*.py`, `main.py`, `app/routers/*` (sólo versionado/seguridad), `monitoring/`, `kubernetes/`, `nginx/`.
  - mid: `pipeline_v4.py`, `weak_label*_v4.py`, `pipeline_metadata_v4.py`, `mlruns/`, `app/services/*scheduler*`, `app/routers/workflow_orchestration.py`, `app/services/mlflow_registry*`.
  - low: `app/services/sandbox*`, `app/services/integrity*`, `app/routers/integrity*.py`, `publications/`, `docs/`, `.github/workflows/`, `scripts/` (validadores/replicator).
- Interfaces comunes:
  - Contratos Pydantic para artefactos (definidos por mid, usados por todos) en `app/models/artifacts/*.py`.
  - API v1 (definida por high): rutas y JSONSchema; tests de contrato por low.
  - Manifesto de artefactos (definido por mid en `models/manifest.schema.json`), verificado por low.

Entregables por fases y asignación paralela

Fase 0 (Semanas 0–2) — Seguridad, API v1, OTel base, metadata y CI mínima
- high (plataforma, seguridad, API)
  - Versionar API en `/api/v1` en `main.py`; alias temporal y headers de deprecación.
  - OAuth2/JWT + scopes (RBAC/ABAC) en `app/security.py`; protección de `plausibility`, `scheduler`, `sandbox`, `mlflow-registry`.
  - Middlewares: CSP estricta, HSTS, `X-Content-Type-Options`, `Referrer-Policy`; límites por ruta; validación homogénea Pydantic v2.
  - OpenTelemetry (traces) en FastAPI + httpx; export Prometheus; dashboard base.
  - Criterios: 100% endpoints críticos tras auth; 100% requests con trace_id; OpenAPI v1 estable.
- mid (datos/ML y reproducibilidad mínima)
  - Ampliar `pipeline_metadata_v4.py` con Brier, ECE, PR/ROC, hyperparams y seeds; HMAC del JSON.
  - Pydantic modelos iniciales de artefactos: `WeakLabelRecord`, `EnsembleRecord`.
  - Calibración isotónica/Platt y grid de pesos para ensemble; logging a MLflow.
  - Criterios: metadata firmada en `models/`; mejora ECE/Brier registrada; artefactos validados por schema.
- low (CI/CD, validadores, docs)
  - CI mínima en `.github/workflows/`: ruff/flake8, pytest (unit/integration), cobertura con gate, bandit, pip‑audit, build imagen.
  - Script validador CLI de manifestos en `scripts/validate_manifest.py`; aplicar a 1–2 modelos en `models/`.
  - README como portal + aviso de versionado v1; doc rápida de auth y trazas.
  - Criterios: pipeline CI rojo ante fallos; 2 modelos con manifest validado.

Fase 1 (Semanas 3–6) — Orquestación reproducible (DAG), DVC, MLflow “source of truth”, contratos/validación
- high (observabilidad y API estable)
  - Métricas de SLIs en `/metrics`: latencias, error rate, cache hit; panel Grafana base por dominio.
  - Contract publishing: JSONSchema por endpoint v1 en `docs/API_REFERENCE.md`; headers de Sunset para legacy.
  - Criterios: dashboards operativos; schemas publicados y probados.
- mid (DAG/Artifact Registry/DVC/MLflow)
  - Extender `Experiment Scheduler` para DAG con dependencias, retries/backoff y checkpointing; estado persistente.
  - Artifact map unificado: path, schema, hash, productor, commit, parámetros (guardar en `models/artifact_map.json`).
  - Enforcement DVC en datasets/embeddings/índices (targets críticos) y snapshots por step; integración MLflow (params, runs, stage transitions por métrica).
  - Criterios: reanudación idempotente; artifact map generado/validado; DVC lock actualizado; promoción a Staging automática.
- low (validación, contratos, CI reforzada)
  - Great Expectations (o validadores propios) en puntos críticos; emitir `.fail.json` con diagnóstico.
  - Contract tests (compatibilidad hacia atrás) y fuzzing de OpenAPI (Schemathesis).
  - CronJobs K8s para ejecuciones periódicas del pipeline “smoke”.
  - Criterios: abortos explicables antes de train; tests de contrato verdes; cron activo.

Fase 2 (Semanas 7–10) — Linaje PROV, firmas avanzadas (Merkle/Ed25519), hardening sandbox, observabilidad avanzada
- high (observabilidad distribuida y sistema)
  - OTel completo (traces/metrics/logs) con Loki/Tempo; correlación API→Scheduler→Sandbox→DB.
  - Endpoints de sistema: `/api/system/lineage` (summary), `/api/system/slo` (SLOs actuales).
  - Criterios: correlación end‑to‑end visible; endpoints de sistema activos.
- mid (PROV/linaje y endpoints)
  - Servicio de proveniencia: grafo PROV-like con nodos/edges de pasos; API `GET /api/provenance/graph`, `GET /api/provenance/lineage/{artifact}`; visualización (pyvis/vis) en `monitoring/`.
  - Criterios: linaje navegable de ingesta→publicación; pruebas integradas.
- low (integridad avanzada y sandbox)
  - Merkle tree y firmas Ed25519 para paquetes en `publications/`; verificación en runtime y en CI; opción de anclaje (OpenTimestamps).
  - Hardening sandbox: gVisor/Firecracker o contenedores rootless, seccomp/apparmor, filesystem RO, cgroups por job; fuzz de endpoints “code”.
  - Criterios: verificación obligatoria antes de inferencia; tests de escape negativos; fuzz suite estable.

Fase 3 (Semanas 11–16) — Laboratorio autónomo: Multi‑Agente + Orchestrator + KG, policy‑aware scheduling, publicaciones automáticas
- high (policy-aware scheduling y recursos)
  - Función de costo multiobjetivo (plausibilidad, riesgo/ética, coste GPU, impacto). Quotas por tenant y deadline scheduling; SLO por job.
  - GPU cost-aware: perfiles por job, preferencia spot/preemptible, autoescalado.
  - Criterios: reducción de coste >20% manteniendo SLOs; colas por prioridad visibles.
- mid (loop científico y publicación)
  - Integrar Multi‑Agente + Orchestrator + Knowledge Graph: hipótesis → plausibilidad → scheduler → sandbox → análisis → publicación → realimentación (KG y prompts).
  - Preregistro antes de ejecución (hipótesis/criterios/plan de análisis) y “Replicability Checker” (re‑run limpio + comparación de hashes/métricas).
  - Criterios: ≥3 workflows/mes E2E con paquetes reproducibles; replicator ≥90% match.
- low (publication-ready outputs, gobernanza y CI/CD extendido)
  - Plantillas LaTeX + anexos reproducibles; DOI interno opcional. 
  - CI/CD con gates científicos (calibración mínima, drift thresholds) y despliegues progresivos (canary/blue-green) en routers críticos (`plausibility`, `scheduler`, `sandbox`).
  - Criterios: paquetes listos para arXiv/Zenodo; gates activos; despliegues sin downtime.

Continuo (operaciones y excelencia)
- SLO/SLI/Alerting: latencia p99, éxito, integridad ≥0.95, reproducibilidad ≥0.9, coste/job. Runbooks.
- Auditorías periódicas (seguridad/ética/bias), rotación de claves y gestión de secretos, backups/DR.
- Gobernanza/documentación versionada: `docs/INDEX.md` con estado stable/experimental/deprecated; completar `docs/EXECUTIVE_SUMMARY_LICENSE_STRATEGY.md` y `docs/OPEN_SOURCE_GOVERNANCE_STRATEGY.md`.

Quick wins (7 días)
- high: `/api/v1` + OAuth2/JWT básico (proteger 3 routers), CSP/HSTS y OTel traces base; dashboard inicial.
- mid: `pipeline_metadata_v4.py` con métricas de calibración + HMAC; Pydantic para weak/ensemble; calibración isotónica; logging MLflow.
- low: CI mínima (lint+tests+seguridad+build), validador de manifiestos en `scripts/`, 2 modelos con manifest verificado, README portal y aviso de versionado.

Matriz de aceptación (resumen)
- F0: 100% endpoints críticos con auth; trazas con `trace_id`; CI roja ante fallos; metadata firmada y artefactos validados.
- F1: DAG con checkpointing y reanudación; artifact map+DVC; promoción MLflow por métrica; validaciones de datos + contract tests.
- F2: Grafo PROV + endpoints/visual; firmas Ed25519+Merkle con verificación; sandbox endurecido y fuzz estable; OTel completo.
- F3: ≥3 workflows/mes E2E con preregistro, peer‑review automático y replicabilidad ≥90%; scheduling policy‑aware; publicación LaTeX.

Riesgos y mitigación
- Rupturas de API: alias y deprecations; contract tests.
- Complejidad DVC/datos: empezar por pipelines críticos; storage remoto eficiente.
- Overhead OTel/sandbox: sampling y modos por entorno; perfiles de aislamiento configurables.
- Coste GPU: perfiles por job y preferencia spot; límites por tenant.

Asignación a componentes (mapeo rápido)
- high:
  - `main.py` (v1 y middlewares), `app/security.py`, `app/middleware/*`, `app/metrics.py`, `app/observability/*`, `monitoring/*`, `kubernetes/*`, `nginx/*`.
- mid:
  - `pipeline_v4.py`, `weak_label*_v4.py`, `pipeline_metadata_v4.py`, `mlruns/`, `app/services/*scheduler*`, `app/routers/workflow_orchestration.py`, `app/services/mlflow_registry*`, `app/models/artifacts/*.py`.
- low:
  - `app/services/sandbox*`, `app/services/integrity*`, `app/routers/integrity*.py`, `publications/*`, `docs/*`, `.github/workflows/*`, `scripts/*` (validador/replicator).

Handoffs y sincronización (evitar estorbo)
- Definición de contratos (mid) en `app/models/artifacts/*.py` y `models/manifest.schema.json` antes de que high/low dependan.
- high publica `OpenAPI v1` y JSONSchema; low arma contract tests y fuzz; mid usa schemas en orquestación.
- Puntos de integración semanales: 
  - Lunes: contratos/schemas y cambios de API.
  - Miércoles: validaciones/CI y avances DAG/observabilidad.
  - Viernes: demo E2E “smoke” y revisión de métricas.

Con este plan, los tres agentes trabajan en paralelo con ownership claro, interfaces estables y criterios de aceptación medibles, fusionando tu análisis, el documento `analisisgpt5normal.md` y el `raodmap gpt5midhigh.md` para ejecutar una transformación ordenada y efectiva hacia un laboratorio autónomo científico.

---

Actualización de progreso (Agente high)
- Implementado middleware de versionado `VersionPrefixMiddleware` para aceptar `/api/v1/*` y marcar `/api/*` como alias en deprecación (headers Deprecation/Sunset/Link). Integrado en `main.py` antes del resto de middlewares.
- Endurecidas cabeceras de seguridad base (HSTS, X-Content-Type-Options, X-Frame-Options, X-XSS-Protection). CSP mantenida compatible con tests (`default-src 'self'`).
- Añadido soporte de JWT (HS256) y dependencia `require_scopes` en `app/security.py` para scopes por endpoint.
- Protegidos endpoints críticos del Scheduler con scopes: `scheduler` y `scheduler:admin` en `app/routers/experiment_scheduler.py`.
- Protegido `sandbox_executor` con scope `sandbox` y `mlflow_registry` con `mlflow:read|write|admin`; `scientific_evaluation` con `sci-eval`.
- Añadida dependencia `PyJWT==2.9.0` en `requirements.txt`.
- Integración OTel base (traces FastAPI + httpx) opcional por env; script `scripts/generate_openapi.py` para exportar `docs/openapi_v1.json`.
- Actualizada `docs/API_REFERENCE.md`: base URL v1 y esquema de autenticación con scopes.
- Guía de observabilidad extendida en `docs/OBSERVABILITY_IMPLEMENTATION.md` (habilitación OTEL + dashboard base Grafana).
- Script `scripts/generate_schemas_from_openapi.py` para exportar JSONSchema por endpoint a `docs/schemas/`.

Próximos (Agente high)
- Publicar OpenAPI v1 con JSONSchema por endpoint en `docs/API_REFERENCE.md`.
- Publicar OpenAPI v1 con JSONSchema por endpoint en `docs/API_REFERENCE.md`.
- Instrumentación OTel base (traces FastAPI + httpx) y dashboard inicial (latencia p50/p95/p99, error rate, cache hit).
 - Crear dashboard base en Grafana (latencia, errores, cache hit) y guía rápida en `docs/OBSERVABILITY_IMPLEMENTATION.md`.
 - Exportar JSONSchema por endpoint (listo el script) y enlazar ejemplos en `docs/API_REFERENCE.md`.

---

Actualización de progreso (Agente mid)
- pipeline_metadata_v4.py fortalecido con métricas de calibración y reproducibilidad:
  - Cálculo de ECE, Brier Score, PR AUC y ROC AUC para modelo base, Platt scaling y regresión isotónica.
  - Calibradores Platt e Isotónico entrenados y guardados en models/calibrated/ (platt_calibrator.pkl, isotonic_calibrator.pkl).
  - Logging a MLflow de: parámetros de entorno (commit, plataforma, versiones), métricas de conteo/clases, métricas de CV (si existen), métricas de calibración y, ahora, hiperparámetros del modelo y seed reproducible.
  - HMAC-SHA256 agregado al JSON final para integridad del metadata.
  - Generación de models/artifact_map.json con información de artefactos (path, hash, productor, commit, parámetros) y validación ligera inline del archivo.
  - Reubicación de validate_artifact_map_file antes de main() para disponibilidad temprana y evitar duplicados.
- Modelos Pydantic iniciales creados para artefactos (WeakLabelRecord, EnsembleRecord) y uso de tracking de confianza/fuentes en weak labeling.
- Integración inicial con MLflow activa (experimento plausibility_pipeline_v4) y registro de run_id en metadata cuando aplica.
- Soporte/servicios de DVC presentes; integración en pipeline_v4 ahora con snapshots por paso y enforcement para artefactos críticos (ENRICHED, EMBEDDINGS, WEAK, ENSEMBLE_WEAK). Si falla el snapshot en un target crítico, el pipeline aborta de forma segura tras persistir PROV/DAG.
- Servicio de Provenance y endpoints HTTP disponibles: GET /api/provenance/experiments y GET /api/provenance/experiment/{experiment_id} con opción render_html.
- Ensemble de weak labels implementado y validado end-to-end:
  - Grid de pesos para combinaciones base/no_cits con selección por métrica; logging completo a MLflow (pesos, métricas por fold y globales) y parámetros de umbral.
  - Artefacto de salida generado en `data/plausibility_training_v4_weak_labels_ensemble.parquet`; actualización del `models/artifact_map.json` con la entrada `ENSEMBLE_WEAK` y rutas en `pipeline_v4.py` alineadas.
  - Ejecución de validación sin labels manuales: fallback a promedio 0.5/0.5; guardado con w_base=0.50, w_no_cits=0.50 y thr_full≈0.1062; commit/git opcional si el repo está inicializado.
- Ingesta/uso de calibradores en inferencia: calibradores Platt/Isotónica cableados en `PlausibilityScoringService` con selección por config (`post_calibration.method: platt|isotonic`). Se mantiene compatibilidad de temperatura y se expone `base_model_score` vs `model_score` en la respuesta.

Próximos (Agente mid)
- Ensemble: auto-promoción en MLflow a Staging/Production por métrica; ajuste de umbrales con calibración aplicada; reportes comparativos.
- Orquestación reproducible: extender Experiment Scheduler a DAG con dependencias, retries/backoff y checkpointing; estado persistente e idempotencia.
- DVC en pipeline: extender cobertura de enforcement/snapshots a índices FAISS y modelos; asegurar actualización de dvc.lock en cada ejecución.
- Validación de contratos: formalizar JSONSchema del artifact map (`models/manifest.schema.json`) y validación con script; añadir schemas Pydantic adicionales si son necesarios.
- MLflow en servicio: registrar métricas de calibración online (si ground truth disponible) y parámetros de calibración/umbral por run.

---

Notas de operación (pipeline reproducible — activación y artefactos)
- Para ejecutar el pipeline con fetch de años de publicación, establece la variable de entorno y corre el script:
  - macOS/Linux:
    - `FETCH_PUBLICATION_YEARS=1 python pipeline_v4.py`
  - Windows (PowerShell):
    - `$env:FETCH_PUBLICATION_YEARS=1; python pipeline_v4.py`
- Salidas y reportes generados (por defecto):
  - DAG del pipeline (JSON): data/pipeline_dag_v4.json
  - Grafo de proveniencia (W3C PROV-JSON): data/provenance_report.json
  - Reporte del loop científico (reproducibilidad, métricas, hash): reports/scientific_loop_report.json
- Modo sin fetch (rápido):
  - `python pipeline_v4.py` (omitiendo la variable de entorno). Genera igualmente DAG/PROV/reportes con pasos base.
- Notas:
  - Si el versionado de artefactos está habilitado, se generan subdirectorios con hash/fecha para cada artefacto relevante.
  - Cualquier error de lectura/escritura es tolerado y registrado; el pipeline intenta continuar cuando es seguro hacerlo.