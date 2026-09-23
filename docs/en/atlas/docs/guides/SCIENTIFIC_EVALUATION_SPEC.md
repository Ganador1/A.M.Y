> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="scientific-evaluation-service-specification-v0"></a>
# Scientific Evaluation Service Specification (v0)

<a id="objetivo"></a>
## Objective
Unify the quantitative evaluation of scientific hypotheses / results through a set of normalized sub-metrics and a traceable composite score.

<a id="componentes-actuales"></a>
## Current Components
- novelty (0-1)
- evidence_strength (0-1)
- methodological_rigor (0-1) – internal heuristic
- reproducibility_likelihood (0-1) – internal heuristic

<a id="fórmula-compuesta-v0"></a>
## Composite Formula (v0)
```
composite = 0.30 * novelty \
          + 0.30 * evidence_strength \
          + 0.25 * methodological_rigor \
          + 0.15 * reproducibility_likelihood
```
Weights designed to prioritize (a) new contribution and (b) empirical soundness, keeping rigor and reproducibility influential but slightly lower.

<a id="normalización"></a>
## Normalization
Each sub-metric is ensured to be in the range [0,1]. Out-of-range values are "clamped" (min(max(x,0),1)).

<a id="heurísticas-internas-v0"></a>
## Internal Heuristics (v0)
- methodological_rigor: penalizes high complexity without justification and low coverage of controls.
- reproducibility_likelihood: favors a lower number of critical steps, dependence on standard tools, and clarity of variables.

<a id="integración-con-hipótesis"></a>
## Integration with Hypotheses
If `hypothesis_id` is passed without `novelty` or `evidence_strength`, it attempts to:
- novelty ≈ min(1.0, 0.2 + 0.05 * n_variables)
- evidence_strength ≈ confidence_score (if it exists in the hypothesis record)
This allows a quick preliminary evaluation before more costly calculations.

<a id="campos-de-salida"></a>
## Output Fields
```json
{
  "inputs": { ... originales ... },
  "normalized": {"novelty":0.x, ...},
  "components": {
     "methodological_rigor": {... breakdown ...},
     "reproducibility_likelihood": {... breakdown ...}
  },
  "composite_score": 0.x,
  "weights": {"novelty":0.30, ...},
  "version": "v0"
}
```

<a id="errores-y-validaciones"></a>
## Errors and Validations
- Missing key metrics -> inferred if `hypothesis_id` is present, otherwise `ValueError` descriptive in future versions.
- Invalid range -> corrected via clamp and the corrected value is exposed in `normalized`.

<a id="extensiones-planeadas-roadmap"></a>
## Planned Extensions (Roadmap)
1. Persistence of snapshots (evaluation_records table) with formula version.
2. Robustness metric (variation under synthetic perturbations).
3. Statistical Power metric (if raw data are available).
4. Dynamic adjustment of weights via Bayesian learning.
5. Export to Decision Ledger (auto-log of evaluations > threshold).
6. API to compare two evaluations and generate a differential explanation.

<a id="versionado"></a>
## Versioning
Changes in weights or the incorporation of new metrics will increase the version (v1, v2...). `formula_hash` (sha256 of the weights+components structure) will be saved for reproducibility.

<a id="ejemplo-de-uso-pseudo"></a>
## Usage Example (pseudo)
```python
svc = ScientificEvaluationService()
res = svc.evaluate({"novelty":0.7, "evidence_strength":0.6})
print(res["composite_score"])  # ~0.65
```

<a id="notas"></a>
## Notes
This document accompanies the initial implementation and must be updated with every change in weights or new metrics.
