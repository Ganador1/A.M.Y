> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="guía-de-contribución-a-axiom-atlas"></a>
# AXIOM ATLAS Contribution Guide

This guide summarizes the recommended workflow for contributing changes safely, reproducibly, and in line with the project's principles.

<a id="1-entorno"></a>
## 1. Environment

1. Clone the repository.
2. Create a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. (Optional) Install additional dependencies for local tools.

<a id="2-verificaciones-rápidas-antes-de-commits"></a>
## 2. Quick Checks Before Commits

| Check | Command | Purpose |
|--------------|---------|----------|
| Clean imports | `python verify_imports.py --skip-optional` (quick) then without flag | Ensures modules are not broken |
| Key unit tests | `pytest -q tests/unit` | Validate base logic |
| Security (Bandit) | `bandit -q -r app tests` | Detect insecure patterns |
| Dependencies (pip-audit) | `pip-audit -r requirements.audit.txt` | Known vulnerabilities |

<a id="3-estrategia-de-imports"></a>
## 3. Import Strategy

The script `verify_imports.py` now includes:

- Core modules (`app/`)
- Ingestion modules (`ingestion/`)
- Critical root scripts (`main`, `comprehensive_analysis`, `generate_final_report`)

Examples:

```bash
python verify_imports.py --skip-optional  # rápido (solo core)
python verify_imports.py                  # completo
```

<a id="4-tests"></a>
## 4. Tests

Existing classification:

- `tests/unit/` (fast, deterministic)
- `tests/integration/` (cross-component interaction)
- `tests/e2e/` (end-to-end flow)
- `tests/performance/`, `tests/fuzz/`, `tests/contract/`

Rules:

- Prioritize unit tests for new logic.
- Isolate network/IO using mocks.
- Add regression cases when you fix a bug.

<a id="5-estándares-de-código"></a>
## 5. Code Standards

- Progressive typing (use annotations in new code).
- Avoid unnecessary dependencies.
- Robust error handling: do not silence critical exceptions.
- Logging: informative, without sensitive data.

<a id="6-seguridad-y-calidad"></a>
## 6. Security and Quality

- Bandit and pip-audit must be clean before PR.
- Do not introduce keys/secrets in commits.
- Validate external inputs (requests, files).

<a id="7-flujo-de-pull-request"></a>
## 7. Pull Request Flow

1. Create a descriptive branch: `feature/descripcion-corta` or `fix/area-breve`.
2. Run checks (imports, tests, security).
3. Accompany changes with documentation if it alters public behavior.
4. Reference related issues.

<a id="8-cobertura-futuro-cercano"></a>
## 8. Coverage (Near Future)

`coverage.py` configuration will be added. Recommended to prepare tests with clear names and avoid critical logic without tests.

<a id="9-documentación"></a>
## 9. Documentation

- Add or update guides under `docs/guides/`.
- For cross-cutting architecture use `docs/system/`.
- Extensive reports: keep in existing sections.

<a id="10-observabilidad-y-depuración"></a>
## 10. Observability and Debugging

- Enable debug mode via a variable in settings if available.
- Log key events and times in new integrations.

<a id="11-ingestión-de-datos"></a>
## 11. Data Ingestion

- New fetchers must extend `BaseFetcher` and return `FetchBatch`.
- Use utilities from `ingestion.utils` for hashing, cache, and state.

<a id="12-checklist-pre-pr"></a>
## 12. Pre-PR Checklist

- [ ] Core + optional imports OK
- [ ] Unit and relevant tests pass
- [ ] No critical vulnerabilities
- [ ] Documentation updated
- [ ] No secrets / credentials
- [ ] Reasonable logs

---
Thank you for contributing to AXIOM ATLAS! 💡
