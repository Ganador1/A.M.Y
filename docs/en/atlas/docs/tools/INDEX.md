> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="índice-de-herramientas"></a>
# Tools index

This directory documents the **internal tools** (adapters, tool interfaces), the autonomous system (pipelines/loops), and external tools (scripts, packages in `external_tools/`).

<a id="secciones"></a>
## Sections
- Tool adapters (unified interface): `docs/tools/TOOL_ADAPTERS.md`
- Autonomous system (pipelines/loops): `docs/tools/AUTONOMOUS_PIPELINES.md`
- Scripts and utilities: `docs/tools/SCRIPTS_AND_UTILS.md`
- Vendored external tools: `docs/tools/EXTERNAL_TOOLS.md`

<a id="convención-recomendada"></a>
## Recommended convention
- If a file in `scripts/` is "operational" (it runs in CI/prod or as a workflow), document it here.
- If a file in `scripts/analysis/` is an ad-hoc report, classify it as "historical" and do not mix it with guides.
