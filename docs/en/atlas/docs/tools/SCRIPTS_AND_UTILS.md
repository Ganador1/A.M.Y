> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="scripts-y-utilidades"></a>
# Scripts and utilities

<a id="objetivo"></a>
## Objective
Catalog "operational" scripts vs "analysis/report" scripts to reduce noise.

<a id="ubicación"></a>
## Location
- `scripts/` contains:
  - execution automations
  - integration/real data tests
  - analysis and audits
  - maintenance tools

<a id="reglas-prácticas-sugeridas"></a>
## Practical rules (suggested)
- Operational: scripts under `scripts/tools/`, `scripts/qa/`, `scripts/security/`, `scripts/maintenance/`.
- Ad-hoc analysis: scripts under `scripts/analysis/`.

<a id="scripts-destacados-por-nombre"></a>
## Featured scripts (by name)
- Environment validation: `scripts/validate_environment.sh`
- Dependency verification: `scripts/verify_dependencies.py`
- Docstring audit: `scripts/audit_docstrings.py`
- Domain navigation: `scripts/domain_navigator.py`

<a id="siguiente-paso"></a>
## Next step
I can generate a navigable catalog "by intention" (run / validate / audit / benchmark) by traversing `scripts/` and classifying them.
