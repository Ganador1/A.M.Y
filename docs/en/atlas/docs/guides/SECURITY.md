> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="seguridad-e-integridad---axiom-meta-4-mvp-consolidación"></a>
# Security and Integrity - AXIOM META 4 (MVP Consolidation)

<a id="objetivos"></a>
## Objectives
Unify scattered controls (blockchain, integrity verification, ethical gating) into a clear and extensible layer.

<a id="componentes-actuales"></a>
## Current Components
- `app/blockchain_validation.py`: Distributed validation (simulated) + signatures.
- `app/integrity_verification.py`: Local/comprehensive checks + logs.
- `app/integrity_core.py`: New unified artifact core + optional blockchain anchoring.
- `app/ethics_gate.py`: Base ethical heuristic + risk scoring.
- `app/risk_assessment.py`: Combined ethical layer + domain rules (bio/chem/clinical/materials).
- `app/service_registry.py`: Service discovery for future per-service policies.

<a id="riesgos-identificados-primer-barrido"></a>
## Identified Risks (First Pass)
| Risk | Description | MVP Mitigation | Future |
|--------|-------------|----------------|--------|
| Duplicate hashing | Hash calculation in multiple modules | Centralize in `integrity_core` | Stable hashing API + versioning | 
| Fixed thresholds | Hardcoded ethics thresholds | Optional YAML policy | Versioned policy system | 
| Lack of unified provenance | Artifacts without lineage | Field prepared in core (pending) | Graph + internal DOI | 
| Simulated blockchain validation | Local signatures not distributed | Marked as experimental | p2p network / real per-node signatures | 
| Absence of circuit breakers | Intensive services without isolation | Base registry | Scheduler + resource limits | 
| Lack of robust authentication | Open endpoints (review) | Base security auditor | OAuth2 / API Keys rotation | 

<a id="flujos-clave"></a>
## Key Flows
1. Artifact registration -> hashes (data + metadata) -> (optional) asynchronous blockchain anchoring.
2. Artifact verification -> hash comparison + blockchain validation + basic integrity check.
3. Experiment risk assessment -> EthicsGate -> domain rules -> unified result.

<a id="uso-rápido-código"></a>
## Quick Usage (Code)
```python
from app.integrity_core import integrity_core
rec = integrity_core.register_artifact({"result": [1,2,3]}, artifact_type="result", metadata={"model_type":"pinn"}, blockchain=True)
status = asyncio.run(integrity_core.verify_artifact(rec.artifact_id))
```

<a id="política-de-reporte-de-vulnerabilidades"></a>
## Vulnerability Reporting Policy
- Send reproducible report (PoC, impact, version) to: security@axiom.local (placeholder)
- Target first response time: 72h
- Responsible disclosure: window of 90 days recommended

<a id="roadmap-de-hardening"></a>
## Hardening Roadmap
1. Real per-node signatures + key rotation.
2. Lineage / provenance (parent-child) + internal DOI (`axiom:year:hash`).
3. Circuit breakers + adaptive timeouts per critical service.
4. Priority-aware scheduler + GPU/CPU quotas.
5. Dynamic ethical policies (signed YAML) + Merkle audit.
6. Secrets module (KMS) and leak scanning.
7. Full integration into publication package (`/publications/{uuid}/`).

<a id="métricas-iniciales-propuestas"></a>
## Proposed Initial Metrics
| Metric | Source | Target |
|---------|--------|----------|
| % artifacts with blockchain proof | integrity_core | >30% initial phase |
| Basic verification time | integrity_core | <150ms |
| Blocked risks (HIGH/CRITICAL) | risk_assessment | 100% without valid signature |
| Service coverage in registry | service_registry | >80% *_service.py files |

<a id="limitaciones-conocidas"></a>
## Known Limitations
- Blockchain not resistant to attacks (simulation mode).
- Not persisted to external storage (in-memory at runtime).
- No end-user authentication implemented in this MVP.

<a id="contribuir"></a>
## Contributing
1. Add new verification -> extend `IntegrityCore`.
2. Add new risk rules -> modify `risk_assessment.py`.
3. Document security changes in this file.

---
`Última actualización`: auto-generated initial consolidation phase.
