# A.M.Y

A.M.Y is an experimental agent for planning research, running scientific tools, retaining evidence, and producing reviewable reports. Version **1.1.0rc1** is a release candidate.

## Start here

```bash
git clone --branch codex/public-release-1.1.0rc1 https://github.com/Ganador1/A.M.Y.git
cd A.M.Y
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
cp .env.example .env
python amy.py --help
```

Configure provider credentials locally. Follow [environment setup](ENVIRONMENT.md) for the separate Atlas worker and scientific libraries. The wheel alone does not install Atlas. Copy `config.release.yaml` for a new mission; the working `config.yaml` is an existing operator profile.

## What you can evaluate

AMY runs a perceive–attend–think–act–learn loop. It can call scientific tools, retain successful and failed experiments, and compare certain reported quantities with computational certificates. Tool coverage is discovered at runtime and depends on installed dependencies; registered tools are not all independently validated.

The latest bounded evaluation exercised five cloud models over 20 sessions and checked 51 measurements. Earlier failures remain in the results. This is evidence about these protocols, not a promise of unrestricted autonomy or scientific discovery.

The autocorrelation witness is a mathematical publication candidate. Reproductions, local exclusions, and engineering changes have different publication categories. See the [results catalog](docs/publication/RESULTS_CATALOG.md).

## Review and contribute

Read the [main documentation](README.md), [release notes](docs/releases/1.1.0rc1.md), [science principles](SCIENCE_MANIFESTO.md), [tool guide](ATLAS_TOOL_GUIDE.md), [contribution guide](CONTRIBUTING.md), [security policy](SECURITY.md), and [use policy](USE_POLICY.md).

Code is licensed under Apache-2.0; see [LICENSE](LICENSE). Author: Ganador1. Repository: https://github.com/Ganador1/A.M.Y
