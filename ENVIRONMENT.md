# Environment setup

AMY supports Python 3.13+ on its macOS and Linux development targets. Install the runtime first, then add the scientific dependencies needed by your experiment. Atlas runs in a separate subprocess and can use a different Python environment from AMY.

## AMY runtime

Run these commands from the repository root:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
cp .env.example .env
python amy.py --help
```

Set your provider credentials in the local `.env` and choose an available model in your configuration. The repository's `config.release.yaml` is a portable starting profile; copy it to `config.local.yaml` for your own settings. Keep credentials and local state out of source control.

```bash
cp config.release.yaml config.local.yaml
python amy.py --config config.local.yaml --goal "Your bounded research question"
```

Provider calls require your account and quota. Review the model, enabled tools and resource limits before starting a mission. See the [main guide](README.md) for the research loop and configuration overview.

## Atlas scientific worker

The Python wheel installs the AMY runtime. Atlas source is supplied in the source checkout, and its scientific libraries must be installed separately. A separate environment lets you select a Python version supported by the libraries you need; Python 3.13 is a useful starting point when newer Python versions lack compatible scientific wheels.

For the worker's base environment, run from the repository root:

```bash
python3.13 -m venv atlas/.venv_new
atlas/.venv_new/bin/python -m pip install -e . -r atlas/requirements-core.txt
atlas/.venv_new/bin/python -m pip install numpy scipy sympy
```

Install additional packages for the selected tools. For example, molecular electronic-structure tools may require PySCF. The files `atlas/requirements-scientific.txt`, `atlas/requirements-bio.txt`, `atlas/requirements-quantum.txt` and `atlas/requirements-ml.txt` group larger optional stacks; `atlas/requirements.txt` combines them. These stacks can require native libraries, substantial downloads or platform-specific setup. Installing every stack is unnecessary for a bounded experiment.

AMY defaults to the adjacent `atlas/` directory and `atlas/.venv_new/bin/python3`. To use another location or interpreter, export both variables **before starting AMY**:

```bash
export AMY_ATLAS_ROOT="$(pwd)/atlas"
export AMY_ATLAS_PYTHON="$AMY_ATLAS_ROOT/.venv_new/bin/python"
```

`AMY_ATLAS_ROOT` must contain `run_agent_with_tools.py` and `app/`. `AMY_ATLAS_PYTHON` must point to an executable interpreter with the required dependencies. AMY passes the selected laboratory root to its worker; no Atlas web server is needed for this subprocess interface.

You can inspect the worker's available tools without starting a research mission:

```bash
"$AMY_ATLAS_PYTHON" core/atlas_worker.py <<'JSON'
{"id": 1, "action": "describe_tools"}
JSON
```

The response describes registered tools and their input formats. Registration alone does not establish that an optional backend is installed or that a tool's output is suitable scientific evidence. Exercise the specific tool and inspect its result and evidence limits. This guide covers the AMY worker connection; deployment of the complete standalone Atlas web application requires separate integration work.

## Generated-code sandbox

The portable profile requires Docker isolation for generated code. With Docker installed and running, build the included image:

```bash
docker build -t amy-sandbox:latest sandbox/
```

The Atlas subprocess is a separate Python process, not the generated-code Docker sandbox. Configure each execution path according to the experiment's needs.

## Check the installation

The public source includes configuration and subprocess regression tests:

```bash
python -m pytest tests/test_cli_config.py tests/test_installed_atlas_worker.py -q
```

The worker test uses a temporary minimal laboratory to verify that a separate Atlas root is honored. It does not validate every scientific backend. Use the [reproducibility guide](docs/REPRODUCIBILITY.md) for the packaged numerical and mathematical examples, and [evidence documentation](docs/EVIDENCE.md) for what their checks establish.
