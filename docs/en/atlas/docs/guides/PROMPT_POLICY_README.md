> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="prompt-registry--policy-engine-mvp"></a>
## Prompt Registry & Policy Engine (MVP)

This document describes the new capabilities introduced:

<a id="promptregistryservice"></a>
### PromptRegistryService
Location: `app/services/prompting/prompt_registry_service.py`

Key functions:
- `register(name, version, template, variables, metadata)` registers a versioned template (Jinja2 StrictUndefined).
- `list()` and `get(name, version)` inspect the repository.
- `render(name, version, context)` validates required variables and produces the final prompt.
- Audit: each render is appended in `data/prompt_renders.jsonl` with hash and context keys.

Immediate intended use:
- Unify prompts for: hypothesis generation, literature review, peer review, and refinement.
- Basis for a future A/B testing and semantic ranking layer.

<a id="policyengineservice"></a>
### PolicyEngineService
Location: `app/services/policy_engine_service.py`

Objective: centralize the advancement decision in the scientific cycle.

Inputs (expected scores if available):
`novelty, evidence_strength, methodological_rigor, reproducibility_likelihood, support_score, coverage, diversity`.

Configuration:
- Optional file `policy_config.yaml` with:
  - `weights`: weights per metric.
  - `thresholds.approve` and `thresholds.refine`.
  - `required`: list of mandatory metrics.

Output (`decide`):
```json
{
  "success": true,
  "decision": {
    "status": "approve|refine|reject",
    "score": 0.7123,
    "reasons": ["Score 0.712 >= approve 0.7"],
    "raw_scores": { ... },
    "timestamp": "..."
  }
}
```

Audit: each decision is appended in `data/policy_decisions.jsonl`.

<a id="próximos-pasos-planeado"></a>
### Next Steps (Planned)
1. Integrate PromptRegistry into current agents (replace inline prompts).
2. Connect PolicyEngine to the `research_cycle_manager` loop for automatic gating.
3. Add temporal normalization (decay) for `support_score` and `confidence_score` in decisions.
4. Introduce semantic ranking of tools and models for adaptive selection.

<a id="tests"></a>
### Tests
Locations:
- `tests/unit/test_prompt_registry_service.py`
- `tests/unit/test_policy_engine_service.py`

All current tests pass (see CI / local run). Additional coverage will be added when integrated into the main flow.
