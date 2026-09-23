> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="roadmap-unificado-fusión-de-planes-y-dividido-para-3-agentes-concurrentes-high-mid-low"></a>
### Unified roadmap (merger of plans) and split for 3 concurrent agents: high, mid, low

Objective: turn AXIOM META 4 into an autonomous multi-domain laboratory, with production-grade security, verifiable reproducibility, intelligent orchestration, and automatic publication, while maintaining SLO/SLI and scientific governance.

Principles
- Security/observability first; reproducibility by default; contracts and lineage as gates.
- Versioned and stable APIs; data and artifact validations; CI/CD with “quality-science-security”.
- Parallel work without collisions: clear ownership per component, small PRs, and previously agreed contracts.

KPIs/SLOs (target)
- Security: 100% endpoints with OAuth2/JWT; 0 critical findings in bandit/pip-audit.
- Reproducibility: ≥90% experiments with complete bundle and verified hash; ≥95% hash-match in replicas.
- Observability: 100% requests with trace_id; p99 < 500 ms (core); MTTR < 30 min.
- Cost: −20% average cost/job with stable SLOs.
- Science: ≥3 multi-domain workflows/month with signed reproducible publication.

Collaboration and anti-conflict rules
- Branches per agent: `feature/high-*`, `feature/mid-*`, `feature/low-*`.
- Ownership by directory:
  - high: `app/middleware/`, `app/observability/` and `app/metrics*`, `app/security*.py`, `main.py`, `app/routers/*` (versioning/security only), `monitoring/`, `kubernetes/`, `nginx/`.
  - mid: `pipeline_v4.py`, `weak_label*_v4.py`, `pipeline_metadata_v4.py`, `mlruns/`, `app/services/*scheduler*`, `app/routers/workflow_orchestration.py`, `app/services/mlflow_registry*`.
  - low: `app/services/sandbox*`, `app/services/integrity*`, `app/routers/integrity*.py`, `publications/`, `docs/`, `.github/workflows/`, `scripts/` (validators/replicator).
- Common interfaces:
  - Pydantic contracts for artifacts (defined by mid, used by all) in `app/models/artifacts/*.py`.
  - API v1 (defined by high): routes and JSONSchema; contract tests by low.
  - Artifact manifest (defined by mid in `models/manifest.schema.json`), verified by low.

Deliverables by phases and parallel assignment

Phase 0 (Weeks 0–2) — Security, API v1, base OTel, metadata, and minimal CI
- high (platform, security, API)
  - Version API in `/api/v1` in `main.py`; temporary alias and deprecation headers.
  - OAuth2/JWT + scopes (RBAC/ABAC) in `app/security.py`; protection of `plausibility`, `scheduler`, `sandbox`, `mlflow-registry`.
  - Middlewares: strict CSP, HSTS, `X-Content-Type-Options`, `Referrer-Policy`; per-route limits; homogeneous Pydantic v2 validation.
  - OpenTelemetry (traces) in FastAPI + httpx; Prometheus export; base dashboard.
  - Criteria: 100% critical endpoints behind auth; 100% requests with trace_id; stable OpenAPI v1.
- mid (data/ML and minimal reproducibility)
  - Extend `pipeline_metadata_v4.py` with Brier, ECE, PR/ROC, hyperparams, and seeds; HMAC of the JSON.
  - Initial Pydantic artifact models: `WeakLabelRecord`, `EnsembleRecord`.
  - Isotonic/Platt calibration and weight grid for ensemble; logging to MLflow.
  - Criteria: signed metadata in `models/`; recorded ECE/Brier improvement; artifacts validated by schema.
- low (CI/CD, validators, docs)
  - Minimal CI in `.github/workflows/`: ruff/flake8, pytest (unit/integration), coverage with gate, bandit, pip-audit, image build.
  - CLI validator script for manifests in `scripts/validate_manifest.py`; apply to 1–2 models in `models/`.
  - README as portal + v1 versioning notice; quick auth and tracing doc.
  - Criteria: CI pipeline red on failures; 2 models with validated manifest.

Phase 1 (Weeks 3–6) — Reproducible orchestration (DAG), DVC, MLflow “source of truth”, contracts/validation
- high (observability and stable API)
  - SLI metrics in `/metrics`: latencies, error rate, cache hit; base Grafana panel per domain.
  - Contract publishing: JSONSchema per v1 endpoint in `docs/API_REFERENCE.md`; Sunset headers for legacy.
  - Criteria: operational dashboards; schemas published and tested.
