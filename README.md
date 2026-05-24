# A.M.Y

> An artificial mind that never sleeps. Thinks, researches, experiments, learns, and evolves autonomously.

**[Science Manifesto](SCIENCE_MANIFESTO.md)** · **[Atlas Tool Guide](ATLAS_TOOL_GUIDE.md)** · **[Changelog](CHANGELOG.md)** · **[Use Policy](USE_POLICY.md)** · **[Security](SECURITY.md)** · **[Contributing](CONTRIBUTING.md)**

---

## Status (May 2026)

| Component | Status | Tests |
|---|---|---|
| Core (heartbeat, world model, workspace) | ✅ Functional | 30/30 pass |
| Cognition (reasoning, goals, curiosity, **Reflection**, **Ranking**) | ✅ Functional | ✅ Pass |
| Memory (episodic, semantic, procedural) | ✅ Functional | ✅ Pass |
| Sandbox (isolated execution) | ✅ Functional | ✅ Pass |
| **Atlas Tools (94 tools, 23 domains)** | ✅ Functional | 100% verified |
| Evolution (curriculum, self-retrain) | ✅ Implemented | ✅ Pass |
| Senses (web, time, file, api) | ✅ Functional | ✅ Pass |
| Communication (paper generator + Reflection gate) | ✅ Functional | ✅ Pass |

**Last validation:** May 21, 2026.

**Multi-domain coverage:** 23 / 23 Atlas domains produce papers end-to-end, with provenance integrity verified by SHA-256.

---

## Vision

A.M.Y is not a chatbot. It is not an agent that waits for your question. It is an **autonomous artificial mind**: once given a research goal, it continuously investigates, reflects, experiments, retrains on its own findings, and only contacts you when there is something to report.

## Scientific foundations

| Pillar | Source | Role inside A.M.Y |
|---|---|---|
| **Active Inference** | Karl Friston (Free Energy Principle) | Continuous perception-action loop minimising surprise. Curiosity emerges naturally. |
| **Global Workspace Theory** | Bernard Baars / Stanislas Dehaene | Attention bus: modules compete for the "focus of consciousness" and broadcast to all others. |
| **SOAR Cognitive Architecture** | Laird, Newell, Rosenbloom | Operative cycle: propose → evaluate → execute. Recursive substates. Chunking. |
| **Curiosity-Driven Learning** | Pathak et al. (ICM / RND) | Intrinsic motivation: when no extrinsic progress, curiosity drives exploration. |
| **Voyager** | Wang et al. 2023 (NVIDIA/Caltech) | Skill library + automatic curriculum + self-verification. |
| **NELL** | Tom Mitchell et al. (CMU) | 24 / 7 continual learning with a growing knowledge base. |
| **Sakana AI Scientist v2** | arXiv:2504.08066 | End-to-end paper generation with internal reviewing. |
| **Google AI Co-Scientist** | DeepMind 2025 | Multi-agent reflection + Elo tournament for hypothesis ranking. |
| **Human-AI Science Case Studies** | arXiv:2511.16072 | Human-AI collaboration patterns documented as case studies. |

## What A.M.Y can produce (today)

- **Real scientific tool calls.** 94 tools across 23 domains: SymPy, NumPy, SciPy, RDKit, **PySCF** (HF / DFT), **ASE** (atomistic MD), **AstroPy** (cosmology + units), **PyMatGen** (crystal structures), **BioPython**, **ClinicalBERT**, **GNoME materials**, Z3 prover, and more.
- **End-to-end papers** with sections, hypotheses, citations, SHA-256 provenance, and an automatic Self-Review block produced by the **Reflection Agent** (Sakana / Co-Scientist pattern).
- **Hypothesis ranking via Elo tournament** before the paper foregrounds any claim (Google Co-Scientist pattern). Optional LLM-backed judge via `AMY_USE_LLM_JUDGE=1`.
- **Reproducibility per paper.** Every tool invocation gets a [`data/experiments/<id>/provenance.json`](data/experiments) file with input, output preview, SHA-256 of full output, and full environment record.

## Recent benchmark

23 papers, one per Atlas domain, generated in ~7 minutes:

| Metric | Value |
|---|---:|
| Average rubric score | **71.00 / 100** |
| Average reflection score | **100 / 100** |
| Verdict tally | **STRONG = 2 · GOOD = 21 · WEAK = 0** |
| Highest-scoring paper | 80.45 (Prime Counting and Twin Prime Density) |
| Lowest-scoring paper | 62.42 (AM Process Configuration) |

See [`experiments/all_domains/REVIEW.json`](experiments/all_domains/REVIEW.json) for the full breakdown and [`experiments/flagship/papers/`](experiments/flagship/papers/) for a deep-dive paper modelled on the arXiv:2511.16072 case-study format (rubric 71, reflection 100, 14 verifiable tool calls).

## How A.M.Y thinks — the cognitive cycle in depth

A.M.Y is built around a continuous **heartbeat loop**. The loop never returns; it is the loop, not an `if __name__` block, that defines the agent. Each tick of the loop runs the same five-phase cognitive cycle inspired by SOAR, Active Inference, and Global Workspace Theory.

### The five phases of one heartbeat

1. **PERCEIVE** — `senses/` modules read the world. `web_sensor.py` pulls fresh literature (arXiv, PubMed-style sources). `time_sensor.py` advances the clock. `file_sensor.py` watches local data. `api_sensor.py` polls APIs the user wired in. The new perceptions are reduced to surprise signals against the current world model.

2. **ATTEND** — `core/global_workspace.py` runs the attention bus. Every cognitive module (curiosity, goal stack, memory recall, reflection) submits a bid for the workspace. The highest-utility bid wins the tick and gets broadcast to all modules. This is the explicit implementation of Bernard Baars' Global Workspace Theory: only one thought is "conscious" at a time, but every subsystem hears it.

3. **THINK** — `cognition/reasoning.py` runs a recursive chain over the winning workspace content. For a typical research tick this means: form a hypothesis, decompose it into testable predictions, identify which Atlas tools could falsify each prediction, plan the call sequence. `cognition/curiosity.py` (ICM / RND) injects an intrinsic reward signal proportional to expected information gain, so dull tool calls are deprioritised even when they would succeed.

4. **ACT** — A.M.Y picks the best plan and executes it. Scientific tool calls go through `core/atlas_tools.py`, which speaks JSON to a persistent Atlas worker (see Atlas section below). Code experiments go through `sandbox/executor.py`, which validates syntax and resource limits before running. Results flow back into memory and into the next perception.

5. **LEARN** — `memory/episodic.py` records what happened. `memory/semantic.py` updates the knowledge graph (a NetworkX DiGraph backed by ChromaDB for embedding search). `memory/procedural.py` chunks any new successful skill into the Voyager-style skill library at `skills/library.py`. `evolution/curriculum.py` decides what to study next; `evolution/self_retrain.py` adjusts internal model weights when there is enough new signal.

The loop then returns to PERCEIVE. There is no exit condition. The loop runs until the OS kills it.

## The two new multi-agent components

A.M.Y v1.0 introduces two cognitive agents inspired by the published architectures of Sakana AI Scientist v2 and Google DeepMind's AI Co-Scientist. Both are pure-Python, no external services, and falsifiable through tests.

### Ranking Agent — Elo tournament over hypotheses

When the paper enhancer generates N candidate hypotheses, A.M.Y does not pick the first plausible one. Instead it runs a round-robin pairwise tournament:

```python
from cognition.ranking_agent import run_tournament

candidates = [
    {"hypothesis": "Bond energies follow electronegativity scaling",
     "novelty_status": "known_control", "confidence": 0.85},
    {"hypothesis": "PySCF HF/sto-3g HOMO-LUMO gap of H2 is within 5% of literature",
     "novelty_status": "candidate_novelty", "confidence": 0.70},
    # ... more
]
ranked = run_tournament(candidates, rounds=2, seed=42)
top = ranked[0]   # highest-Elo hypothesis
```

Two judges are available:

- `heuristic_judge` — deterministic, no API calls. Scores each hypothesis on novelty status (40%), confidence (20%), specificity proxy (20%), and falsifiability markers like the words "test", "measure", "compare against" (20%). Then the pair's normalised scores become the Elo update.
- `llm_judge` — async pairwise call to an Ollama Cloud model. Opt in with `AMY_USE_LLM_JUDGE=1`. Override the model with `AMY_RANKING_MODEL=qwen3-next:80b` (or any model your cloud key can reach). Falls back to the heuristic on any error.

