# A.M.Y Science Manifesto
## Real Science, Real Reproducibility, Real Discovery

> *"A.M.Y does not generate toy science. It generates science you can verify, reproduce, and build on."*

---

## 1. Fundamental principles

### 1.1 Falsification before confirmation
A.M.Y follows Karl Popper's principle: **a hypothesis is scientific only if it is falsifiable.**

- Before accepting any finding, A.M.Y actively searches for contradicting evidence.
- It uses `literature_search` with queries like *"limitations of X"*, *"failure of Y"*, *"X side effects"*.
- A finding with no falsification attempt is not considered valid.

### 1.2 Real evidence, never fabricated
Any numerical claim in an A.M.Y paper must come from:

| Source | Requirement |
|---|---|
| Own experiment | Include `experiment_id` in the paper |
| Real dataset | Include URL / dataset name |
| Verified paper | Include citation with real DOI |

**A.M.Y never invents numbers.** If it lacks evidence, it writes *"further evidence needed"*.

### 1.3 Reproducibility by design
Every A.M.Y experiment is reproducible:

```python
# Each experiment record contains:
{
  "experiment_id": "<unique_hash>",
  "tool": {
    "name": "...",
    "input": "...",
    "output_hash": "<sha256>",
    "output_length": 1234,
    "success": true
  },
  "output_preview": "...",         # First 2000 chars
  "timestamp": "ISO8601",
  "domain": "...",
  "environment": {...}             # Python version, platform, hostname
}
```

The full output is stored alongside in `data/experiments/<id>/output.txt`; the SHA-256 in `provenance.json` is the hash of that file.

### 1.4 Verification with real tools
A.M.Y does not rely on the LLM alone. It verifies with:

- **SymPy** — exact symbolic computation
- **NumPy / SciPy** — reproducible numerical analysis
- **PySCF** — ab initio quantum chemistry (Hartree-Fock, DFT)
- **ASE** — atomistic simulation (geometry optimisation, thermochemistry)
- **AstroPy** — cosmology, units, constants
- **PyMatGen** — crystal structures and properties
- **RDKit** — cheminformatics
- **BioPython** — biological sequences
- **ClinicalBERT** — clinical text NER
- **Atlas ToolUniverse** — 94 validated scientific tools across 23 domains
- **Z3 / Lean prover** — formal verification

---

## 2. Scientific research cycle

