> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="router-registry-de-axiom-atlas"></a>
# Router Registry of AXIOM ATLAS

The *router registry* automates the loading of more than 100 FastAPI routers grouped by domain. This guide explains how to analyze, regenerate, and validate `app/routers/router_registry.py` without breaking compatibility with the legacy architecture.

<a id="1-componentes-principales"></a>
## 1. Main components

| Element | Location | Description |
| --- | --- | --- |
| Generated file | `app/routers/router_registry.py` | Central table of routers with prefixes and tags. |
| Utility script | `scripts/utils/router_registry.py` | Tools to analyze and regenerate the file. |
| Optional config | `config/router_registry.json` | Persistence of custom configurations. |

<a id="2-comandos-disponibles"></a>
## 2. Available commands

Go to the root of the repo and run:

```bash
cd .
python scripts/utils/router_registry.py --analyze   # Detecta routers actuales en main.py
python scripts/utils/router_registry.py --create    # Genera router_registry.py desde templates
python scripts/utils/router_registry.py --migrate   # Migra routers legacy al sistema modular
```

> The header of `router_registry.py` keeps an abbreviated reminder (`python router_registry.py --create`). This guide adds the full path of the script.

<a id="3-flujo-recomendado-para-agregar-un-router"></a>
## 3. Recommended flow for adding a router

1. **Create the router** in `app/routers/nombre.py` exporting `router = APIRouter(...)`.
2. **Update templates or JSON** (optional): add metadata in `config/router_registry.json` if you want to document dependencies.
3. **Regenerate the registry**:

   ```bash
   python scripts/utils/router_registry.py --create
   ```

4. **Review diffs**: confirm that the corresponding block appears in `router_registry.py` with the correct prefix.
5. **Run tests**: run smoke tests or import checks to ensure that the router loads (`pytest tests/smoke/test_advanced_modules.py -q`, for example).

<a id="4-validación-y-compatibilidad"></a>
## 4. Validation and compatibility

- `main_refactored.py` attempts to register routers through `register_routers(app, router_config)`.
- If automatic registration fails (ImportError, missing module), `register_legacy_routers` runs as a fallback.
- Keep the generated file under version control: any manual edit will be overwritten when the script is run again.

<a id="5-buenas-prácticas"></a>
## 5. Best practices

- **Atomicity**: after running `--create`, commit the changes to the generated file together with the new routers.
- **Dependency review**: the script can flag missing dependencies; install them or document the requirements.
- **Documentation**: link new routers in `docs/ROUTERS_INDEX.md` to keep the documentation centralized.
- **CI/CD**: consider adding a job that runs `python scripts/utils/router_registry.py --analyze` to detect unregistered routers.

Keep this document up to date when routes, scripts, or registry conventions are modified.