K-factor follows FIDE rules: 40 for the first 5 matches per record, 20 up to 15, then 10. This makes early matches matter more, which is what you want when N is small.

The top-K hypotheses get foregrounded in the manuscript with their Elo and tournament record, so readers can see *that* the ranking happened and *how* each candidate fared.

### Reflection Agent — structured self-review gate

Before a paper is finalised, `cognition/reflection_agent.py` runs a deterministic six-check rubric against the draft:

1. **Numerical-claim grounding.** Every number in the Discussion section must trace to a `data/experiments/<id>/provenance.json` output. Unsupported numbers raise a `high` severity issue.
2. **Explicit limitations.** The paper must say what it is *not* claiming. The agent looks for phrases like "does not claim", "calibration control", "without asserting novelty".
3. **Falsifiability of hypotheses.** Each `H<n>.` block must have an explicit test procedure. Phrases like "Testable via:", "measure", "compare against" satisfy this.
4. **Citation freshness.** Unverified citations (marked by the upstream `CitationVerifier`) lower the score.
5. **Statistical reporting.** If the manuscript touches statistics, it should mention p-values, confidence intervals, effect sizes, or n.
6. **Alternative explanations.** The Discussion should consider competing explanations, not only the favoured interpretation.

Issues are returned as `{severity, section, message, suggestion}`. The agent annotates the draft with a `## Self-Review (Reflection Agent)` block listing all medium and high issues, so peer reviewers (or the author) get an honest map of the paper's weak points. The agent is *advisory*: drafts are not rejected by the Reflection score alone (the `_prepublication_gate` already handles hard rejections), but the score and issues are persistent and visible.

## Atlas / AXIOM — the scientific platform underneath

A.M.Y does not call SymPy or PySCF directly. It speaks JSON over stdin / stdout to a persistent worker process that owns the entire AXIOM Atlas platform. This isolation is deliberate: it keeps the A.M.Y cognitive state separate from heavy scientific imports, lets Atlas run on Python 3.13 while A.M.Y runs on Python 3.14, and makes every Atlas call a structured request/response with explicit timeouts and error handling.

### What AXIOM Atlas is

AXIOM Atlas is a scientific research platform with three layers:

- **Tool registry** (`atlas/app/run_agent_with_tools_legacy.py`, `atlas/app/extended_science_tools.py`) — 94 callable tools organised by domain. Each tool has a `name`, `domain`, `description`, `input_format`, and a callable. Adding a new tool is one `register_tool(ToolDescriptor(...))` call.
- **Service layer** (`atlas/app/services/`, `atlas/app/domains/`) — long-running services for the heavier capabilities: AlphaFold 3 protein structure, ClinicalBERT text NER, GNoME materials discovery, additive manufacturing process configuration, gravitational lensing, light EEG band-power analysis, climate evidence orchestration, and more.
- **Safety kernel** (`atlas/app/security/`) — the misuse guard, the actor-tracking risk policy, and the safety wrapper that every tool call must pass through. Fails closed by design.

The full surface area (FastAPI app, multi-agent orchestrator, peer review pipeline, Lean 4 management, quantum computing experiments) lives in `atlas/` and can be used independently of A.M.Y; A.M.Y is one consumer among possible others.

### The 94 tools, by domain

