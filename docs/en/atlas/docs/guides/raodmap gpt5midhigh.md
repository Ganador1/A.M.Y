> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

Perfect. I have read your analysis in "analisis gp5hig.md" and I have merged it with my previous evaluation to produce a detailed and actionable roadmap, aligned with the project's current architecture and your strategic priorities.

Below I give you:
- A complement to the analysis (what it adds and how it converges with the previous one).
- A phased and prioritized roadmap with concrete tasks, acceptance criteria, dependencies, and risks.
- A mapping of changes to specific repo components.
- Metrics/KPIs and quick wins for the next 7 days.

If you want, at the end I can save this roadmap as a Markdown document inside the repository.

Complement to the analysis (convergences and key additions)
- Strong convergence:
  - Modular and mature architecture with a robust middleware chain, MLflow for tracking, publications with verifiable integrity, and a sandbox for controlled executions.
  - Coverage of scientific domains and advanced services (plausibility, scheduler, orchestrator, multi-agent, GPU).
  - Observability and extensive testing, although with gaps to be filled.
- Contributions/emphasis added by the document:
  - Need for a coherent and versioned API (/api/v1), standardization of contracts, and compatibility tests.
  - Reproducibility of datasets/artifacts: standardize manifest and enforce DVC where applicable.
  - CI/CD with gates (lint, security, tests, migrations) and operational defense (SLO/SLI with alerts).
  - Hardening of the sandbox with container/microVM-level isolation and resource policies.
  - Governance/documentation: complete key docs, TOC, and navigable index per release.
  - "Policy-aware" scheduler and "cost-aware" GPU, plus integration with Multi-Agent and KG to close the scientific loop.

Merged and prioritized roadmap (12–16 weeks + continuous)
Vision: Turn AXIOM META 4 into an autonomous multidomain laboratory that produces reproducible science at scale, with production-grade security, distributed observability, open governance, and methodological rigor.

Principles:
- Security and observability first.
- Contracts and reproducibility as gates (not "nice-to-have").
- Automation: everything critical is tested and deployed with a pipeline.
- Metrics and SLOs that guide decisions.

Phase 0 (Weeks 0–2): Production foundations (high impact/urgency)
Objective: Close critical security gaps, basic distributed observability, API cohesion, and a minimal CI pipeline.

Epics and tasks
- Security (AuthN/Z + hardening)
  - Implement OAuth2/JWT with scopes per router (RBAC/ABAC per endpoint). Criterion: 100% endpoints protected with a documented scheme.
  - Harden security headers (strict CSP, HSTS, X-Content-Type-Options, Referrer-Policy). Criterion: scan with no critical findings.
  - Homogeneous payload validation with Pydantic v2 on all endpoints, maximum sizes per route, rate limits per category.
- Observability (OTel base)
  - OpenTelemetry instrumentation (traces/metrics/logs) in FastAPI and internal http clients; end-to-end trace_id propagation. Criterion: 100% requests with trace_id and visible traces.
  - Export to Prometheus and collector/tempo/loki (according to your stack); base dashboard for p50/p95/p99 latency, error rate, and saturation.
- Coherent API
  - Version API at /api/v1, unify prefixes/tags, and publish validated OpenAPI; generate JSONSchema per contract. Criterion: versioned contracts + consistent docs.
- Minimal CI (GitHub Actions/GitLab CI)
  - Jobs: lint (flake8/ruff), unit+integration, coverage with gate, security (bandit, pip-audit), multi-stage build. Criterion: pipeline red if any fails.

Dependencies:
- None strong, except defining JWT issuers/validators and a secure secret.

Risks:
- Breaking changes in routes; mitigation: introduce /api/v1 in parallel and maintain gradual deprecation.

Phase 1 (Weeks 3–6): Scientific rigor and reproducibility
Objective: Close end-to-end reproducibility and establish strong integrity in artifacts and publications.

