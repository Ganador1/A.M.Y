# Project map

The repository contains the AMY agent, the Atlas scientific laboratory and the inputs needed to reproduce the bundled results.

| Location | What it contains |
|---|---|
| `amy.py`, `core/` | Command-line entry point, heartbeat, workspace, transport, receipts and execution evidence |
| `cognition/` | Reasoning, curiosity, goals, reflection, hypothesis ranking and mathematical search |
| `memory/` | Episodic records, semantic graph, procedural skills and consolidation |
| `senses/`, `skills/` | Research inputs and executable actions |
| `communication/`, `evolution/` | Reports, manuscript support, curricula and belief-confidence updates |
| `sandbox/` | Isolation and resource limits for generated code |
| `atlas/app/`, `atlas/config/` | Scientific services, worker integration and default laboratory configuration |
| `tests/`, `atlas/tests/`, `benchmarks/` | Runtime regressions, optional Atlas integration tests and evaluation protocols |
| `atlas/alembic/`, `atlas/static/`, `atlas/templates/` | Database migrations and optional standalone application assets |
| `atlas/scripts/`, `atlas/examples/`, `scripts/examples/` | Development tools, data preparation and runnable usage examples |
| `experiments/` | Selected reproducible calibration harnesses |
| `release_evidence/` | Exact witness, numerical inputs/results, certificates and offline verifiers |
| `scripts/run/`, `scripts/verify/`, `scripts/release/` | Campaign launchers, evidence checks and packaging tools |

## Documentation

- [What AMY is and how it works](../README.md)
- [Environment setup](../ENVIRONMENT.md)
- [Scientific tool guide](../ATLAS_TOOL_GUIDE.md)
- [Reproducible experiments and tests](REPRODUCIBILITY.md)
- [Results](RESULTS.md) and [evidence scope](EVIDENCE.md)
- [Upgrading an installation](MIGRATION.md)
- [English technical reference library](ENGLISH_MANUALS.md)
- [Version changes](../CHANGELOG.md)

AMY creates local state and run outputs when it executes. Raw private conversations, caches, internal planning notes and draft publication packages are not part of this source distribution. Configuration defaults are examples to review for a new installation; user credentials belong in an untracked local environment file.