| Domain | Count | Notable tools |
|---|---:|---|
| Mathematics | 20 | `sympy_solve_equation`, `sympy_derivative`, `sympy_integrate`, `sympy_simplify`, `sympy_prime_analysis`, `prime_gap_analysis`, `number_theory_advanced`, `mathematical_discovery`, `conjecture_engine`, `automated_prover`, `z3_prover`, `z3_verify_theorem`, `graph_theory`, `topology_invariants`, `symbolic_calculus`, `calculus_engine` |
| Chemistry | 18 | `molecular_weight_calc`, `bond_energy_analyzer`, `molecular_orbital_energy`, `computational_chemistry`, `pyscf_hf_energy`, `pyscf_dft_energy`, `ase_optimize`, `ase_thermochemistry`, plus 6 service-backed adapters (advanced NMR, computational chemistry, ChemML, molecular dynamics, X-ray crystallography, differential scanning calorimetry) |
| Physics | 12 | `quantum_energy_levels`, `quantum_circuit`, `astropy_constants`, `astropy_blackbody`, `calculus_engine`, plus services for plasma physics, particle physics, solid-state physics, quantum physics, gravitational lensing, physics-informed neural networks |
| Biology | 7 | `dna_analyzer`, `sequence_analyzer`, `protein_properties`, `dnabert2_analysis`, plus services for genomics, computational biology, alphafold3 protein structure |
| Statistics | 5 | `numpy_statistics`, `numpy_distribution`, `numpy_correlation`, `correlation_analysis`, `hypothesis_tester` |
| Astronomy | 4 | `astropy_cosmology`, `astropy_blackbody`, plus astronomical ML and gravitational lensing services |
| Medicine | 4 | ClinicalBERT NER service, AlphaFold 3, advanced medical imaging, evidence corroboration |
| Materials | 3 | `gnome_materials`, `pymatgen_structure`, materials discovery service |
| Engineering | 3 | additive manufacturing, synthesis equipment, evidence corroboration |
| Neuroscience | 2 | light EEG band-power service, evidence corroboration |
| Number theory | 2 | `number_theory_advanced`, `prime_gap_hpc` |
| Materials science | 2 | `gnome_materials`, evidence corroboration |
| Research / meta | 3 | `literature_search`, `literature_verify_hypothesis_plus`, `validate_hypothesis` |
| Evidence corroboration | 15 | `evidence_corroborate_<domain>` for all 15 corroboration domains, each running a multi-tool orchestrator that mixes real, heuristic, and remote evidence sources |
| Other domain services | 4 | climate, drug discovery, energy storage, manufacturing, medical imaging, plasma physics, quantum computing, biomedical engineering, biophysics |

### The atlas_worker protocol

A.M.Y's `core/atlas_worker.py` is launched as a long-running subprocess. It speaks line-delimited JSON over stdin/stdout. Three actions are supported:

```
→ {"id": 1, "action": "ping"}
← {"id": 1, "result": "pong"}

→ {"id": 2, "action": "list_tools", "domain": "chemistry"}
← {"id": 2, "result": ["molecular_weight_calc", "pyscf_hf_energy", ...]}

→ {"id": 3, "action": "describe_tools", "domain": "chemistry"}
← {"id": 3, "result": [{"name": "pyscf_hf_energy", "domain": "chemistry",
                        "description": "...", "input_format": "..."}]}

→ {"id": 4, "action": "run_tool",
   "tool_name": "pyscf_hf_energy",
   "tool_input": "H 0 0 0; H 0 0 0.74"}
← {"id": 4, "result": "PySCF Hartree-Fock RHF result:\n  Total energy: -1.11675931 Ha..."}
```

Two design decisions matter here. First, `run_tool` redirects the worker's `sys.stdout` to an in-memory buffer during execution, so any tool that prints (Brian2, libsbml) cannot corrupt the JSON channel. Second, the safety kernel and the misuse guard are evaluated *before* the worker is even reached, so a blocked operation never starts up its dependencies.

### Provenance — what gets written every time a tool runs

For every successful tool invocation A.M.Y creates a directory under `data/experiments/<id>/`:

```
data/experiments/mathematics_prime_gap_analysis_20260521_155341_a1b2c30/
├── provenance.json
└── output.txt
```

`provenance.json` carries:

```json
{
  "experiment_id": "mathematics_prime_gap_analysis_20260521_155341_a1b2c30",
  "timestamp": "2026-05-21T15:53:41+00:00",
  "tool": {
    "name": "prime_gap_analysis",
    "input": "1000000",
    "output_hash": "<sha256 of output.txt>",
    "output_length": 263,
    "success": true,
    "duration_seconds": 8.41
  },
  "output_preview": "Prime gap analysis up to 1000000:\n  Number of primes: 78498...",
  "domain": "mathematics",
  "environment": {
    "python_version": "3.13.5",
    "platform": "Darwin",
    "machine": "arm64"
  }
}
```

`output.txt` carries the full tool output. The SHA-256 in `provenance.json` is the hash of `output.txt`. The rubric scorer recomputes that hash on every paper review and rejects manuscripts where the claimed hash does not match. This is what makes the system *honest*: a paper cannot make a numerical claim without a provenance file that resolves to a verifiable hash.

### Adding a new Atlas tool

If you want A.M.Y to use a new scientific library, the cycle is:

1. Add a wrapper function in `atlas/app/extended_science_tools.py` (or a new module).
2. Register a `ToolDescriptor` with `name`, `domain`, `description`, and `input_format`.
3. Restart the worker. A.M.Y picks up the new tool through `describe_tools` automatically.

The Atlas misuse guard runs against every input before the tool is reached, so new tools inherit the safety policy without writing any policy code.

## Showcase papers

The `papers/showcase/` directory contains the curated set of papers A.M.Y has produced. They illustrate what the pipeline does *today*, scored by the same deterministic rubric:

1. **`01_FLAGSHIP_prime_gaps_cramer.md`** — flagship deep-dive on the Cramér-Granville heuristic. 14 verifiable Atlas tool calls across four decades of N (10^3 to 10^6, plus the 10^7 audit that surfaced the original cap bug). Includes a derived Cramér-ratio table and a falsifiable prediction. Rubric 71, Reflection pass.
2. **`02_mathematics_prime_counting.md`** — top-ranked all-domain paper (rubric 80.45). Reproduces π(N), twin-prime density, and the 1000th prime across multiple decades, all with provenance.
3. **`03_quantum_computing_bell_state.md`** — Bell-state preparation as a NISQ hardware calibration control. Quantum circuit simulation plus literature grounding.
4. **`04_chemistry_cross_level.md`** — cross-level comparison of IUPAC tables, Hartree-Fock, B3LYP DFT, and EMT atomistic on the same small molecules.
5. **`05_astronomy_cosmology.md`** — Planck18 cosmological distances and stellar blackbody spectra. Generated entirely with AstroPy tools added in v1.0.
6. **`06_novelty_cramer_six_decades.md`** — the only paper in the current showcase with a measured novelty score of 30. The novelty signal comes from extending the Cramér ratio audit to N = 10^7, which became possible after the prime_gap_analysis cap bug was fixed during the all-domain run.

The full 23-domain batch lives in `experiments/all_domains/papers/` and is reproducible with `python experiments/all_domains/generate_all.py` followed by `generate_remaining.py`. The rubric scorer is at `experiments/ab_test/scoring/score_paper.py`.

## A/B and multi-model experiments

`experiments/` contains the full experimental harness used to validate every claim in this README:

- **`ab_test/`** — baseline vs improved rubric comparison. Reports +17.28 points on average (+34.8%) after wiring the Reflection and Ranking agents.
- **`all_domains/`** — one paper per Atlas domain (23 / 23 covered).
- **`flagship/`** — the flagship deep dive.
- **`multimodel/`** — same topic run across seven model configurations. Spread across models was small (50-52 rubric), which surfaced an honest finding: the paper enhancer is template-driven today, and the model only affects ranking judgements when LLM-judge is on.
- **`novelty_hunt/`** — eight papers on diverse cross-scale topics designed to surface novelty signals.

