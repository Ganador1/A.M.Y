> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="guía-de-curación-de-documentación-anti-ruido"></a>
# Documentation curation guide (anti-noise)

<a id="problema"></a>
## Problem
In this repo there are three "types" of documents mixed together:
1) Stable documentation (how to use/operate the system)
2) Technical specifications (interfaces, architecture)
3) Historical reports (executions, phases, analyses, results)

When they are mixed at the same level (e.g. root of `docs/`), the documentation becomes difficult to navigate.

<a id="convención-recomendada"></a>
## Recommended convention

<a id="1-docs-estables"></a>
### 1) Stable docs
Keep in:
- `docs/api/` → API reference and overview
- `docs/domains/` → canonical documentation by domain
- `docs/services/` → documentation by cross-cutting service
- `docs/tools/` → adapters, pipelines and tools
- `docs/guides/` → practical guides

<a id="2-especificaciones"></a>
### 2) Specifications
Keep in:
- `docs/system/`
- `docs/architecture.md`, `docs/configuration.md`, `docs/router_registry.md`

<a id="3-reportes--análisis-históricos"></a>
### 3) Reports / historical analyses
Move (or at least "catalog") into:
- `docs/reports/` (ideal)
- `docs/analysis/` (if applicable)

Rule: if a document has a name like `ANALISIS_*`, `PHASE*`, `REPORT_*`, dates or specific results, treat it as a **report**, not as a guide.

<a id="qué-hacer-con-los-archivos-actuales-ruido"></a>
## What to do with the current "noise" files
Safe option (without breaking anything):
- Do not delete.
- Create an `docs/reports/INDEX.md` index and reference the root reports there.

Better option (with path changes):
- Create folder `docs/reports/archive/`.
- Move the `.md` of "results/analysis" from `docs/` root to `docs/reports/archive/`.

<a id="siguiente-paso-recomendado"></a>
## Recommended next step
Done in this curation:
- `docs/reports/INDEX.md` was created.
- Reports/analyses were moved from the root of `docs/` to `docs/reports/archive/`.
- An explicit reference was added in `docs/INDEX.md`.
