# A.M.Y — Autonomous Mind Yield

A.M.Y is an experimental, open-source research agent that turns a research question into a continuing cycle of reasoning, scientific computation, memory and review. You give it a mission and access to tools; it chooses actions, runs experiments, compares results and uses the retained evidence to decide what to try next.

The project combines **AMY**, the cognitive runtime, with **Atlas**, its scientific laboratory. Its purpose is to make computational research easier to inspect and reproduce: a proposed explanation, a successful tool call and a verified result remain distinct throughout the workflow.

**Version 1.1.0rc1 (release candidate) · Python 3.13+ · Apache-2.0 · Maintainer: Ganador1**

[Quick start](README_PUBLIC.md) · [Tool guide](ATLAS_TOOL_GUIDE.md) · [Reproducibility](docs/REPRODUCIBILITY.md) · [Research results](docs/RESULTS.md) · [Changelog](CHANGELOG.md) · [Contributing](CONTRIBUTING.md)

## What you can do with AMY

- Give an agent a bounded research question, let it decompose the question into subgoals, and inspect its decisions and tool results.
- Run scientific calculations through Atlas, or use a dedicated laboratory with a fixed experimental protocol.
- Retain successful and failed experiments, retrieve earlier measurements and continue a mission with persistent memory.
- Compare hypotheses, reflect on recurring mistakes and generate reports or manuscript drafts linked to computational evidence.
- Run independent workers across models or tasks, with explicit budgets and separate outputs.
- Recheck the supplied exact mathematical witness and recorded numerical calculations without a cloud model.

These capabilities support research and evaluation. They do not make a model's interpretation correct, establish novelty or replace independent scientific review.

## How the cognitive cycle works

AMY runs a heartbeat implemented in [`core/heartbeat.py`](core/heartbeat.py). Each cycle moves through five phases; reflection runs periodically rather than after every action.

| Phase | What happens |
|---|---|
| **Perceive** | Read the current goals, time and internal surprise and curiosity signals. Literature searches and other external observations enter through the available actions and sensors. |
| **Attend** | Select a focus from goal, curiosity and memory candidates using the global workspace. |
| **Think** | Ask the configured model to choose a structured action using the mission, pending subgoals, tool descriptions, prior experiment receipts and review feedback. |
| **Act** | Execute the selected action: search, calculate, run an isolated code experiment, manage a subgoal, create a skill or produce a report. Parse and execution failures remain observable outcomes. |
| **Learn** | Record the cycle, retain new claims with their cited experiment IDs, update exploration priorities and account for goal attempts. A successful execution does not by itself complete a scientific goal. |

Periodic **reflection** reviews progress and receipts, consolidates memory and can feed recurring review weaknesses back into later reasoning. The loop then continues until its configured stopping condition, budget or operator interruption.

The architecture draws on ideas from SOAR, Global Workspace Theory, Active Inference, curiosity-driven exploration and reusable skill libraries. These are engineering inspirations: attention, curiosity and belief updates include explicit heuristics. The project does not demonstrate consciousness or implement on-device neural self-training. See [research foundations](RESEARCH.md).

## Memory and learning

AMY keeps several kinds of state because an experiment result and a model's recollection of it serve different purposes:

| Component | Role |
|---|---|
| **Episodic memory** | A persistent JSONL record of experiences, with a bounded in-memory history restored across restarts. |
| **Semantic memory** | A knowledge graph and claim store. Model assertions retain their source and experiment references; repeating an assertion is not independent confirmation. |
| **Procedural memory and skills** | Stored code and descriptions that can be retrieved for later tasks. Consolidation can extract reusable procedures from successful recorded experiments. |
| **Experiment receipts** | Structured access to previous tool executions, including identifiers, outcomes and evidence used in subsequent decisions and reflections. |
| **Review feedback** | Recurring weaknesses from prior reviews that can influence later prompts and hypothesis refinement. |

The public configuration separates memory by mission. Optional embedding-based retrieval can augment keyword matching; its usefulness depends on the embedding provider and installed dependencies. Memory is not unlimited context, and a retained claim still needs an appropriate verifier.

## AMY and Atlas

**AMY coordinates the investigation.** Its runtime contains goals, reasoning, memory, action dispatch, evidence recording and reporting. **Atlas performs scientific work.** It exposes domain tools and services through a separate Python worker, allowing scientific dependencies to be managed separately from the cognitive runtime.

Examples of the available tool families include:

| Area | Examples |
|---|---|
| Mathematics and statistics | Symbolic calculation, numerical analysis, hypothesis tests and selected exact or solver-backed checks. |
| Physics and astronomy | Physical-model calculations, spectra, cosmology, units and astronomical constants. |
| Chemistry and materials | Quantum-chemistry calculations, molecular analysis, structure and materials workflows. |
| Biology and related domains | Sequence analysis and specialized data-processing services. |

Availability varies with the installed libraries, external services and toolchain. Atlas contains both scientific-library integrations and heuristic, tabulated or demonstration paths. A registered tool name or domain label is not a validation certificate. Use the [tool guide](ATLAS_TOOL_GUIDE.md), inspect the live descriptor and check the evidence grade and limitations of the tool you select.

The wheel installs the AMY runtime. A source checkout also contains Atlas and the reproducibility packages; it does not automatically install every optional scientific dependency. See [environment setup](ENVIRONMENT.md).

## Agent roles and unattended campaigns