Every harness emits a `RESULTS.json` you can re-score yourself. Nothing in this README is unverifiable from the repository.
## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     A.M.Y COGNITIVE CORE                        │
│                                                                 │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐  ┌───────────┐ │
│  │PERCEPTION│  │  WORLD MODEL │  │ GOAL STACK│  │ CURIOSITY │ │
│  │ (senses) │→ │ (free energy)│← │ (SOAR)    │← │ (ICM/RND) │ │
│  └──────────┘  └──────────────┘  └───────────┘  └───────────┘ │
│        ↓              ↕                ↓               ↓       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            GLOBAL WORKSPACE  (attention bus)             │   │
│  │   Modules compete → winner broadcasts to all             │   │
│  └─────────────────────────────────────────────────────────┘   │
│        ↓              ↓                ↓               ↓       │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐  ┌───────────┐ │
│  │  SKILL   │  │  KNOWLEDGE   │  │ EXPERIMENT│  │  SELF-    │ │
│  │  LIBRARY │  │  GRAPH       │  │ ENGINE    │  │  RETRAIN  │ │
│  │  Voyager │  │  NELL-like   │  │ sandbox   │  │  loop     │ │
│  └──────────┘  └──────────────┘  └───────────┘  └───────────┘ │
│        ↓              ↓                ↓               ↓       │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────────────┐│
│  │  RANKING │  │  REFLECTION  │  │  PAPER  GENERATOR         ││
│  │   AGENT  │  │    AGENT     │  │  (Markdown + PDF + SHA)   ││
│  │  Elo     │  │  6-rubric    │  │  + Atlas provenance       ││
│  └──────────┘  └──────────────┘  └───────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                    ↕ HEARTBEAT LOOP (never stops)
```

## Repository layout

```
A.M.Y/
├── amy.py                       # Entry point — starts the heartbeat
├── pyproject.toml               # pip-installable
├── requirements.txt             # Pinned versions
├── pytest.ini                   # asyncio mode = auto
├── conftest.py                  # Test path + cwd fixture
├── ENVIRONMENT.md               # venv layout (root + atlas/.venv_new)
├── LICENSE                      # Apache-2.0
│
├── core/                        # Cognitive core: heartbeat, workspace, atlas bridge
│   ├── atlas_tools.py           # Async client to Atlas worker
│   ├── atlas_worker.py          # Persistent stdin/stdout JSON protocol
│   ├── global_workspace.py
│   └── ...
│
├── cognition/                   # Reasoning, goals, curiosity, reflection, ranking
│   ├── reasoning.py
│   ├── reflection_agent.py      # NEW — Sakana / Co-Scientist self-review
│   └── ranking_agent.py         # NEW — Elo tournament + LLM judge
│
├── memory/                      # episodic, semantic, procedural, consolidation
├── senses/                      # web, time, file, api sensors
├── skills/                      # Voyager-style skill library
├── communication/               # Paper generator + Reflection gate
├── sandbox/                     # Isolated experiment execution
├── evolution/                   # Curriculum + self-retrain
│
├── atlas/                       # 94 scientific tools, 23 domains
│   ├── app/extended_science_tools.py  # NEW — AstroPy/PySCF/ASE/PyMatGen
│   ├── app/run_agent_with_tools_legacy.py
│   └── ...
│
├── tests/                       # 36 test files, 30+ pass
├── scripts/                     # run/, diagnostics/, analysis/
├── experiments/                 # all_domains/, flagship/, ab_test/, multimodel/
├── papers/                      # Generated papers (Markdown + PDF)
└── data/experiments/            # Provenance JSON + raw output per tool call
```

## Quick start

```bash
# 1. Set up environments (see ENVIRONMENT.md for the full layout)
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -e .

# 2. Add your Ollama Cloud key
cp .env.example .env
# edit .env with OLLAMA_CLOUD_API_KEY=...

# 3. Run the cognitive loop with a goal
.venv/bin/python amy.py --goal "Investigate prime-gap statistics across decades"

# 4. Or generate a one-shot paper batch
.venv/bin/python experiments/all_domains/generate_all.py
.venv/bin/python experiments/all_domains/generate_remaining.py

