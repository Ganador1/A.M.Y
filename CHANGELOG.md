# Changelog

All notable changes to A.M.Y are documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-05-21 — First public release

### Added — Multi-agent paper pipeline
- **Reflection Agent** ([`cognition/reflection_agent.py`](cognition/reflection_agent.py)): structured self-review with a six-check rubric (numerical-claim grounding, explicit limitations, falsifiable predictions, citation freshness, statistical reporting, alternative explanations). Returns score 0–100, pass / fail, and concrete suggestion per issue. Wired into [`communication/paper_generator.py`](communication/paper_generator.py) as an advisory gate; appends a Self-Review section to every draft.
- **Ranking Agent** ([`cognition/ranking_agent.py`](cognition/ranking_agent.py)): Elo tournament over candidate hypotheses with K-factor decay (FIDE-style). Two judges:
  - `heuristic_judge` (default): deterministic, no network calls.
  - `llm_judge` (opt-in via `AMY_USE_LLM_JUDGE=1`): async pairwise comparison via `OllamaCloudClient`, with automatic fallback to the heuristic on any error.
- **Extended Atlas tools** ([`atlas/app/extended_science_tools.py`](atlas/app/extended_science_tools.py)): 9 new tools backed by real libraries.
  - AstroPy: `astropy_constants`, `astropy_unit_convert`, `astropy_cosmology`, `astropy_blackbody`.
  - PySCF: `pyscf_hf_energy`, `pyscf_dft_energy`.
  - ASE: `ase_optimize`, `ase_thermochemistry`.
  - PyMatGen: `pymatgen_structure`.
  - Total Atlas tool count: **85 → 94**.
- **`describe_tools` action** in [`core/atlas_worker.py`](core/atlas_worker.py) and [`core/atlas_tools.py`](core/atlas_tools.py): A.M.Y can now ask Atlas for tool descriptions and input-format strings, so the LLM picks the right tool without guessing.
- **Stdout isolation in `atlas_worker.run_tool`**: tools that print during execution (brian2, libsbml) no longer corrupt the JSON protocol between worker and A.M.Y.
- **Diversified paper abstracts** ([`communication/paper_enhancer.py`](communication/paper_enhancer.py)): 5 opening variants × 4 finding phrasings × 3 closings × 3 hypothesis phrasings = 180 combinations. Seeded by `hash(topic)` for reproducibility — same topic produces same abstract.
- **Experimental harness** ([`experiments/`](experiments/)):
  - `ab_test/` — baseline vs improved comparison with deterministic rubric.
  - `all_domains/` — one paper per Atlas domain (23 / 23 covered).
  - `flagship/` — GPT-5-style deep-dive paper.
  - `multimodel/` — same topic with multiple Ollama Cloud models.

### Added — Project packaging
- [`pyproject.toml`](pyproject.toml): `pip install -e .` ready, `amy` console script entry point.
- [`pytest.ini`](pytest.ini) with `asyncio_mode = auto`.
- Root [`conftest.py`](conftest.py): path + cwd fixtures so tests under `tests/` can find top-level modules.
- [`LICENSE`](LICENSE) Apache-2.0 (root and atlas/ kept in sync).
- [`ENVIRONMENT.md`](ENVIRONMENT.md): documents the two-venv layout (`.venv` for A.M.Y on Python 3.14, `atlas/.venv_new` for Atlas tools on Python 3.13).
- Pinned [`requirements.txt`](requirements.txt) for reproducibility.

### Changed — Repository reorganisation
- Root `.py` count: **71 → 3** (`amy.py`, `conftest.py`, `test_atlas_by_branch.py`).
- 35 test files moved to [`tests/`](tests/).
- 35 run / diagnostic / analysis scripts moved to [`scripts/run/`](scripts/run/), [`scripts/diagnostics/`](scripts/diagnostics/), [`scripts/analysis/`](scripts/analysis/).
- 21 stale JSON / log / PNG artefacts moved to [`artifacts/`](artifacts/) (gitignored).
- Deleted obsolete `atlas/.venv` (4.1 GB), `:memory:/`, `config.yaml.bak`, top-level `.DS_Store`.

