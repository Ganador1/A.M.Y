# Getting started with A.M.Y

**A.M.Y — Autonomous Mind Yield** is an experimental research agent. Given a mission, it cycles through reasoning, tool use, memory and review to decide what to investigate next. **AMY** coordinates the work; **Atlas** supplies scientific tools. The [main README](README.md) explains the architecture, agent roles and research scope.

This guide covers the public **1.1.0rc1** source branch. You can start by checking the included results offline, or configure a model and scientific tools for a new mission.

**Version 1.1.0rc1 — release candidate.**

## Get the public source

```bash
git clone --branch main https://github.com/Ganador1/A.M.Y.git
cd A.M.Y
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python amy.py --help
```

Python 3.13+ is required for the runtime. The source includes Atlas, but its scientific dependencies need separate setup. Follow [ENVIRONMENT.md](ENVIRONMENT.md) for the worker environment. The wheel alone is not the full laboratory.

## Verify results without a model

```bash
python release_evidence/autocorrelation/verify.py
python -m pip install -r release_evidence/runtime/requirements.txt
python release_evidence/runtime/verify.py
```

The first command checks an exact mathematical witness. The second rechecks recorded numerical measurements. Neither requires a cloud key. Read the [reproduction guide](docs/REPRODUCIBILITY.md) for expected results and the scope of each verifier.

## Configure a mission

```bash
cp .env.example .env
cp config.release.yaml config.local.yaml
```

Add your own provider credentials to `.env`. Edit `config.local.yaml` to select available models, a bounded research question and appropriate resource limits. The public `config.yaml` matches the portable `config.release.yaml`; both use CPU settings and disable automatic mission chaining.

For generated-code experiments, start Docker and build the isolation image:

```bash
docker build -t amy-sandbox:latest sandbox/
python amy.py --config config.local.yaml --goal "Your bounded research question"
```

Stop the interactive run with Ctrl-C. Disabling mission chaining does not impose a time budget. For unattended model comparisons, use the bounded calibration launcher described in the [reproduction guide](docs/REPRODUCIBILITY.md), beginning with a small worker subset.

## Inspect the work

Follow the paths in your configuration or campaign output directory to inspect decisions, receipts, scientific outputs, memory and reports. Keep failed experiments when evaluating a run. A valid tool execution and a convincing summary do not by themselves establish a new scientific finding.

Read the [results catalog](docs/RESULTS.md) for the included research, the [evidence guide](docs/EVIDENCE.md) for provenance limits, and the [tool guide](ATLAS_TOOL_GUIDE.md) for scientific capabilities and their dependencies.

## Develop and contribute

```bash
python -m pip install -r scripts/release/requirements-validation.txt
python -m pytest tests -m "not network" -q
```

See the [contribution guide](CONTRIBUTING.md), [changelog](CHANGELOG.md), [migration guide](docs/MIGRATION.md), [security policy](SECURITY.md) and [use policy](USE_POLICY.md).

Apache-2.0; see [LICENSE](LICENSE). Maintainer: **Ganador1**.
