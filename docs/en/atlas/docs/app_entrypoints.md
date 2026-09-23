> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="puntos-de-entrada-de-la-api"></a>
# API Entry Points

This document describes the two entrypoints available in the repository and how to use them depending on the scenario. The goal is to facilitate the transition to the refactored modular architecture while preserving compatibility with existing integrations.

<a id="resumen-rápido"></a>
## Quick summary

| File | Status | Recommended use |
| --- | --- | --- |
| `main_refactored.py` | ✅ Main | Active development, deployments, and new integrations |
| `main.py` | 🟡 Legacy | Compatibility with old scripts and specific tests |

<a id="main_refactoredpy-entrypoint-preferido"></a>
## `main_refactored.py` (preferred entrypoint)

- **Architecture**: Modular, with *router registry* and lazy loading.
- **Middleware**: Configured from `configure_middleware` with CORS, TrustedHosts, and centralized logging.
- **Lifecycle**: Uses asynchronous `lifespan` to initialize orchestrators, database, and periodic health checks.
- **Advantages**:
  - 60-80% faster startup.
  - Reduced memory (40-60%).
  - Automatic router registration (more than 100) without manual imports.

<a id="cómo-ejecutarlo"></a>
### How to run it

```bash
uvicorn main_refactored:app --host 0.0.0.0 --port 8002 --reload
```

> Adjust host/port with the variables in the `.env` file or CLI parameters.

<a id="mainpy-modo-legacy"></a>
## `main.py` (legacy mode)

- **Architecture**: Manual router registration with exhaustive import.
- **Compatibility**: Maintains historical route names and dependencies that have not yet migrated to the registry.
- **When to use it**:
  - Validate integrations that still depend on explicit imports.
  - Compare responses between architectures during a progressive migration.

<a id="ejecución"></a>
### Execution

```bash
uvicorn main:app --host 0.0.0.0 --port 8002
```

Enabling `--reload` together with the legacy version in production is not recommended because startup time is longer.

<a id="roadmap-sugerido"></a>
## Suggested roadmap

1. **New features** → Develop and register routers through the *router registry* (see `docs/router_registry.md`).
2. **Smoke tests and CI** → Update scripts to point to `main_refactored:app` by default.
3. **Controlled lag** → Clearly document any dependency that requires `main.py` and plan its migration.
4. **Deprecation** → When all routers are dynamically registered, `main.py` will be removed or converted into an alias of the modern entrypoint.

Keep this document updated whenever the startup process or the status of the entrypoints changes.