- mid (DAG/Artifact Registry/DVC/MLflow)
  - Extend `Experiment Scheduler` for DAG with dependencies, retries/backoff, and checkpointing; persistent state.
  - Unified artifact map: path, schema, hash, producer, commit, parameters (save in `models/artifact_map.json`).
  - DVC enforcement on datasets/embeddings/indexes (critical targets) and snapshots per step; MLflow integration (params, runs, stage transitions by metric).
  - Criteria: idempotent resumption; artifact map generated/validated; DVC lock updated; automatic promotion to Staging.
- low (validation, contracts, reinforced CI)
  - Great Expectations (or custom validators) at critical points; emit `.fail.json` with diagnostics.
  - Contract tests (backward compatibility) and OpenAPI fuzzing (Schemathesis).
  - K8s CronJobs for periodic “smoke” pipeline runs.
  - Criteria: explainable aborts before train; green contract tests; active cron.

Phase 2 (Weeks 7–10) — PROV lineage, advanced signatures (Merkle/Ed25519), sandbox hardening, advanced observability
- high (distributed observability and system)
  - Full OTel (traces/metrics/logs) with Loki/Tempo; API→Scheduler→Sandbox→DB correlation.
  - System endpoints: `/api/system/lineage` (summary), `/api/system/slo` (current SLOs).
  - Criteria: visible end-to-end correlation; active system endpoints.
- mid (PROV/lineage and endpoints)
  - Provenance service: PROV-like graph with step nodes/edges; API `GET /api/provenance/graph`, `GET /api/provenance/lineage/{artifact}`; visualization (pyvis/vis) in `monitoring/`.
  - Criteria: navigable lineage from ingestion→publication; integrated tests.
- low (advanced integrity and sandbox)
  - Merkle tree and Ed25519 signatures for packages in `publications/`; runtime and CI verification; anchoring option (OpenTimestamps).
  - Sandbox hardening: gVisor/Firecracker or rootless containers, seccomp/apparmor, RO filesystem, cgroups per job; fuzzing of “code” endpoints.
  - Criteria: mandatory verification before inference; negative escape tests; stable fuzz suite.

Phase 3 (Weeks 11–16) — Autonomous laboratory: Multi-Agent + Orchestrator + KG, policy-aware scheduling, automatic publications
- high (policy-aware scheduling and resources)
  - Multi-objective cost function (plausibility, risk/ethics, GPU cost, impact). Quotas per tenant and deadline scheduling; SLO per job.
  - GPU cost-aware: profiles per job, spot/preemptible preference, autoscaling.
  - Criteria: cost reduction >20% while maintaining SLOs; visible priority queues.
- mid (scientific loop and publication)
  - Integrate Multi-Agent + Orchestrator + Knowledge Graph: hypothesis → plausibility → scheduler → sandbox → analysis → publication → feedback (KG and prompts).
  - Preregistration before execution (hypothesis/criteria/analysis plan) and “Replicability Checker” (clean re-run + comparison of hashes/metrics).
  - Criteria: ≥3 E2E workflows/month with reproducible packages; replicator ≥90% match.
- low (publication-ready outputs, governance, and extended CI/CD)
  - LaTeX templates + reproducible appendices; optional internal DOI. 
  - CI/CD with scientific gates (minimum calibration, drift thresholds) and progressive deployments (canary/blue-green) on critical routers (`plausibility`, `scheduler`, `sandbox`).
  - Criteria: packages ready for arXiv/Zenodo; active gates; zero-downtime deployments.

Continuous (operations and excellence)
- SLO/SLI/Alerting: p99 latency, success, integrity ≥0.95, reproducibility ≥0.9, cost/job. Runbooks.
- Periodic audits (security/ethics/bias), key rotation and secret management, backups/DR.
- Versioned governance/documentation: `docs/INDEX.md` with stable/experimental/deprecated status; complete `docs/EXECUTIVE_SUMMARY_LICENSE_STRATEGY.md` and `docs/OPEN_SOURCE_GOVERNANCE_STRATEGY.md`.

Quick wins (7 days)
- high: `/api/v1` + basic OAuth2/JWT (protect 3 routers), CSP/HSTS, and base OTel traces; initial dashboard.
- mid: `pipeline_metadata_v4.py` with calibration metrics + HMAC; Pydantic for weak/ensemble; isotonic calibration; MLflow logging.
- low: minimal CI (lint+tests+security+build), manifest validator in `scripts/`, 2 models with verified manifest, README portal, and versioning notice.

