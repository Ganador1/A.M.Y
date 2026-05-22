# Changelog - Autonomous Agent (Agent 3)

## [0.1.0] - 2025-09-18

### Added

- Scaffold `app/autonomous/` package structure (core, generators, pipelines, metrics, models).
- Core modules: priority scoring (`priority_scoring.py`), state management (`state_manager.py`), task scheduler (`task_scheduler.py`), budget allocator (`budget_allocator.py`).
- Generators: hypothesis mutator (`hypothesis_mutator.py`), proof sketch generator (`proof_sketch_generator.py`).
- Pipeline: mathematics loop (`mathematics_loop.py`).
- Models: conjecture predictor heuristic (`conjecture_predictor.py`), embedding fusion (`embedding_fusion.py`).
- Telemetry collector (`telemetry_collector.py`) with iteration counters, histogram, gauges.

### Integrated (0.3.0)

- Telemetry calls inside mathematics loop iteration run.

### Notes

- `embedding_fusion.fuse` retains higher cyclomatic complexity (future refactor candidate).
- Persistence currently in-memory; snapshot interfaces present for future durability layer.

## [0.2.0] - 2025-09-18

### Added

- Difficulty estimator heuristic (`difficulty_estimator.py`).
- Quantum exploration loop skeleton (`quantum_loop.py`) con integración telemetría.
- Materials exploration loop skeleton (`materials_loop.py`) con integración telemetría.
- Smoke test script matemáticas (`smoke_math_loop.py`).

### Telemetry

- Extendida a dominios: mathematics, quantum, materials.

### Next (Planned)

- experimental_design_generator, novelty_assessor.
- Integración bridges agent1/agent2.
- Persistencia snapshot disco + pruebas.

## [0.3.0] - 2025-09-18

### Added

- Experimental design generator (`experimental_design_generator.py`).
- Novelty assessor heurístico (`novelty_assessor.py`).
- Bridges iniciales: agente 1 (`agent1_bridge.py`), agente 2 (`agent2_bridge.py`).
- Extensión persistencia: `save_snapshot`, `load_snapshot_file` en `state_manager.py`.
- Publication skeleton: `paper_builder.py`, `summary_generator.py`, `export_manager.py`.
- Unit tests: novelty assessor, experimental design, state snapshot round-trip.

### Integrated

- Novelty scoring integrado en `quantum_loop` y `materials_loop`.
- Experimental design inicial (factor sweep) cacheado en `quantum_loop`.
- `PriorityScorer` ahora acepta clave alternativa `novelty_score` además de `novelty`.

### Internal

- Modularización ampliada para integración futura (experimental planning, novelty scoring, bridges externos).

### Next

- Integrar novelty & experimental planning en loops (quantum/materials/química futura).
- Export manager + paper builder.
- Ampliar loops: chemistry, biology, climate.
- Validadores: sketch_validator, empirical_feedback.

## [0.4.0] - 2025-09-18

### Added (0.4.0)

- Chemistry exploration loop skeleton (`chemistry_loop.py`).
- Biology exploration loop skeleton (`biology_loop.py`).
- Climate / geoscience exploration loop skeleton (`climate_loop.py`).
- Importance ranker heuristic (`importance_ranker.py`).
- Validation layer: `sketch_validator.py` (estructura y completitud de bosquejos).
- Empirical feedback processor (`empirical_feedback.py`) ajusta heurísticamente parámetros.
- External APIs stub (`external_apis.py`) para futuras integraciones (literature, materials, quantum, biomolecular).

### Integrated (0.4.0)

- Mathematics loop ahora incorpora validación de bosquejos + feedback empírico (gauges: `autonomous_feedback_adjustment_last`, `autonomous_sketch_valid_ratio`).
- Feedback empírico y gauge de ajuste integrados en loops: chemistry, materials, quantum, biology, climate.
- Novedad registrada como gauge unificado `autonomous_novelty_last` en todos los nuevos loops.

### Telemetry (0.4.0)

- Gauges adicionales para ajuste de feedback en dominios no matemáticos.

### Next (0.4.0)

- Profundizar experiment design en chemistry & biology (multi-factor con criterios adaptativos).
- Unificación de embedding pipeline para novelty en dominios heterogéneos.
- Persistencia extendida: almacenamiento incremental y recuperación parcial de iteraciones grandes.
- Refactor de `embedding_fusion.fuse` para reducir complejidad.