AMY has several cooperating roles within its research workflow. The **ranking agent** compares hypotheses through an Elo tournament. The **reflection agent** checks manuscript structure and selected grounding requirements. **Meta-review** summarizes recurring weaknesses, while **evolution** can propose refinements. Some paths are deterministic; model-based judging and refinement are optional. Internal review scores describe those checks, not external peer review.

Dedicated campaign launchers can also run multiple AMY sessions in parallel. The included calibration harness pairs five configured model choices with two laboratories, for up to ten workers. Each worker has its own mission, memory, protocol and results. A prepared plan freezes relevant source and configuration hashes; the launcher checks that plan before execution and enforces cycle, call and runtime limits.

Concurrency is a resource setting, not a guarantee that every provider account supports ten simultaneous requests. The general public profile starts with two concurrent model calls. The calibration harness configures its workers separately. Start with a small subset and follow the [reproduction guide](docs/REPRODUCIBILITY.md) before launching a full campaign.

## Install and run

Python 3.13+ is required for the AMY runtime. macOS and Linux are the development targets. Start from the main branch:

```bash
git clone --branch main https://github.com/Ganador1/A.M.Y.git
cd A.M.Y
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
cp .env.example .env
python amy.py --help
```

Put your own provider credentials in the local `.env`. Choose models available to your account and install the scientific dependencies required by your chosen tools. Atlas uses a separate worker environment; [ENVIRONMENT.md](ENVIRONMENT.md) explains its setup.

In this distribution, `config.yaml` and `config.release.yaml` both provide the portable CPU profile. Copy it before customization:

```bash
cp config.release.yaml config.local.yaml
# Edit the mission, model choices, tools and resource limits in config.local.yaml.
python amy.py --config config.local.yaml --goal "Your bounded research question"
```

The profile sets `continuous_mission: false`, so AMY does not automatically replace an ended mission with another. This setting is not a wall-clock budget; use a bounded campaign for unattended evaluation. Stop an interactive run with Ctrl-C.

Generated experiment code requires the configured Docker isolation. With Docker running, build its image before using that action:

```bash
docker build -t amy-sandbox:latest sandbox/
```

The public profile refuses to fall back to a host subprocess when the required isolation is unavailable. The supplied offline numerical verifiers do not require Docker. Existing installations should also read the [migration guide](docs/MIGRATION.md).

## Outputs and evidence

Depending on the selected workflow, AMY writes experiment inputs and outputs, native receipts, execution events, source and configuration records, memory, reports and manuscript drafts. Default paths are declared in the configuration; campaign workers use their own output directories. These generated records are local working data and can contain prompts, provider responses and user-supplied information.

Execution evidence uses hashes and retained artifacts to make changes detectable within the recorded chain. Scientific verifiers answer narrower questions: an exact checker can establish a finite mathematical bound, while a numerical checker can test consistency under stated inputs and tolerances. Hashes alone do not establish scientific truth, provider identity, trusted time or complete instrumentation coverage. See [evidence and provenance](docs/EVIDENCE.md).

## Reproduce the included results offline

The exact autocorrelation witness uses the Python standard library:

```bash
python release_evidence/autocorrelation/verify.py
```

The recorded numerical calibration requires NumPy and checks 23 AR1 replays, 28 H₂ certificates and one retained invalid request:

```bash
python -m pip install -r release_evidence/runtime/requirements.txt
python release_evidence/runtime/verify.py
```

Neither command calls a cloud model. These packages contain selected public inputs, results and verifiers, with explicit limits on what they reproduce. They do not include private model conversations or the complete historical search. For a fresh native model run and the full instructions, see [reproducibility](docs/REPRODUCIBILITY.md).

To run the public regression suite, install its optional validation dependencies first:

```bash
python -m pip install -r scripts/release/requirements-validation.txt
python -m pytest tests -m "not network" -q
```

## Research status

The included autocorrelation witness certifies **C ≥ 0.40863826** for the stated minimum-autocorrelation functional. It is a mathematical publication candidate with an exact finite verifier. Worldwide priority, global optimality and wholly autonomous invention are not established by this package; algorithm contributions and agent choices have separate attribution.

Other retained work includes numerical reproductions, local negative results, solver diagnostics and engineering improvements. Their status is recorded in the [results catalog](docs/RESULTS.md). AMY does not claim to have solved a Millennium Prize Problem. Generated manuscripts and internal scores are research artifacts awaiting appropriate review.

Version 1.1.0rc1 strengthens decision parsing, persistent receipts, bounded recovery, source tracking and quantitative session checks. See the [changelog](CHANGELOG.md) for software changes, rather than interpreting every runtime improvement as a scientific discovery.

## Documentation, contribution and credits

- [Repository map](docs/PROJECT_MAP.md) and [English technical manuals](docs/ENGLISH_MANUALS.md)
- [Scientific principles](SCIENCE_MANIFESTO.md) and [research foundations](RESEARCH.md)
- [Contributing](CONTRIBUTING.md), [security reporting](SECURITY.md) and [use policy](USE_POLICY.md)
- [Citation metadata](CITATION.cff)

AMY builds on open-source scientific computing and software infrastructure, including NumPy, SciPy, SymPy, NetworkX, PySCF, ASE, AstroPy, RDKit, BioPython, Z3 and their wider ecosystems. Which packages are used depends on the installed tools. Their authors retain their own credits and licenses.

AMY is licensed under [Apache-2.0](LICENSE). Maintainer: **Ganador1**.
