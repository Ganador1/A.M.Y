# AXIOM Atlas — AMY scientific laboratory

Atlas provides scientific tool implementations and a separate web application. In the AMY source tree, the cognitive runtime accesses its tool registry through a subprocess worker. The maintained AMY release documentation is [one directory above](../README.md).

## Worker setup

From the repository root:

```bash
python3.13 -m venv atlas/.venv_new
atlas/.venv_new/bin/python -m pip install -r atlas/requirements.txt
```

Dependency availability differs across scientific tools and platforms. Tool registration is not proof of numerical correctness. Query the tool descriptor, inspect the evidence grade, and run the relevant checks before interpreting a result.

For a separately installed AMY runtime, set `AMY_ATLAS_ROOT` to this directory and `AMY_ATLAS_PYTHON` to the scientific environment's interpreter. See [environment layout](../ENVIRONMENT.md) and [tool integration](../ATLAS_TOOL_GUIDE.md).

## Optional service application

Atlas also contains the `main_refactored.py` service entry point, web assets, database migrations, configuration examples, scripts and tests. From the `atlas/` directory, run `python -m uvicorn main_refactored:app --host 127.0.0.1 --port 8000` after installing the required dependencies and configuring the services you need. See the [technical reference library](../docs/ENGLISH_MANUALS.md) for domain and service references.

## Optional assets and infrastructure

The source preserves the training and evaluation scripts under `scripts/data_processing/` and `scripts/tools/`, together with `models/manifest.schema.json`. Historical fitted models (`.pkl` and `.joblib`), training datasets, caches and local registries are not distributed as runtime assets. A workflow that requires one of these models needs an operator-supplied artifact or a new training run with the appropriate data and dependencies. The presence of the training code does not reproduce the historical fitted model or its reported metrics.

Small examples include the synthetic time series in `test_data/` and the water geometry in `data/water_simple.pdb`. These are fixtures, not new research findings. Library-shadowing test stubs are excluded; scientific integrations require the actual optional libraries.

Database migration source is retained in `alembic/`, with supporting scripts in `scripts/database/` and `scripts/tools/`. Review the target database and back up existing data before applying a migration. The service image uses `main_refactored:app`; its build context is this `atlas/` directory. From the repository root, its build command is `docker build -f atlas/Dockerfile -t amy-atlas:local atlas/`.

The optional Compose example is `config/docker-compose.yml`. Supply your own `POSTGRES_PASSWORD`, `SECRET_KEY` and `GF_SECURITY_ADMIN_PASSWORD`; the additional services example also requires `NEO4J_PASSWORD`. From the repository root, `docker compose --env-file atlas/.env -f atlas/config/docker-compose.yml config` validates the resolved Compose configuration without starting services. Treat its output as sensitive because it includes resolved credentials. Bind paths resolve relative to the Compose file. The examples use local service defaults and require deployment-specific network, authentication and dependency review.

Container builds, database upgrades, external providers and the complete optional service stack have **not** been validated by the release's offline checks. The legacy integration image in `config/Dockerfile` runs `tests/integration/test_meta4_real_data.py`; that script's own score is not a release acceptance test. Tests under `tests/` include optional, network and infrastructure cases and are separate from the focused AMY release suite.

## Evidence and publication

H₂ numerical checks, SSH finite-chain certificates and population-model certificates have explicit, different verification scopes. Reproduced papers and internal review scores are not original discoveries or external peer review. Consult the [results catalog](../docs/RESULTS.md) and [provenance limits](../docs/EVIDENCE.md).

Source license: [Apache-2.0](LICENSE). Preserve third-party attribution. Keep local credentials, generated experiment state and service caches out of release archives.
