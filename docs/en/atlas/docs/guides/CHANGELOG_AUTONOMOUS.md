> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="changelog---autonomous-agent-agent-3"></a>
# Changelog - Autonomous Agent (Agent 3)

<a id="010---2025-09-18"></a>
## [0.1.0] - 2025-09-18

<a id="added"></a>
### Added

- Scaffold `app/autonomous/` package structure (core, generators, pipelines, metrics, models).
- Core modules: priority scoring (`priority_scoring.py`), state management (`state_manager.py`), task scheduler (`task_scheduler.py`), budget allocator (`budget_allocator.py`).
- Generators: hypothesis mutator (`hypothesis_mutator.py`), proof sketch generator (`proof_sketch_generator.py`).
- Pipeline: mathematics loop (`mathematics_loop.py`).
- Models: conjecture predictor heuristic (`conjecture_predictor.py`), embedding fusion (`embedding_fusion.py`).
- Telemetry collector (`telemetry_collector.py`) with iteration counters, histogram, gauges.

<a id="integrated-030"></a>
### Integrated (0.3.0)

- Telemetry calls inside mathematics loop iteration run.

<a id="notes"></a>
### Notes

- `embedding_fusion.fuse` retains higher cyclomatic complexity (future refactor candidate).
- Persistence currently in-memory; snapshot interfaces present for future durability layer.

<a id="020---2025-09-18"></a>
## [0.2.0] - 2025-09-18

<a id="added-1"></a>
### Added

- Difficulty estimator heuristic (`difficulty_estimator.py`).
- Quantum exploration loop skeleton (`quantum_loop.py`) with telemetry integration.
- Materials exploration loop skeleton (`materials_loop.py`) with telemetry integration.
- Mathematics smoke test script (`smoke_math_loop.py`).

<a id="telemetry"></a>
### Telemetry

- Extended to domains: mathematics, quantum, materials.

<a id="next-planned"></a>
### Next (Planned)

- experimental_design_generator, novelty_assessor.
- Integration bridges agent1/agent2.
- Disk snapshot persistence + tests.

<a id="030---2025-09-18"></a>
## [0.3.0] - 2025-09-18

<a id="added-2"></a>
### Added

- Experimental design generator (`experimental_design_generator.py`).
- Heuristic novelty assessor (`novelty_assessor.py`).
- Initial bridges: agent 1 (`agent1_bridge.py`), agent 2 (`agent2_bridge.py`).
- Persistence extension: `save_snapshot`, `load_snapshot_file` in `state_manager.py`.
- Publication skeleton: `paper_builder.py`, `summary_generator.py`, `export_manager.py`.
- Unit tests: novelty assessor, experimental design, state snapshot round-trip.

<a id="integrated"></a>
### Integrated

- Novelty scoring integrated in `quantum_loop` and `materials_loop`.
- Initial experimental design (factor sweep) cached in `quantum_loop`.
- `PriorityScorer` now accepts alternative key `novelty_score` in addition to `novelty`.

<a id="internal"></a>
### Internal

- Expanded modularization for future integration (experimental planning, novelty scoring, external bridges).

<a id="next"></a>
### Next

- Integrate novelty & experimental planning in loops (quantum/materials/future chemistry).
- Export manager + paper builder.
- Expand loops: chemistry, biology, climate.
- Validators: sketch_validator, empirical_feedback.

<a id="040---2025-09-18"></a>
## [0.4.0] - 2025-09-18

<a id="added-040"></a>
### Added (0.4.0)

- Chemistry exploration loop skeleton (`chemistry_loop.py`).
- Biology exploration loop skeleton (`biology_loop.py`).
- Climate / geoscience exploration loop skeleton (`climate_loop.py`).
- Importance ranker heuristic (`importance_ranker.py`).
- Validation layer: `sketch_validator.py` (structure and completeness of sketches).
- Empirical feedback processor (`empirical_feedback.py`) heuristically adjusts parameters.
- External APIs stub (`external_apis.py`) for future integrations (literature, materials, quantum, biomolecular).

<a id="integrated-040"></a>
### Integrated (0.4.0)

- Mathematics loop now incorporates sketch validation + empirical feedback (gauges: `autonomous_feedback_adjustment_last`, `autonomous_sketch_valid_ratio`).
- Empirical feedback and adjustment gauge integrated in loops: chemistry, materials, quantum, biology, climate.
- Novelty recorded as unified gauge `autonomous_novelty_last` in all new loops.

<a id="telemetry-040"></a>
### Telemetry (0.4.0)

- Additional gauges for feedback adjustment in non-mathematical domains.

<a id="next-040"></a>
### Next (0.4.0)

- Deepen experiment design in chemistry & biology (multi-factor with adaptive criteria).
- Unification of embedding pipeline for novelty in heterogeneous domains.
- Extended persistence: incremental storage and partial recovery of large iterations.
- Refactor of `embedding_fusion.fuse` to reduce complexity.
