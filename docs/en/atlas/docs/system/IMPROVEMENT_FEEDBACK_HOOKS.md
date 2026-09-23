> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="integración-de-hooks-de-feedback-en-researchcyclemanager"></a>
# Integrating Feedback Hooks in ResearchCycleManager

Date: 2025-09-14
Status: Implemented

<a id="objetivo"></a>
## Objective
Record normalized metrics (accuracy, coherence, scientific_validity) in the iterative improvement pipeline upon completion of key phases of the research cycle to enable longitudinal analytics and optimization recommendations.

<a id="fases-instrumentadas"></a>
## Instrumented Phases
| Phase | Method | Main Metric | Proxy Used |
|------|--------|------------------|-----------------|
| hypothesis_generation | `_phase_hypothesis_generation` | accuracy, coherence | `confidence_score` of hypotheses (coherence = 0.9 * confidence) |
| literature_review | `_phase_literature_review` | accuracy, coherence | normalized coverage: `papers_found / 20` (cap 1.0) |
| analysis | `_phase_analysis` | accuracy, coherence | `analysis_result.confidence_score` (coherence = 0.95 * confidence) |
| validation | `_phase_validation` | accuracy, coherence, scientific_validity | `quality_score` (coherence = 0.97 * quality) |

<a id="implementación"></a>
## Implementation
A private helper `_record_phase_feedback` was added that:
- Maps phase → `AnalysisType` of the iterative pipeline.
- Normalizes values to range [0,1].
- Adds context (`cycle_id` as `trace_id`, domain, and research_question).
- Uses defensive `getattr` to tolerate absence of the improvement module.

```python
await self._record_phase_feedback(cycle, phase="analysis", accuracy=conf, coherence=conf*0.95)
```

<a id="robustez"></a>
## Robustness
- Optional loading of the pipeline (`try/except`).
- If not available, the hooks are silent no-ops.
- Exception handling within the helper so as not to affect the main flow.

<a id="impacto-esperado"></a>
## Expected Impact
- Early activation of aggregate metric calculation after >=5 samples per type.
- Future optimizations based on parameter correlation (already supported by the pipeline).
- Basis for endpoint `/api/improvement/metrics/all` (future sprint task).

<a id="próximos-pasos-relacionados"></a>
## Related Next Steps
1. Integrate plausibility scoring to enrich accuracy/coherence (sprint task 2/3).
2. Add formal Trace IDs and endpoint `/metrics` for operational visibility.
3. Expose consolidated public metrics endpoint.

---
Document automatically generated as part of Sprint 1.