### Fixed
- **`prime_gap_analysis`** silently capped at 100,000 ([`atlas/app/run_agent_with_tools_legacy.py:2302`](atlas/app/run_agent_with_tools_legacy.py#L2302)). Cap raised to 10⁷ and an explicit "NOTE: requested limit exceeded the hard cap" notice is emitted when truncation happens. Verified: N = 10⁶ now returns 78,498 primes (previously silently 9,592).
- **`molecular_weight_calc`** returned 0 for pure-element inputs like `He` / `Ne` in older code paths; fixed in the active service.
- **`sympy_derivative` / `sympy_integrate` / `sympy_prime_analysis`** crashed with `list index out of range` on malformed input. Now return a helpful error message with the expected format and concrete examples.
- **Reflection regex** for "Testable Predictions" now tolerates both `##` headings and `**bold**` inline.
- **Provenance ID regex** now accepts hex / mixed suffixes (`<domain>_<tool>_<YYYYMMDD>_<HHMMSS>_<hex>`).
- **Numerical-grounding** check now tolerates truncation (e.g. `5.5` is grounded by `5.5000`).

### Validated — Measured A/B improvements
With seven baseline papers and seven regenerated papers under the new pipeline:

| Metric | Baseline | Improved | Δ |
|---|---:|---:|---:|
| **Total rubric score** | 49.65 | 66.93 | **+17.28 (+34.8%)** |
| Provenance integrity | 2.86 | 10.00 | +7.14 (+250%) |
| Falsifiability | 0.86 | 5.00 | +4.14 (+483%) |
| Numerical claims grounded | 4.29 | 11.04 | +6.76 (+157%) |
| Explicit limitations | 2.86 | 8.57 | +5.71 (+200%) |
| Statistical rigor | 3.43 | 8.64 | +5.21 (+152%) |

### Validated — All-23-domain run
23 papers, one per Atlas domain, generated in ~7 minutes. 0 weak, 21 good, 2 strong. Average rubric 71.00 / 100. See [`experiments/all_domains/REVIEW.json`](experiments/all_domains/REVIEW.json).

### Validated — Flagship paper
GPT-5-style deep dive on the Cramér–Granville heuristic. 14 tool calls, derived Cramér-ratio table across four decades, all SHA-256 provenance verified. Rubric 71.00, reflection 100, pass. See [`experiments/flagship/papers/`](experiments/flagship/papers/).

## [0.9.0] — 2026-04-23 — Pre-release

### Added
- Robust JSON parsing (`cognition/reasoning.py`) and pre-execution syntax check (`sandbox/executor.py`).
- Implemented missing modules: `senses/api_sensor.py`, `senses/file_sensor.py`, `evolution/curriculum.py`, `evolution/self_retrain.py`, `evolution/strategy_optimizer.py`.
- Initial test suite: `test_amy_quick.py`, `tests/test_core.py`, `test_atlas_tools.py`, `test_reproducibility.py`.
- Documentation drafts: `README_PUBLIC.md`, `SCIENCE_MANIFESTO.md`.

### Validated
- Atlas tools: 7 / 8 pass across 8 scientific domains.
- Reproducibility: three consecutive runs produce identical results (fixed seeds + SHA-256 fingerprinting).

### Known issues
- Literature search async / coroutine handling.
- Some Atlas tools require specific input formats.

### Dependencies
- Python 3.13+, PyTorch 2.x with MPS support, ChromaDB, JAX, Atlas subproject with 84 tools.

## [0.8.0] — 2026-04-01

### Added
- Initial integration with AXIOM Atlas.
- Peer review paper generation.
- Breakthrough detection.
- Multi-domain research capabilities.

## [0.7.0] — 2026-03-15

### Added
- Global Workspace Theory implementation.
- Active Inference world model.
- SOAR-like goal stack.
- ICM / RND curiosity module.

## [0.6.0] — 2026-02-28

### Added
- Sandbox executor with Docker support.
- Episodic + semantic memory.
- Skill library with retrieval.
- Web sensor for literature search.

## [0.5.0] — 2026-02-10

### Added
- Heartbeat cognitive cycle.
- Ollama Cloud integration with dual API-key load balancing.
- ReAct-style reasoning engine.
- Experiment generation and execution.

## [0.1.0] — 2025-10-01

### Added
- Initial project structure.
- Core architecture design.
- Configuration system.
- Basic logging with structlog.