Acceptance matrix (summary)
- F0: 100% critical endpoints with auth; traces with `trace_id`; CI red on failures; signed metadata and validated artifacts.
- F1: DAG with checkpointing and resumption; artifact map+DVC; MLflow promotion by metric; data validations + contract tests.
- F2: PROV graph + endpoints/visual; Ed25519+Merkle signatures with verification; hardened sandbox and stable fuzz; full OTel.
- F3: ≥3 E2E workflows/month with preregistration, automatic peer-review, and replicability ≥90%; policy-aware scheduling; LaTeX publication.

Risks and mitigation
- API breaks: aliases and deprecations; contract tests.
- DVC/data complexity: start with critical pipelines; efficient remote storage.
- OTel/sandbox overhead: sampling and per-environment modes; configurable isolation profiles.
- GPU cost: per-job profiles and spot preference; per-tenant limits.

Component assignment (quick mapping)
- high:
  - `main.py` (v1 and middlewares), `app/security.py`, `app/middleware/*`, `app/metrics.py`, `app/observability/*`, `monitoring/*`, `kubernetes/*`, `nginx/*`.
- mid:
  - `pipeline_v4.py`, `weak_label*_v4.py`, `pipeline_metadata_v4.py`, `mlruns/`, `app/services/*scheduler*`, `app/routers/workflow_orchestration.py`, `app/services/mlflow_registry*`, `app/models/artifacts/*.py`.
- low:
  - `app/services/sandbox*`, `app/services/integrity*`, `app/routers/integrity*.py`, `publications/*`, `docs/*`, `.github/workflows/*`, `scripts/*` (validator/replicator).

Handoffs and synchronization (avoid getting in the way)
- Definition of contracts (mid) in `app/models/artifacts/*.py` and `models/manifest.schema.json` before high/low depend on them.
- high publishes `OpenAPI v1` and JSONSchema; low builds contract tests and fuzz; mid uses schemas in orchestration.
- Weekly integration points: 
  - Monday: contracts/schemas and API changes.
  - Wednesday: validations/CI and DAG/observability progress.
  - Friday: E2E "smoke" demo and metrics review.

With this plan, the three agents work in parallel with clear ownership, stable interfaces, and measurable acceptance criteria, merging your analysis, the `analisisgpt5normal.md` document, and the `raodmap gpt5midhigh.md` to execute an orderly and effective transformation toward an autonomous scientific laboratory.

---

Progress update (Agent high)
- Implemented versioning middleware `VersionPrefixMiddleware` to accept `/api/v1/*` and mark `/api/*` as a deprecated alias (Deprecation/Sunset/Link headers). Integrated into `main.py` before the rest of the middlewares.
- Hardened base security headers (HSTS, X-Content-Type-Options, X-Frame-Options, X-XSS-Protection). CSP kept compatible with tests (`default-src 'self'`).
- Added JWT support (HS256) and dependency `require_scopes` in `app/security.py` for per-endpoint scopes.
- Protected critical Scheduler endpoints with scopes: `scheduler` and `scheduler:admin` in `app/routers/experiment_scheduler.py`.
- Protected `sandbox_executor` with scope `sandbox` and `mlflow_registry` with `mlflow:read|write|admin`; `scientific_evaluation` with `sci-eval`.
- Added dependency `PyJWT==2.9.0` in `requirements.txt`.
- Base OTel integration (FastAPI + httpx traces) optional via env; script `scripts/generate_openapi.py` to export `docs/openapi_v1.json`.
- Updated `docs/API_REFERENCE.md`: v1 base URL and authentication scheme with scopes.
- Extended observability guide in `docs/OBSERVABILITY_IMPLEMENTATION.md` (OTEL enablement + base Grafana dashboard).
- Script `scripts/generate_schemas_from_openapi.py` to export JSONSchema per endpoint to `docs/schemas/`.

Next (Agent high)
- Publish OpenAPI v1 with JSONSchema per endpoint in `docs/API_REFERENCE.md`.
- Publish OpenAPI v1 with JSONSchema per endpoint in `docs/API_REFERENCE.md`.
- Base OTel instrumentation (FastAPI + httpx traces) and initial dashboard (p50/p95/p99 latency, error rate, cache hit).
 - Create base dashboard in Grafana (latency, errors, cache hit) and quick guide in `docs/OBSERVABILITY_IMPLEMENTATION.md`.
 - Export JSONSchema per endpoint (script ready) and link examples in `docs/API_REFERENCE.md`.