```
┌─────────────────────────────────────────────────────────────┐
│                  A.M.Y SCIENTIFIC CYCLE                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. OBSERVE    →  What do we know? What is missing?         │
│       ↓                                                     │
│  2. HYPOTHESIS →  Specific and FALSIFIABLE claim            │
│       ↓                                                     │
│  3. FALSIFY    →  Search for evidence AGAINST the claim     │
│       ↓                                                     │
│  4. EXPERIMENT →  Executable code + recorded results        │
│       ↓                                                     │
│  5. RANK       →  Elo tournament across candidates          │
│       ↓                                                     │
│  6. REFLECT    →  Self-review against 6-check rubric        │
│       ↓                                                     │
│  7. VERIFY     →  Real tool runs with provenance            │
│       ↓                                                     │
│  8. PIVOT      →  Next open question                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.1 Anti-loop rules
A.M.Y has strict rules against repetition:

- If the last 3+ actions were `peer_review_paper` on similar topics → switch to `decompose_goal` or `experiment`.
- If the last 5+ actions were `research` → synthesise via `think_more` or `experiment`.
- If a hypothesis has already been validated → do not repeat. Pivot to the next question.

### 2.2 Curiosity mandate
After every validated finding, A.M.Y asks itself:

> *"What is the most surprising implication of this finding?"*

And it pursues *that*. Science advances through unexpected connections, not incremental repetition.

---

## 3. Validation with Atlas

A.M.Y integrates with **AXIOM Atlas**, a platform of 94 validated scientific tools across 23 domains.

### 3.1 Validated tools per domain

| Domain | Tools (excerpts) |
|---|---|
| Mathematics (20) | `sympy_solve_equation`, `prime_gap_analysis`, `number_theory_advanced`, `z3_prover`, `automated_prover`, `graph_theory`, `topology_invariants` |
| Physics (12) | `quantum_energy_levels`, `quantum_circuit`, `calculus_engine`, `astropy_constants`, `astropy_blackbody` |
| Chemistry (18) | `molecular_weight_calc`, `bond_energy_analyzer`, `pyscf_hf_energy`, `pyscf_dft_energy`, `ase_optimize`, `ase_thermochemistry` |
| Biology (7) | `dna_analyzer`, `protein_properties`, `sequence_analyzer`, `service_dnabert2genomicsservice` |
| Medicine (4) | `service_clinicalbertservice`, `service_alphafold3proteinstructureservice` |
| Statistics (5) | `numpy_statistics`, `numpy_correlation`, `hypothesis_tester` |
| Astronomy (4) | `astropy_cosmology`, `astropy_blackbody`, `service_astronomicalmlservice` |
| Neuroscience (2) | `service_neurosciencelightservice` (EEG band powers) |
| Materials (3) | `gnome_materials`, `pymatgen_structure` |
| Engineering (3) | `service_additivemanufacturingservice`, `service_synthesisequipmentservice` |
| Research / meta (3) | `literature_search`, `validate_hypothesis`, `literature_verify_hypothesis_plus` |
| Evidence corroboration (15) | `evidence_corroborate_<domain>` for biology, chemistry, physics, climate, drug discovery, plasma physics, quantum computing, etc. |

### 3.2 Validation process

```text
1. Generate candidate hypotheses (PaperEnhancer)
2. Rank by Elo tournament (Ranking Agent — heuristic or LLM judge)
3. Execute real scientific tools (Atlas worker)
4. Compose Markdown + PDF with SHA-256 provenance
5. Self-review via Reflection Agent (6-check rubric)
6. Annotate the draft with action items
```

---

## 4. Technical reproducibility

### 4.1 Isolated environment
Experiments run in a **sandbox** with:
- Configurable timeout (default 300 s)
- Memory limit (default 2048 MB)
- Optional `--network=none`
- Pre-execution syntax validation

### 4.2 Dependency versioning
```
requirements.txt                  # A.M.Y core, pinned
atlas/requirements*.txt           # Atlas scientific stack
pyproject.toml                    # Install metadata + entry points
```

### 4.3 Random seeds
Every stochastic experiment uses `np.random.seed(42)` by default.

### 4.4 Provenance integrity
Every tool invocation generates a `provenance.json` record with SHA-256 of the full output. The rubric scorer recomputes the hash and rejects manuscripts whose claimed provenance does not match.

---

## 5. Ethics and safety

### 5.1 Safety kernel
A.M.Y has an integrated misuse guard ([`atlas/app/security/misuse_guard.py`](atlas/app/security/misuse_guard.py)) that:
- Blocks research that would enable biological / chemical weapons.
- Blocks research that targets surveillance of identified individuals.
- Requires human review for experiments on humans.
- Fails closed when the policy engine is unavailable.

### 5.2 Data integrity
- SHA-256 hashes for every experiment output.
- Decision audit logs persisted by the kernel.
- Full provenance chain from tool input to paper claim.

---

## 6. Quality metrics

A.M.Y tracks the following metrics on every paper:

| Metric | Target |
|---|---|
| Falsification attempts | >30 % of hypotheses |
| Reproducibility | 100 % of experiments reproducible bit-for-bit |
| Real citations | >80 % of citations resolve to real publications |
| Peer-review score | ≥7 / 10 for publishable papers |
| Reflection score | ≥70 / 100 to pass the advisory gate |
| Novelty | No repetition of already-validated hypotheses |

The **Rubric Scorer** ([`experiments/ab_test/scoring/score_paper.py`](experiments/ab_test/scoring/score_paper.py)) is deterministic and runs without any LLM, so any reviewer can verify the same scores independently.

---

## 7. Contributing science with A.M.Y

### 7.1 For researchers
1. Define a scientific mission in `config.yaml`.
2. A.M.Y investigates autonomously.
3. Review the papers in `papers/`.
4. Verify the experiments in `data/experiments/`.
5. Publish the validated findings.

### 7.2 For developers
1. Add scientific tools to [`atlas/app/extended_science_tools.py`](atlas/app/extended_science_tools.py).
2. Register them in `DynamicToolRegistry` (`register_extended_tools`).
3. Write tests in `tests/`.
4. Document in `ATLAS_TOOL_GUIDE.md`.

### 7.3 For reviewers
1. Run the regression tests: `.venv/bin/python -m pytest tests/test_atlas_misuse_guard.py tests/test_security_guardrails.py tests/test_science_gates.py`.
2. Run the rubric on any paper: `.venv/bin/python experiments/ab_test/scoring/score_paper.py papers/`.
3. Inspect `data/experiments/<id>/provenance.json` to verify SHA-256 against `output.txt`.
4. Verify citations against real sources.

---

## 8. Scientific references

A.M.Y is inspired by cognitive architectures and autonomous research systems:

| Pillar | Source | Role in A.M.Y |
|---|---|---|
| Active Inference | Karl Friston (Free Energy Principle) | Central engine: continuous perception–action |
| Global Workspace Theory | Bernard Baars / Stanislas Dehaene | Attention bus and broadcast |
| SOAR | Laird, Newell, Rosenbloom | Operative cycle: propose → evaluate → execute |
| Curiosity-Driven Learning | Pathak et al. (ICM / RND) | Intrinsic motivation |
| Voyager | Wang et al. 2023 (NVIDIA / Caltech) | Skill library + automatic curriculum |
| NELL | Tom Mitchell et al. (CMU) | 24 / 7 continual learning |
| ResearchAgent | Baek et al. 2024 | Iterative idea generation |
| Autotelic Agents | Colas, Oudeyer et al. | Autonomous goal generation |
| Sakana AI Scientist v2 | arXiv:2504.08066 | End-to-end paper generation |
| Google AI Co-Scientist | DeepMind 2025 | Multi-agent Reflection + Elo Ranking |
| OpenAI GPT-5 Science | arXiv:2511.16072 | Human–AI collaboration patterns |

---

## 9. License and use

A.M.Y is released under the Apache License 2.0:
- ✅ Academic and research use.
- ✅ Commercial use with attribution.
- ✅ Modification and distribution.
- ❌ Use for weapons or mass surveillance.
- ❌ Claiming A.M.Y discoveries as one's own without attribution.

---

*A.M.Y — Autonomous Mind Yield*
*A mind that never sleeps, dedicated to expanding human knowledge.*
