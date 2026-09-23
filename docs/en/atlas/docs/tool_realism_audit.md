> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="tool-realism-audit"></a>
# Tool Realism Audit

Atlas now distinguishes between routes that produce real scientific evidence and routes that only provide context, heuristics, or fallbacks.

<a id="categorías"></a>
## Categories

- `real_remote`: evidence obtained from real scientific APIs, databases, or services.
- `real_local`: real scientific computation executed locally, for example Qiskit, SciPy, or statistical validation.
- `heuristic`: LLM-assisted reasoning or synthesis that does not constitute direct measurement.
- `fallback`: controlled degradation when a real integration is not available.
- `mock`: demos or simplified simulations that should not be counted as evidence.
- `auxiliary`: tools useful for visualization or inventory, but not for corroborating hypotheses.
- `unavailable`: dependency or endpoint not available.

<a id="métricas-nuevas"></a>
## New metrics

The orchestrator keeps nominal metrics for compatibility and adds metrics focused on real evidence:

- `support_score`: support adjusted by realism. Only counts `real_remote` and `real_local`.
- `nominal_support_score`: legacy support, before discounting heuristics and fallbacks.
- `real_coverage`: proportion of successful routes that provided real evidence.
- `real_weighted_coverage`: weighted coverage using only real evidence.
- `tool_realism_score`: weighted fraction of successful executions that were truly scientific.
- `tier_counts`: count by realism category.

<a id="mejoras-implementadas-en-esta-pasada"></a>
## Improvements implemented in this pass

- `ToolEvidenceOrchestratorService` labels each tool call with `evidence_tier`, `counts_as_real_evidence`, `realism_factor`, and `classification_reason`.
- `MultiAgentCoordinator` includes those metrics in artifacts, papers, and smokes.
- `scripts/run_ollama_cloud_research_smoke.py` exports a complete realism breakdown per tool.
- `MatplotlibService` forces loading the real `matplotlib` from `site-packages` instead of the repo's local stub.
- `LiteratureFacade` does the same before invoking `mp-api`, avoiding false failures due to local shadowing.

<a id="estado-actual"></a>
## Current status

- `PaperQA2` remains in `atlas_fallback` mode unless the real backend of the `paper-qa` package is connected and configured.
- `MatterGen`, `MatterSim`, and `AlphaGenome` remain prepared as HTTP adapters, but do not count as real evidence until their endpoints are configured and respond.
- LLM scientific reasoning routes remain useful for planning, but no longer inflate the evidence `support_score`.

<a id="smoke-recomendado"></a>
## Recommended smoke

```bash
"/workspace/atlas/.venv_new/bin/python" scripts/run_ollama_cloud_research_smoke.py \
  --domain quantum_computing \
  --output logs/agents/ollama_cloud_smoke_realism.json
```

Check in the JSON:

- `support_score` vs `nominal_support_score`
- `tool_realism_score`
- `tier_counts`
- `tool_realism_breakdown`
