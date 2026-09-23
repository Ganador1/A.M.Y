# A.M.Y

A.M.Y (Autonomous Mind Yield) is an experimental research agent that connects a cognitive loop to scientific tools, retains execution evidence, and checks selected claims against computational certificates.

**Version: 1.1.0rc1 — release candidate, not yet published.**

[Release notes](docs/releases/1.1.0rc1.md) · [Getting started](README_PUBLIC.md) · [Repository map](docs/PROJECT_MAP.md) · [Research results](docs/publication/RESULTS_CATALOG.md) · [Evidence limits](docs/publication/PROVENANCE.md) · [Contributing](CONTRIBUTING.md)

## What changed

- Persistent experiment receipts make earlier checked results available to later decisions and reflections.
- Decision parsing distinguishes executable responses from examples, rejects incomplete or ambiguous output, and records how JSON was selected.
- Session closure checks known experiment IDs and, in the calibrated laboratories, explicit numerical assessments. Successful execution is not scientific success.
- Bounded recovery and per-run provenance help diagnose failed calls, exhausted goals, and interrupted sessions.
- Numerical and exact certificate tools cover selected H₂, SSH and population-model calculations. Each verifier has a stated scope.
- A comparison across five cloud models exercised 20 native sessions in four versioned batches: 51 verified measurements, 14 quantitative closures, and six retained unsuccessful sessions. The final parser batch completed 4/4 GLM sessions; the clarified H₂ contract completed 2/2 further sessions. These are small calibration studies, not a model leaderboard.

## Install from source

Python 3.13+ and macOS or Linux are supported development targets. Scientific dependencies vary by tool. Start with a source checkout; the Python wheel contains the AMY runtime, not the separate Atlas laboratory or every optional scientific dependency.

```bash
git clone --branch codex/public-release-1.1.0rc1 https://github.com/Ganador1/A.M.Y.git
cd A.M.Y
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
cp .env.example .env
python amy.py --help
```

Add your provider credentials to the local `.env`. Configure Atlas separately as described in [ENVIRONMENT.md](ENVIRONMENT.md). Generated-code experiments use the configured sandbox; building its Docker image requires `docker build -t amy-sandbox:latest sandbox/`.

For a new mission, copy `config.release.yaml`, choose the tools and model available to you, and set resource limits before starting:

```bash
cp config.release.yaml config.local.yaml
python amy.py --config config.local.yaml --goal "Your bounded research question"
```

`continuous_mission: false` prevents automatically replacing a completed mission, but is not a wall-clock budget. Use a bounded campaign launcher for unattended evaluations. Stop the CLI with Ctrl-C. The working `config.yaml` is an operator profile; it enables continuous missions and has machine-specific settings. See [migration guidance](docs/releases/MIGRATION_1_1.md).

## Architecture

`perceive → attend → think → act → learn → reflect`

AMY coordinates reasoning, goals, episodic and semantic memory, tool execution, and reporting. Atlas supplies scientific tools through a subprocess interface. Capability names and domain coverage do not imply that every tool is experimentally validated: some paths are heuristic, tabulated, approximate, unavailable without optional libraries, or explicitly rejected as mock output. Query the live tool descriptor and inspect its evidence grade.

The architecture draws inspiration from cognitive theories; it does not demonstrate consciousness, general intelligence, or neural self-training. See [research foundations](RESEARCH.md) and the [tool guide](ATLAS_TOOL_GUIDE.md).

## Research status

The strongest mathematical publication candidate is an exact rational witness for the minimum-autocorrelation functional, with a lower bound above 0.40863826. The release evidence package checks the finite witness; worldwide priority, global optimality, and wholly autonomous discovery are not established. Public baseline attribution and the distinction between operator algorithms and agent choices are retained.

Other work includes local negative combinatorial results, reproductions, solver diagnostics, and engineering improvements. They are classified individually in the [results catalog](docs/publication/RESULTS_CATALOG.md). Neither manuscript generation nor an internal score constitutes external peer review. AMY does not claim to have solved a Millennium Prize Problem.

## Verify before relying on a result

```bash
python release_evidence/autocorrelation/verify.py
python -m pytest tests/test_public_release_hygiene.py tests/test_decision_schema.py tests/test_decision_envelope.py -q
```

Hashes establish consistency of retained bytes under the verifier's assumptions. They do not establish scientific truth, provider identity, trusted time, or instrumentation coverage. Exact mathematical checking, numerical consistency, operational completion, and external attestation are separate claims. Historical outputs are retained research records, not automatically approved publications.

## Documentation and use

- [Science principles](SCIENCE_MANIFESTO.md)
- [Release checklist](RELEASE_CHECKLIST.md)
- [Publication plan](docs/publication/PUBLICATION_PLAN.md)
- [Security reporting](SECURITY.md) and [use policy](USE_POLICY.md)
- [Changelog](CHANGELOG.md) and [citation metadata](CITATION.cff)

Apache-2.0; see [LICENSE](LICENSE). Third-party materials retain their own licenses and attribution. Maintainer: Ganador1.

## Release resources

- [English technical manuals](docs/ENGLISH_MANUALS.md)
- [Reproduction guide](docs/releases/REPRODUCING.md)