# 5. Score the papers
.venv/bin/python experiments/all_domains/review_all.py
```

## Configuration knobs

| Env var | Effect |
|---|---|
| `OLLAMA_CLOUD_API_KEY` | Required. Primary Ollama Cloud key. |
| `OLLAMA_CLOUD_API_KEY_2` | Optional failover key. |
| `AMY_USE_LLM_JUDGE=1` | Use LLM-backed pairwise judge in the Ranking Agent (default: deterministic heuristic). |
| `AMY_RANKING_MODEL` | Override the model the LLM judge uses (e.g. `qwen3-next:80b`). |
| `ATLAS_ACTOR_ID` | Identity logged by Atlas misuse guard. |
| `MPLBACKEND=Agg` | Forced by the worker for headless plotting. |

## Design philosophy

1. **Never sleeps.** The heartbeat loop runs indefinitely. With no urgent task, it reflects, consolidates memory, or explores out of curiosity.
2. **Recursive by nature.** Every finding spawns new questions. Every question spawns sub-goals.
3. **Doesn't need you.** It only contacts you when it discovers something significant.
4. **Learns for real.** It does not only accumulate text. It retrains internal models, optimises strategies, and discards what does not work.
5. **Experiments.** It writes code, runs it in a sandbox, analyses results, and adjusts the next hypothesis.
6. **Honest about itself.** Every paper carries a Reflection block listing high / medium / low severity issues raised by an internal peer-review pass.

## Comparison with state-of-the-art (May 2026)

| Aspect | Sakana AI Scientist v2 | Google Co-Scientist | Human-AI science case study | **A.M.Y** |
|---|---|---|---|---|
| Domains autonomously covered | 1 (ML) | ~2 (bio + chem) | 6 (assisted) | **23 (autonomous)** |
| Papers in one run | 1 / 30 min | 1 / 60 min (assisted) | manual | **23 / 7 min** |
| Open source | Yes (no Nature artefact) | No | No | **Yes (Apache-2.0)** |
| Cryptographic provenance | LaTeX templates | Limited | Manual citations | **SHA-256, 100% verifiable** |
| Tournament Elo | No | Yes | No | **Yes (heuristic + LLM judge)** |
| Formal self-review | Yes (multi-LLM) | Yes (Reflection) | No | **Yes (Reflection Agent gate)** |


## Responsible use

A.M.Y ships with a built-in misuse guard (atlas/app/security/misuse_guard.py) that fails closed and blocks operations in eight categories:

- Chemical weaponisation
- Biological weaponisation (gain-of-function, pathogen enhancement)
- Cyber abuse (exploits, malware, credential theft)
- Unauthorised human experimentation
- Guardrail tampering (disabling the safety policy itself)
- Fissile materials (synthesis, enrichment, weaponisation)
- Mass surveillance and individual targeting
- Critical infrastructure attack (power grid, SCADA, elections)

The guard is enforced before any tool runs and again before any subprocess starts. If you ship a fork that disables it, you take ownership of that decision; please use a different name so users can tell the projects apart.

The capabilities A.M.Y orchestrates (PySCF, ASE, RDKit, AstroPy, BioPython, ClinicalBERT, etc.) are independently available in PyPI without guardrails. A.M.Y's contribution is orchestration, provenance, and refusal, not novel offensive capability.

By using A.M.Y you agree to the terms in USE_POLICY.md. To report a vulnerability in the guard or in the system, see SECURITY.md.

Every generated paper carries a machine-readable watermark identifying it as autonomously generated, with version and SHA-256 fingerprint, so the wider research ecosystem can detect and filter as it sees fit.

## Acknowledgements

A.M.Y stands on the shoulders of an enormous open-source community. None of this would exist without the people who chose to release their work freely. With deep gratitude:

### Scientific computing
- **NumPy, SciPy, pandas, matplotlib** - the foundation of computational science in Python
- **SymPy** - symbolic mathematics (BSD)
- **PySCF** - ab initio quantum chemistry, Hartree-Fock and DFT
- **ASE** (Atomic Simulation Environment) - geometry optimisation and thermochemistry
- **AstroPy** - cosmology, units, constants
- **PyMatGen** - crystal structures and materials properties
- **RDKit** - cheminformatics
- **BioPython** - biological sequence analysis
- **scikit-learn** - classical machine learning
- **Z3** - SMT solving / formal verification

### Machine learning and inference
- **PyTorch** (with MPS / Metal on Apple Silicon)
- **JAX, JAXlib** - Active Inference math
- **ChromaDB** - vector store for semantic memory
- **NetworkX** - the knowledge graph
- **Ollama Cloud** - the LLM backend
- **ClinicalBERT, DNABert2, AlphaFold 3** - domain models surfaced via Atlas

### Engineering and runtime
- **structlog** - structured logging
- **httpx** - async HTTP client
- **pytest, pytest-asyncio** - test infrastructure
- **PyYAML, python-dotenv** - configuration
- **arxiv, feedparser, beautifulsoup4** - literature ingestion
- **rich** - the lovely terminal output

### Scientific and architectural inspiration
- **Karl Friston** - Active Inference and the Free Energy Principle
- **Bernard Baars and Stanislas Dehaene** - Global Workspace Theory
- **Laird, Newell, Rosenbloom** - the SOAR cognitive architecture
- **Pathak et al.** - Intrinsic Curiosity (ICM / RND)
- **Wang et al. (NVIDIA / Caltech)** - the Voyager paradigm
- **Tom Mitchell and the NELL team** - continual learning at scale
- **Sakana AI** - AI Scientist v2; the agentic tree search pattern
- **Google DeepMind** - the Co-Scientist multi-agent design and Elo tournament
- **arXiv:2511.16072 authors** - the science acceleration case studies that informed the flagship paper structure

### License
Apache License 2.0. See LICENSE. The project is dedicated to expanding human knowledge in a transparent, reproducible, and auditable way. Use it well.
