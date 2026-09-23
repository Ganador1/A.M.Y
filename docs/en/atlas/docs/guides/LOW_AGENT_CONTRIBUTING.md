> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="guía-de-contribución---agente-low"></a>
# Contribution Guide - Low Agent

Status: experimental

<a id="alcance-del-rol"></a>
## Role Scope

The Low agent focuses on:

- Base CI/CD and extensions.
- Structural documentation and operational governance.
- Manifest validation and operational reproducibility (scripts, checks).
- Publication integrity (signatures, hashes, Merkle) – later phases.

<a id="flujo-de-trabajo"></a>
## Workflow

1. Create branch: `feature/low-<descripcion-corta>`.
2. Open early PR (draft) with checklist.
3. Ensure green CI (lint, tests, security, build, manifest validation).
4. Update progress section in `raodmap gpt5midhigh.md`.
5. Request 1 technical reviewer + 1 documentation reviewer if applicable.

<a id="checklist-pr-copiar-en-descripción"></a>
## PR Checklist (copy into description)

- [ ] Title with Conventional Commit.
- [ ] Green CI (attach run or badge).
- [ ] No critical bandit / pip-audit findings.
- [ ] Updated documentation (`docs/INDEX.md` if status/file changes).
- [ ] Validated manifest(s) (if applicable) – attach report excerpt.
- [ ] Changelog (if there is a user-visible change).

<a id="estándares-de-código-scripts"></a>
## Code Standards (Scripts)

- Python 3.11+.
- Strict typing where reasonable (`from __future__ import annotations`).
- Avoid unnecessary dependencies; prefer stdlib.
- CLI outputs in JSON for easy integration.

<a id="validación-de-manifests"></a>
## Manifest Validation

Run locally:

```bash
python scripts/validate_manifests.py --models-dir models --schema models/manifest.schema.json --output reports/manifest_validation_report.json
```

If there is no schema yet: warnings are accepted, not errors.

<a id="política-de-documentación"></a>
## Documentation Policy

- Each new document: add to `docs/INDEX.md` with initial status `experimental`.
- Change to `stable` after two iterations without structural modifications.
- Mark `deprecated` and keep for 1 release before deleting.

<a id="errores-comunes-a-evitar"></a>
## Common Mistakes to Avoid

| Situation | Corrective Action |
|-----------|-------------------|
| Large PR (>400 loc) | Split into smaller logical PRs |
| Lack of roadmap update | Add progress in Low Agent Progress section |
| Silent failure in scripts | Return code !=0 and JSON with `errors` |
| Modify core logic without coordination | Open proposal issue first |

<a id="métricas-de-calidad-internas"></a>
## Internal Quality Metrics

- Target average review time: < 24h.
- % PRs with complete checklist: > 95%.
- Scripts without critical partial typing (mypy errors) in advanced phases.

<a id="próximos-incrementos-del-rol"></a>
## Next Role Increments

- Integration of manifest validation as a dedicated job in CI.
- Mandatory gate for manifests once schema stabilizes.
- Signature scripts (Ed25519) and Merkle verification.

(Update this document when responsibilities change or new gates are added.)