Epics and tasks
- Data/artifact reproducibility
  - Standard "Artifact Manifest" per model and experiment (YAML/JSON) with origin, commit, hyperparams, dataset hash, metrics, CV, HMAC/Ed25519 signature, link to MLflow. Criterion: 100% models in <mcfolder name="models/" path="./models"></mcfolder> with validated manifest.
  - DVC required in key training pipelines; enforcement in CI (reject merges without dvc.lock for published experiments). Criterion: 90% relevant experiments with DVC + lock.
- Replicability Checker
  - Re-execution in a clean environment (container) comparing hashes/metrics with tolerances; automatic report. Criterion: ≥90% hash-match reproductions.
- Publication integrity (Merkle + signature)
  - Ed25519 signatures of publication packages in <mcfolder name="publications/" path="./publications"></mcfolder>, Merkle tree with proofs, optional anchoring (OpenTimestamps). Criterion: automated verification in CI and at an integrity endpoint.
- API contracts and tests
  - Generate JSONSchema + contract tests (backward compatibility); Schemathesis or similar for OpenAPI fuzzing. Criterion: compatibility ≥95% on minor version changes.

Dependencies:
- Phase 0 for CI and versioned API.

Risks:
- Operational complexity of DVC with large data; mitigation: select critical pipelines first and efficient remote storage.

Phase 2 (Weeks 7–10): Intelligent orchestration and cost (scheduler/policies/GPU)
Objective: Bring the orchestrator and scheduler to multi-objective policies with cost and risk, and harden the sandbox.

Epics and tasks
- Policy-aware scheduling
  - Incorporate plausibility, risk/ethics, GPU cost, and scientific priority into the scheduler's cost function. Criterion: priority queues, "admission control" with quotas per tenant/project.
  - Deadline scheduling and SLOs per job; timeouts and retries differentiated by criticality.
- GPU cost-aware allocation
  - Profiles per job (mem/vRAM/time) and matching allocation; auto-scaling on demand; preference for spot/preemptible where applicable. Criterion: reduction in average cost per experiment with stable SLOs.
- Hardened sandbox
  - Isolation with gVisor/Firecracker or rootless containers; seccomp/apparmor; read-only mounts; cgroup limits per job. Criterion: negative escape tests; minimum permission audit.

Dependencies:
- Metrics/traces (Phase 0) to observe the effect of policies.

Risks:
- Isolation overhead; mitigation: configurable profiles according to job criticality.

Phase 3 (Weeks 11–16): Autonomous multidomain laboratory (closed loop)
Objective: Integrate Multi-Agent and KG with orchestration to close the complete scientific cycle and publish automatically.

Epics and tasks
- Multi-Agent + KG integration
  - Hypothesis → plausibility evaluation → scheduler → sandbox → validation → publication → knowledge feedback (KG) and prompts. Criterion: 3 multidomain workflows/month end-to-end.
- Automated peer review
  - Independent reviewer agent with statistical/UQ criteria and reproducibility checklist; gate before promoting to "scientific production". Criterion: 100% publications with automated peer review.
- "Publication-ready outputs"
  - LaTeX templates + reproducible appendices (data, code, hashes, proofs). Criterion: package ready for arXiv/Zenodo with optional DOI.

Continuous (operations and excellence)
- SLO/SLI/Alerting: p99 latency, success rate, integrity (≥0.95), reproducibility (≥0.9), cost per experiment. Alerts and runbooks.
- Periodic audits (security, ethics, bias), key rotation and secret management, backups/DR.
- Open governance and versioned documentation with TOC and index per release.

Map of changes to repo components
- API, security, middlewares
  - <mcfile name="main.py" path="./main.py"></mcfile>: mounting of /api/v1, registration of security/OTel middlewares and routers.
  - <mcfolder name="app/middleware/" path="./app/middleware/"></mcfolder> and <mcfile name="middleware.py" path="./app/middleware.py"></mcfile>: CSP, HSTS, TraceIdMiddleware, size limits, rate limits per route.
  - <mcfile name="security.py" path="./app/security.py"></mcfile>: OAuth2/JWT, scopes, RBAC/ABAC.
  - <mcfolder name="app/routers/" path="./app/routers/"></mcfolder> (e.g. <mcfile name="pde.py" path="./app/routers/pde.py"></mcfile>): route versioning and Pydantic v2 validation.
