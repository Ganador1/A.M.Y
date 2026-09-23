> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="plausibility-scoring---implementación-base"></a>
# Plausibility Scoring - Base Implementation
Date: 2025-09-14
Status: ✅ Implemented (heuristic version + persistence + integrated into feedback pipeline)

<a id="resumen"></a>
## Summary
Service `plausibility_scoring_service.py` that calculates a composite plausibility score for scientific hypotheses by combining:
- Structural coverage (title, description, variables, assumptions)
- Quantitative elements present in description/expected results
- Duplication penalty (hash-based embedded vector store)
- Adjustment for empirical evidence (count + average support with log factor and weighting)
- Domain and component weights (optional YAML config)
- Persistence in table `hypothesis_plausibility_metrics` if `hypothesis_uuid` is provided

<a id="componentes-principales"></a>
## Main Components
| Component | Description | Range |
|------------|-------------|-------|
| title_length | Validates reasonable length | 0 / 1 |
| description_length | Description > 40 chars | 0 / 1 |
| variables_coverage | Non-empty variables and <=12 | -1 / 0 / 1 |
| quant_elements | Presence of numbers/% | 0 / 1 |
| assumptions_present | >=1 assumption | 0 / 1 |
| duplication_penalty | High similarity in vector store | 0 / -1 / -2 |

Raw score is clipped to [-2,5] and linearly normalized to [0,1]. Subsequent multiplicative adjustments: evidence and domain weight.

<a id="evidencia"></a>
## Evidence
- Unit tests: `tests/unit/test_plausibility_scoring_service.py`
- Persistence confirmed (insertion into DB and retrieval of components)
- Evidence adjustment increases score (factor >1 when support exists)

<a id="extensibilidad-futura"></a>
## Future Extensibility
1. ML calibration (Logistic Regression already conditionally supported)
2. Add factors: novelty (global embedding), complexity_penalty (length + number of variables), risk_factor.
3. Integrate with feedback pipeline to emit derived ACCURACY_SCORE/COHERENCE_SCORE.

<a id="integración-con-feedback-pipeline"></a>
## Integration with Feedback Pipeline
Scoring is now invoked at three moments of the research cycle:
1. Hypothesis generation (plausibility_initial)
2. Post-experimental analysis (plausibility_analysis) fusing composite with analysis confidence
3. Final validation (plausibility_validation) reinforcing final metrics

Each invocation injects derived signals (accuracy/coherence proxies) into the Iterative Improvement Pipeline. The composite acts as reinforcement of ACCURACY_SCORE and a smoothed average is used as COHERENCE_SCORE.

<a id="hooks-pendientes"></a>
## Pending Hooks
- Register distribution metrics in endpoint `/metrics` once created.

<a id="riesgos"></a>
## Risks
- Embedding simplification (hash) limits real semantic detection.
- Penalties can dominate with unbalanced datasets.

<a id="próximos-pasos"></a>
## Next Steps
- Implement real embedding layer (sentence-transformers) when dependency is incorporated.
- Add cross-validation of ML calibration.

---
Document generated automatically.
