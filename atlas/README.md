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

## Web application

The modular web entry point is `main_refactored.py`; it requires the Atlas service configuration and optional dependencies. From this directory, a configured development environment can run:

```bash
.venv_new/bin/python -m uvicorn main_refactored:app --host 127.0.0.1 --port 8000
```

Starting the web application is not required for every AMY subprocess tool workflow. Older web and domain documentation under `docs/` and `app/domains/` is historical and may remain in Spanish; it has not all been revalidated for the AMY 1.1 candidate.

## Evidence and publication

H₂ numerical checks, SSH finite-chain certificates and population-model certificates have explicit, different verification scopes. Reproduced papers and internal review scores are not original discoveries or external peer review. Consult the [results catalog](../docs/publication/RESULTS_CATALOG.md) and [provenance limits](../docs/publication/PROVENANCE.md).

Source license: [Apache-2.0](LICENSE). Preserve third-party attribution. Keep local credentials, generated experiment state and service caches out of release archives.
