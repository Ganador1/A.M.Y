> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="unified-policy-engine-design"></a>
# Unified Policy Engine Design

<a id="objetivo"></a>
## Objective
Centralized and configurable system for making decisions about scientific hypotheses and research cycles. It provides explainable outputs (status + reasons + contributions) and decouples business logic from weights/thresholds through a versioned YAML file.

<a id="estados-de-decisión"></a>
## Decision States
- **halt**: stop immediately (high risk or very low composite value)
- **approve**: continue / promote to the next step
- **refine**: requires moderate adjustments before promoting
- **reject**: does not proceed (insufficient or contradictory)

Precedence order: `halt > approve > refine > reject`.

<a id="métricas-soportadas-ejemplos-actuales"></a>
## Supported Metrics (current examples)
| Metric | Direction | Weight (example) | Notes |
|---------|---------|----------------|-------|
| novelty | + | 0.15 | Perceived innovation |
| evidence_strength | + | 0.20 | Quality and quantity of evidence |
| reproducibility_risk | - | -0.20 | Risk (lower is better) |
| coverage | + | 0.10 | Coverage of variables/keys |
| diversity | + | 0.05 | Variety of sources/angles |
| consistency | + | 0.10 | Internal coherence |
| peer_review | + | 0.15 | Community validation |
| methodological_rigor | + | 0.10 | Methodological quality |
| safety | + | 0.05 | Ethical risks / safety |

Weights can be adjusted in `config/policy_engine_config.yaml`.

<a id="configuración-yaml"></a>
## YAML Configuration
```yaml
version: 1
weights: {...}
thresholds:
  approve:
    composite_min: 0.62
    max_reproducibility_risk: 0.50
  refine:
    composite_min: 0.45
    composite_max: 0.65
  halt:
    composite_max: 0.30
    min_reproducibility_risk: 0.80
normalization:
  missing_score_policy: treat_as_neutral
caps:
  max_positive: 1.0
  min_negative: -1.0
logging:
  decisions_path: data/policy_decisions.jsonl
  include_deltas: true
```

<a id="semántica-de-umbrales"></a>
### Threshold Semantics
- `halt.composite_max`: if the normalized score falls below ⇒ halt.
- `halt.min_reproducibility_risk`: if the risk exceeds this threshold ⇒ halt.
- `approve.composite_min`: minimum to approve (if halt was not triggered and the optional maximum risk is met).
- `refine`: intermediate band. If it does not enter approve and `composite` within the range ⇒ refine.
- Else ⇒ reject.

<a id="cálculo-del-composite"></a>
## Composite Calculation
1. Iterate over the metrics defined in `weights`.
2. For each metric present: `contrib = peso * valor_capeado`.
3. Sum contributions and normalize by the sum of absolute weights:  
   \( composite = \frac{\sum (w_i * v_i)}{\sum |w_i|} \).
4. Missing metrics: ignored (neutral) unless a different future policy applies.
5. Caps guarantee values in [-1,1] before multiplying.

<a id="proceso-de-decisión"></a>
## Decision Process
1. Evaluate the rules of `halt` first (low energy and safety-first).
2. Evaluate approval with risk constraints.
3. Evaluate the refinement range.
4. Fallback to rejection.

<a id="output-estructurado"></a>
## Structured Output
```json
{
  "status": "approve",
  "composite": 0.625,
  "reasons": ["composite_ok:0.625>=0.62", "repro_risk_ok:0.200<=0.5"],
  "raw_scores": {"novelty":0.8,...},
  "contributions": {"novelty":0.12,"evidence_strength":0.18,...},
  "ordered_factors": ["evidence_strength","peer_review",...],
  "timestamp": "2025-09-14T...",
  "config_version": 1
}
```
`ordered_factors` sorts by |contribution| to explain dominance.

<a id="logging"></a>
## Logging
JSONL format in `data/policy_decisions.jsonl` (append-only). It allows:
- Historical auditing
- Statistical analysis / offline tuning
- Drift detection in metric distribution

<a id="integración-en-el-agente"></a>
## Integration into the Agent
The wrapper `policy_decide` inside `ScientificHypothesisAgent` exposes action `policy_decide`:
```python
agent.policy_decide({
  "scores": {"novelty":0.8, ...},
  "hypothesis_id": "..."  # opcional
})
```
This enriches the log with `hypothesis_id` to correlate decisions with trajectories.

<a id="ejemplo-rápido"></a>
## Quick Example
```
python - <<'PY'
from app.services.policy_engine_service import policy_engine_service
print(policy_engine_service.decide({
  'novelty':0.7,'evidence_strength':0.8,'reproducibility_risk':0.3,
  'coverage':0.6,'diversity':0.5,'consistency':0.7,'peer_review':0.75,
  'methodological_rigor':0.7,'safety':0.9
}))
PY
```

<a id="estrategia-de-tuning"></a>
## Tuning Strategy
1. Collect N real decisions.
2. Calculate the distribution of `composite` and rates (approve/refine/halt/reject).
3. Adjust `approve.composite_min` targeting, for example, 15-25% refine, <10% halt.
4. Adjust weights by increasing the magnitude of underrepresented metrics (e.g., safety) without exceeding saturation.
5. Add unit tests for new edge cases.

<a id="extensiones-planeadas"></a>
## Planned Extensions
| Feature | Description | Priority |
|---------|-------------|-----------|
| Temporal decay | Penalize aged hypotheses without new evidence | Medium |
| Causal justification | Generate a summarized chain-of-thought textual explanation | High |
| Dynamic weight adaptation | Retrain weights with human feedback | Medium |
| Semantic similarity guard | Detect duplicates / near-duplicates and adjust novelty | Medium |
| Risk decomposition | Split reproducibility_risk into subcomponents | Low |
| Config hot-reload API | Endpoint to refresh config without restarting | Medium |

<a id="testing"></a>
## Testing
File: `tests/unit/test_unified_policy_engine.py` covers:
- approve pathway
- refine band
- halt due to high risk
- halt/reject due to low composite
- JSONL logging

<a id="buenas-prácticas"></a>
## Best Practices
- Keep weights normalized (sum of absolutes ≈ 1) for interpretive stability.
- Accompany threshold changes with test adjustments.
- Analyze outliers regularly (dominant |contrib| > 0.5) ⇒ reconsider the weight.

<a id="roadmap-siguiente-iteración"></a>
## Roadmap Next Iteration
1. Add derived metrics (e.g., `evidence_velocity`).
2. Persist the version of the prompt template used in the hypothesis for correlation.
3. Lightweight dashboard (notebook) for composite histogram and decision rates.

---
**Current Status:** Operational and tested baseline implementation (5 tests). Ready for integration into advanced workflows and iterative tuning.
