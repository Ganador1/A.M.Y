> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="especificación-unificación-del-pipeline-de-integridad"></a>
# Specification: Integrity Pipeline Unification

<a id="objetivo"></a>
## Objective
Consolidate hashing, verification, traceability, and semiblockchain anchoring into a single declarative flow.

<a id="estado-actual"></a>
## Current State
| Component | Function | Limitation |
|------------|---------|-----------|
| blockchain_validation.py | Consensus simulation / logging | Does not orchestrate other hashes |
| integrity_verification.py | Verifies individual artifacts | Isolated from the complete flow |
| metrics.py | Partial exposure | Scattered metrics |

<a id="diseño-propuesto"></a>
## Proposed Design
```
[Evento Artefacto] -> Hasher -> Registro Local -> Batch Merkle Builder -> Anchor Writer -> Verificador Programado -> Alertas
```

<a id="tipos-de-artefacto"></a>
## Artifact Types
| Type | Example Path | Hash Fields |
|------|--------------|-------------|
| DATASET | /data/processed/*.parquet | bytes + schema_signature |
| MODEL | /models/*.bin | bytes + hyperparams.json |
| REPORT | /reports/papers/*.md | content + metadata |
| CONFIG | /configs/*.yml | content |

<a id="esquema-registro-local-jsonl"></a>
## Local Registry Schema (JSONL)
```
{
  "timestamp": "ISO8601",
  "artifact_type": "MODEL",
  "path": "...",
  "sha256": "...",
  "merkle_root": "...",
  "previous_root": "...",
  "integrity_chain_height": 42
}
```

<a id="lógica-merkle-simplificada"></a>
## Simplified Merkle Logic
1. Group new hashes every N artifacts or T minutes
2. Build binary tree (pad last if odd)
3. Save root + link with previous root (block-like)

<a id="api-interna-plan"></a>
## Internal API (Plan)
| Function | Description |
|---------|-------------|
| register_artifact(meta) | Computes and stores base hash |
| build_merkle_batch() | Consolidates pending batch |
| anchor_root(root) | Anchors root (simulated) |
| verify_artifact(path) | Recomputes and compares |
| audit_chain() | Traverses previous root links |

<a id="métricas"></a>
## Metrics
| Metric | Meaning |
|---------|-------------|
| integrity_chain_height | Length of roots chain |
| pending_artifacts | Queued for batch |
| verification_failures | Discrepancy count |
| avg_batch_interval_sec | Actual batch cadence |

<a id="alertas"></a>
## Alerts
| Condition | Action |
|-----------|--------|
| verification_failures > 0 | Critical integrity alert |
| pending_artifacts > threshold | Force batch build |
| avg_batch_interval_sec > SLA | Adjust N or T |

<a id="roadmap"></a>
## Roadmap
| Phase | Deliverable |
|------|---------|
| 1 | Unified registry + consistent hashing |
| 2 | Merkle batches + chain linking |
| 3 | Verification API + complete audit |
| 4 | Export metrics + alerts |
| 5 | Optional: external anchoring (timestamp server) |

<a id="riesgos-y-mitigaciones"></a>
## Risks and Mitigations
| Risk | Mitigation |
|--------|-----------|
| Log growth | Rotation + compression |
| Unlikely collisions | SHA256 + optional BLAKE3 |
| Delayed batches | Timer + quantity threshold |

---
Initial specification completed.
