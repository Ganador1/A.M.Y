# Guía de curación de documentación (anti-ruido)

## Problema
En este repo hay tres “tipos” de documentos mezclados:
1) Documentación estable (cómo usar/operar el sistema)
2) Especificaciones técnicas (interfaces, arquitectura)
3) Reportes históricos (ejecuciones, fases, análisis, resultados)

Cuando se mezclan en el mismo nivel (p.ej. raíz de `docs/`), la documentación se vuelve difícil de navegar.

## Convención recomendada

### 1) Docs estables
Mantener en:
- `docs/api/` → referencia y overview de API
- `docs/domains/` → documentación canónica por dominio
- `docs/services/` → documentación por servicio transversal
- `docs/tools/` → adapters, pipelines y herramientas
- `docs/guides/` → guías prácticas

### 2) Especificaciones
Mantener en:
- `docs/system/`
- `docs/architecture.md`, `docs/configuration.md`, `docs/router_registry.md`

### 3) Reportes / análisis históricos
Mover (o al menos “catalogar”) en:
- `docs/reports/` (ideal)
- `docs/analysis/` (si aplica)

Regla: si un documento tiene nombre tipo `ANALISIS_*`, `PHASE*`, `REPORT_*`, fechas o resultados puntuales, tratarlo como **reporte**, no como guía.

## Qué hacer con los archivos actuales “ruido”
Opción segura (sin romper nada):
- No borrar.
- Crear un índice `docs/reports/INDEX.md` y referenciar ahí los reportes de raíz.

Opción mejor (con cambios de rutas):
- Crear carpeta `docs/reports/archive/`.
- Mover los `.md` de “resultados/análisis” desde `docs/` raíz a `docs/reports/archive/`.

## Siguiente paso recomendado
Hecho en esta curación:
- Se creó `docs/reports/INDEX.md`.
- Se movieron reportes/análisis desde la raíz de `docs/` a `docs/reports/archive/`.
- Se añadió referencia explícita en `docs/INDEX.md`.