- Observability
  - <mcfile name="metrics.py" path="./app/metrics.py"></mcfile>, <mcfile name="monitoring.py" path="./app/monitoring.py"></mcfile>, <mcfolder name="monitoring/" path="./monitoring/"></mcfolder>: OTel instrumentation, export, dashboards.
- Data/ML and reproducibility
  - <mcfile name="pipeline_v4.py" path="./pipeline_v4.py"></mcfile> and <mcfile name="weak_label_v4.py" path="./weak_label_v4.py"></mcfile>: DVC integration, enriched logging, manifest, and coherent MLflow registry.
  - <mcfolder name="mlruns/" path="./mlruns/"></mcfolder> + <mcfolder name="models/" path="./models"></mcfolder>: generation/validation of manifests.
  - <mcfolder name="publications/" path="./publications"></mcfolder>: Merkle tree, Ed25519 signature, proofs, and verification.
- Orchestration and sandbox
  - <mcfolder name="app/services/" path="./app/services/"></mcfolder> (scheduler/orchestrator): multi-objective cost policies, deadlines, queues/priorities, quotas.
  - <mcfolder name="app/services/sandbox/" path="./app/services/sandbox/"></mcfolder> or equivalent module: isolation with gVisor/Firecracker, cgroup limits.
- Documentation and CI/CD
- <mcfolder name="docs/" path="./docs/"></mcfolder>: INDEX.md/TOC, complete “licenses” and “governance”.
  - <mcfolder name=".github/workflows/" path="./.github/workflows/"></mcfolder>: CI pipelines with gates and artifacts.
  - <mcfile name="README.md" path="./README.md"></mcfile>: split into thematic guides; keep a thin and navigable README.

Acceptance criteria per phase (summary)
- Phase 0:
  - 100% endpoints under /api/v1 with auth and homogeneous validation; CSP/HSTS active.
  - OTel traces visible with trace_id propagation; base dashboard operational.
  - CI red if lint, tests, security, or build fail.
- Phase 1:
  - 100% models with validated manifest; ≥90% relevant pipelines with DVC.
  - Replicability Checker with ≥90% hash‑match; publications with signature and Merkle verified in CI.
  - Contract tests active; backward compatibility ≥95%.
- Phase 2:
  - Scheduler with multi‑objective policies and per-tenant quotas; SLO per job.
  - Cost‑aware GPU allocation with cost reduction and stable SLOs.
  - Hardened sandbox with negative escape tests.
- Phase 3:
  - ≥3 multidomain workflows/month completed E2E with automated peer‑review.
  - “Publication‑ready outputs” automatically generated for priority packages.

KPIs and SLO/SLI
- Security: 0 critical findings in bandit/pip‑audit; 100% endpoints with auth.
- Reproducibility: ≥90% of experiments with complete bundle and verified hash.
- Observability: 100% requests with trace_id; p99 < agreed SLO; MTTR < 30 min.
- Cost: reduction ≥20% in average cost per experiment with SLO stability.
- Science: ≥3 multidomain workflows/month with validated publication.

Quick wins (next 7 days)
- API/Security
  - Introduce /api/v1 in <mcfile name="main.py" path="./main.py"></mcfile> and keep a temporary alias for old routes (deprecation).
  - Add strict CSP and HSTS in <mcfile name="middleware.py" path="./app/middleware.py"></mcfile>.
  - Add basic OAuth2/JWT in <mcfile name="security.py" path="./app/security.py"></mcfile> and protect 2–3 critical routers (e.g., plausibility, scheduler).
- Observability
  - Integrate OTel FastAPI + httpx and export to Prometheus; propagate trace_id to logs in <mcfile name="metrics.py" path="./app/metrics.py"></mcfile>.
  - Initial dashboard: p50/p95/p99 latencies, error rate, cache hit ratio.
