> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="plan-cross-validation-matrix"></a>
# Plan: Cross-Validation Matrix

<a id="objetivo"></a>
## Objective
Create a dynamic NxN matrix that quantifies compatibility and cross-validation between scientific domains (rows and columns = main domains/services).

<a id="motivación"></a>
## Motivation
- Raise scientific rigor by combining results from different methods
- Detect inter-domain contradictions
- Prioritize experiments with greater marginal value

<a id="estructura-de-datos-propuesta"></a>
## Data Structure (Proposal)
```json
{
  "domains": ["plasma", "materials", "clinical", "genomics", ...],
  "matrix": {
    "plasma|materials": {"compatibility": 0.82, "evidence": 5, "last_updated": "2025-09-09T12:00:00Z", "rationale": "Thermal gradients ↔ phase stability"},
    "clinical|genomics": {"compatibility": 0.74, "evidence": 3, "rationale": "Mutation-load ↔ phenotype metrics"}
  },
  "version": "cv_matrix.v1"
}
```

<a id="cálculo-compatibilidad"></a>
## Compatibility Calculation
| Factor | Weight | Source |
|--------|------|--------|
| Entity matching (shared variables) | 0.25 | Ontology (future) |
| Numerical coherence (expected correlations) | 0.25 | Statistical analysis |
| Prior evidence (n consistent experiments) | 0.20 | validation_history |
| Cross robustness (result stability) | 0.15 | robustness_metrics |
| Convergent uncertainty (UQ overlap) | 0.15 | UQ service |

Final score = Σ (normalized_factor * weight).

<a id="pipeline-de-actualización"></a>
## Update Pipeline
1. Register multi-domain workflow execution
2. Extract common variables + metrics
3. Calculate correlations / divergences
4. Integrate robustness and UQ
5. Update matrix cell + timestamp
6. Emit event `cross_validation.updated`

<a id="endpoints-planeados"></a>
## Planned Endpoints
| Method | Route | Description |
|--------|------|-------------|
| GET | /cv/matrix | Retrieves full matrix |
| GET | /cv/matrix/cell?src=A&dst=B | Detail for domain pair |
| POST | /cv/matrix/recompute | Forces global recomputation |
| GET | /cv/matrix/stats | Aggregated metrics |

<a id="métricas-clave"></a>
## Key Metrics
| Metric | Target |
|---------|----------|
| domain_coverage | ≥ 80% active pairs |
| contradictions_detected | < 5% pairs | 
| update_time | < 2s cell |
| query_latency | < 150ms |

<a id="integraciones"></a>
## Integrations
- Hypothesis Core: compatibility snapshot
- Publication Pipeline: cross-validation section
- Knowledge Graph: shared entities
- Integrity: matrix version hash

<a id="roadmap-incremental"></a>
## Incremental Roadmap
| Phase | Description | Delivery |
|------|-------------|---------|
| F1 | Schema + dummy read endpoints | Week 1 |
| F2 | Basic correlation calculation | Week 2 |
| F3 | UQ + robustness integration | Week 3 |
| F4 | Events + integrity hashing | Week 4 |

<a id="riesgos"></a>
## Risks
| Risk | Mitigation |
|--------|-----------|
| Initial sparsity | Bootstrapping with critical pairs|
| Computational cost | Incremental cache |
| Data inconsistencies | Typed validators |

---
First blueprint. Next: define persistence model and endpoint prototype.