---

Progress update (Agent mid)
- pipeline_metadata_v4.py strengthened with calibration and reproducibility metrics:
  - Calculation of ECE, Brier Score, PR AUC, and ROC AUC for base model, Platt scaling, and isotonic regression.
  - Platt and Isotonic calibrators trained and saved in models/calibrated/ (platt_calibrator.pkl, isotonic_calibrator.pkl).
  - Logging to MLflow of: environment parameters (commit, platform, versions), count/class metrics, CV metrics (if any), calibration metrics, and now, model hyperparameters and reproducible seed.
  - HMAC-SHA256 added to the final JSON for metadata integrity.
  - Generation of models/artifact_map.json with artifact information (path, hash, producer, commit, parameters) and lightweight inline validation of the file.
  - Relocation of validate_artifact_map_file before main() for early availability and to avoid duplicates.
- Initial Pydantic models created for artifacts (WeakLabelRecord, EnsembleRecord) and use of confidence/source tracking in weak labeling.
- Initial integration with MLflow active (plausibility_pipeline_v4 experiment) and run_id logging in metadata when applicable.
- DVC support/services present; integration in pipeline_v4 now with per-step snapshots and enforcement for critical artifacts (ENRICHED, EMBEDDINGS, WEAK, ENSEMBLE_WEAK). If the snapshot fails on a critical target, the pipeline aborts safely after persisting PROV/DAG.
- Provenance service and HTTP endpoints available: GET /api/provenance/experiments and GET /api/provenance/experiment/{experiment_id} with render_html option.
- Weak label ensemble implemented and validated end-to-end:
  - Weight grid for base/no_cits combinations with metric-based selection; full logging to MLflow (weights, per-fold and global metrics) and threshold parameters.
  - Output artifact generated in `data/plausibility_training_v4_weak_labels_ensemble.parquet`; update of `models/artifact_map.json` with the `ENSEMBLE_WEAK` entry and paths in `pipeline_v4.py` aligned.
 - Validation run without manual labels: fallback to 0.5/0.5 average; saved with w_base=0.50, w_no_cits=0.50, and thr_full≈0.1062; commit/git optional if the repo is initialized.
- Ingest/use of calibrators in inference: Platt/Isotonic calibrators wired in `PlausibilityScoringService` with selection by config (`post_calibration.method: platt|isotonic`). Temperature compatibility is maintained and `base_model_score` vs `model_score` is exposed in the response.

Next (Agent mid)
- Ensemble: auto-promotion in MLflow to Staging/Production by metric; threshold tuning with applied calibration; comparative reports.
- Reproducible orchestration: extend Experiment Scheduler to DAG with dependencies, retries/backoff, and checkpointing; persistent state and idempotency.
- DVC in pipeline: extend enforcement/snapshot coverage to FAISS indexes and models; ensure dvc.lock update on each run.
- Contract validation: formalize JSONSchema of the artifact map (`models/manifest.schema.json`) and validation with script; add additional Pydantic schemas if needed.
- MLflow in service: log online calibration metrics (if ground truth available) and calibration/threshold parameters per run.

---

Operation notes (reproducible pipeline — activation and artifacts)
- To run the pipeline with fetch of publication years, set the environment variable and run the script:
  - macOS/Linux:
    - `FETCH_PUBLICATION_YEARS=1 python pipeline_v4.py`
  - Windows (PowerShell):
    - `$env:FETCH_PUBLICATION_YEARS=1; python pipeline_v4.py`
- Outputs and reports generated (by default):
  - Pipeline DAG (JSON): data/pipeline_dag_v4.json
  - Provenance graph (W3C PROV-JSON): data/provenance_report.json
  - Scientific loop report (reproducibility, metrics, hash): reports/scientific_loop_report.json
- No-fetch mode (fast):
  - `python pipeline_v4.py` (omitting the environment variable). It still generates DAG/PROV/reports with base steps.
- Notes:
  - If artifact versioning is enabled, subdirectories with hash/date are generated for each relevant artifact.
  - Any read/write error is tolerated and logged; the pipeline attempts to continue when it is safe to do so.