- CI
  - Base workflow in <mcfolder name=".github/workflows/" path="./.github/workflows/"></mcfolder>: Python setup, deps cache, ruff/flake8, pytest with coverage and gates, bandit, pip‑audit, image build.
- Reproducibility
  - Define the “Artifact Manifest” schema and create a CLI validator in <mcfolder name="scripts/" path="./scripts/"></mcfolder>; apply to 1–2 models in <mcfolder name="models/" path="./models"></mcfolder> for pilot testing.

Risks and mitigations
- Breaking changes in API: maintain a compatibility period with aliases, communicate deprecations in <mcfile name="README.md" path="./README.md"></mcfile> and in /docs.
- Friction with DVC/storage: start with critical pipelines and define efficient remote storage.
- OTel and hardened sandbox overhead: enable by profile/environment, adjust sampling and limits.

<a id="progreso-agente-low-seguimiento-iterativo"></a>
## Low Agent Progress (Iterative Tracking)

Initial status (Week 0) – All deliverables in planning.

Phase 0 deliverables under Low Agent ownership:

- Minimal CI: workflow with lint (ruff), tests (pytest + coverage), security (bandit, pip-audit), and base build.
- Structured base documentation: `docs/INDEX.md` (TOC + statuses), complete license and governance drafts.
- Model/dataset manifest validator (`scripts/validate_manifests.py`).
- Contribution guide specific to the low role (`docs/LOW_AGENT_CONTRIBUTING.md`).
- Integration of manifest validation in CI (soft gate at start: warning → then mandatory error).

Progress metric (will be updated each iteration):

| Deliverable | Status | ETA | Notes |
|------------|--------|-----|-------|
| Minimal CI | done | ✅ | Initial workflow operational (ruff, tests, security, build) |
| INDEX.md + TOC | done | ✅ | Index created with statuses and base TOC |
| License & Governance (skeletons) | done | ✅ | Draft documents added |
| Manifest validator | done | ✅ | Script with JSON output and hashes |
| LOW_AGENT_CONTRIBUTING.md | done | ✅ | Guide with checklist and standards |
| Manifest validation in CI | done | ✅ | Step added (non-blocking) |
| manifest.schema.json | done | ✅ | Draft schema (initial version) |
| Example manifest (plausibility_v4_rf) | done | ✅ | Validated against schema |
| Additional manifests (logreg, rf_regularized) | done | ✅ | Total 3 valid manifests |
| Ed25519 signature script (`sign_manifest.py`) | done | ✅ | Key generation + deterministic signature |
| Signature verification script (`verify_manifest_signatures.py`) | done | ✅ | JSON report with status per manifest |
| Signature verification job in CI | done | ✅ | Non-blocking, publishes artifact |
| cryptography dependency added | done | ✅ | Aligned with requirements.audit.txt |
| Enable strict manifests gate | pending | TBD | Condition: 2 consecutive runs without errors (met), next commit will enable fail-on-error |
| Enable signatures gate (blocking) | pending | TBD | Condition: ≥1 valid signature per manifest and versioned public keys |

Immediate next steps (Low Agent - update):

1. Enable blocking mode of the manifest validator (change CI step: remove `|| true` and/or add `--fail-on-error`).
2. Add public key storage in `keys/public/` + `keys/README.md` (public only; private outside the repo).
3. Run signing on the 3 current manifests and commit signatures (add `signatures` section).
4. Enable signatures gate (warning → blocking) after verifying consistency in 2 consecutive pipelines.
5. Extend schema to validate `signatures[*]` structure (alg, sig, public_key_fingerprint, optional ts).
6. Document key rotation and local verification flow in `docs/REPRODUCIBILITY_INTEGRITY.md` (new).
7. Prepare preliminary Merkle tree design for publication batch (technical draft).

Gate activation conditions:

- Manifests gate (structure + hashes): IMMINENT (criterion met).
- Signatures gate: after 3 signed manifests + 2 consecutive CI runs without verification failures.


Next update: after enabling blocking manifests gate and signing the 3 current manifests.
