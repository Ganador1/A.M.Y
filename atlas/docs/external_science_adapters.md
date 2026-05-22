# External Science Adapters

Atlas now includes a dedicated adapter layer for optional AI-for-science systems.

## Implemented adapters

- `paperqa2`
  - status: integrated
  - current runtime mode: citation-grounded Atlas fallback by default
  - optional package: `paper-qa`
- `mattergen`
  - status: scaffolded via configurable HTTP adapter
- `mattersim`
  - status: scaffolded via configurable HTTP adapter
- `alphagenome`
  - status: scaffolded via configurable HTTP adapter

## Config

Main configuration file:

- [external_science.yaml](/Volumes/Ganador%20disk/atlas/config/external_science.yaml)

Environment variables supported:

- `MATTERGEN_BASE_URL`
- `MATTERGEN_API_KEY`
- `MATTERSIM_BASE_URL`
- `MATTERSIM_API_KEY`
- `ALPHAGENOME_BASE_URL`
- `ALPHAGENOME_API_KEY`

## Service entrypoint

- [external_science_service.py](/Volumes/Ganador%20disk/atlas/app/services/external_science/external_science_service.py)

Supported actions:

- `list_adapters`
- `paperqa2_verify_claim`
- `paperqa2_answer_question`
- `mattergen_generate_candidates`
- `mattersim_simulate_candidates`
- `alphagenome_predict_variant_effects`

## Current integration points

- [literature_service.py](/Volumes/Ganador%20disk/atlas/app/services/literature/literature_service.py)
  - `verify_hypothesis_plus` now enriches results with `paperqa2`
- [tool_evidence_orchestrator.py](/Volumes/Ganador%20disk/atlas/app/services/orchestration/tool_evidence_orchestrator.py)
  - materials, biology and quantum routes now include external adapter evidence

## Notes

- The `paperqa2` adapter currently works even without the `paper-qa` package by producing a deterministic citation-grounded synthesis from Atlas literature sources.
- Remote adapters are intentionally disabled by default until real endpoints and keys are provided.
