> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="guía-avanzada-de-desarrollo-y-contribución"></a>
# Advanced Development and Contribution Guide

This guide complements `CONTRIBUTING.md` with operational details and recommended practices.

<a id="1-filosofía"></a>
## 1. Philosophy

- Fail-fast on imports (unified script)
- Fast tests first; defer heavy E2E
- Minimum viable observability (logs + metrics if applicable)

<a id="2-flujo-sugerido-diario"></a>
## 2. Suggested Daily Flow

1. Update branch from `main`.
2. Run: `python verify_imports.py --skip-optional`.
3. Run unit tests relevant to the modified module.
4. Implement changes.
5. Run full verification (`python verify_imports.py`).
6. Run security: Bandit + pip-audit.
7. Open PR with a concise summary (what / why / risks).

<a id="3-estructura-de-tests-y-selección-rápida"></a>
## 3. Test Structure and Quick Selection

| Type | Folder | Main use |
|------|---------|---------------|
| Unit | tests/unit | Pure logic, utilities, edge cases |
| Integration | tests/integration | Interaction between services/classes |
| E2E | tests/e2e | Full user/system flow |
| Performance | tests/performance | Specific bottlenecks |
| Fuzz | tests/fuzz | Robustness against unexpected inputs |
| Contract | tests/contract | Stable external interfaces |

<a id="4-estrategia-para-nuevos-servicios"></a>
## 4. Strategy for New Services

1. Create module in `app/services/` with minimal dependency.
2. Add registration in `service_registry` if applicable.
3. Provide base unit test + light integration.
4. Add brief doc in `docs/services/` (if no reusable format exists).

<a id="5-ingestión-de-datos"></a>
## 5. Data Ingestion

- Extend `BaseFetcher`.
- Return `FetchBatch` with normalized items.
- Keep canonical id with `canonical_id`.
- Persist incremental state with `save_state`.

<a id="6-patrones-de-errores-y-logging"></a>
## 6. Error and Logging Patterns

| Situation | Action |
|-----------|--------|
| Recoverable external exception (timeout) | Retry with `retry_call` |
| Internal logical error | Throw clear exception |
| Inconsistent state | Log + safe fallback |

<a id="7-seguridad-y-hardening"></a>
## 7. Security and Hardening

- Do not directly interpolate external input into sensitive logs.
- Watch new dependencies: run `pip-audit` immediately.
- Avoid PII data in traces.

<a id="8-próxima-integración-de-cobertura"></a>
## 8. Next Coverage Integration

`.coveragerc` will be added. Recommended to tag expensive tests with a pytest mark for selective exclusion.

<a id="9-estilo-y-calidad"></a>
## 9. Style and Quality

- Keep functions < ~50 lines where reasonable.
- Extract reusable blocks.
- Document public functions with a brief docstring.

<a id="10-validación-de-importación-masiva"></a>
## 10. Bulk Import Validation

`verify_imports.py` enables early detection of:

- Syntax errors
- Missing dependencies
- Dangerous side-effects

<a id="11-checklists-de-pr-extendido"></a>
## 11. PR Checklists (Extended)

- [ ] Import check (full)
- [ ] New services documented
- [ ] Tests: unit + (integration if applicable)
- [ ] No added vulnerabilities
- [ ] Logs reviewed
- [ ] No secrets

<a id="12-roadmap-técnico-extracto"></a>
## 12. Technical Roadmap (Excerpt)

- Automated coverage
- Homogeneous metrics
- Refactor legacy modules into thematic subpackages

---
End of the extended guide.
