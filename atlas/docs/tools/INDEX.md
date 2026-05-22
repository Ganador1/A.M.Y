# Índice de herramientas

Este directorio documenta las **herramientas internas** (adapters, tool interfaces), el sistema autónomo (pipelines/loops) y herramientas externas (scripts, paquetes en `external_tools/`).

## Secciones
- Tool adapters (interfaz unificada): `docs/tools/TOOL_ADAPTERS.md`
- Sistema autónomo (pipelines/loops): `docs/tools/AUTONOMOUS_PIPELINES.md`
- Scripts y utilidades: `docs/tools/SCRIPTS_AND_UTILS.md`
- External tools vendorizadas: `docs/tools/EXTERNAL_TOOLS.md`

## Convención recomendada
- Si un archivo en `scripts/` es “operacional” (se corre en CI/prod o como workflow), documentarlo aquí.
- Si un archivo en `scripts/analysis/` es un reporte ad-hoc, clasificarlo como “histórico” y no mezclarlo con guías.
