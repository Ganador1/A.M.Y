# Scripts y utilidades

## Objetivo
Catalogar scripts “operacionales” vs scripts “de análisis/reporte” para reducir ruido.

## Ubicación
- `scripts/` contiene:
  - automatizaciones de ejecución
  - tests de integración/real data
  - análisis y auditorías
  - herramientas de mantenimiento

## Reglas prácticas (sugeridas)
- Operacional: scripts bajo `scripts/tools/`, `scripts/qa/`, `scripts/security/`, `scripts/maintenance/`.
- Análisis ad-hoc: scripts bajo `scripts/analysis/`.

## Scripts destacados (por nombre)
- Validación de entorno: `scripts/validate_environment.sh`
- Verificación dependencias: `scripts/verify_dependencies.py`
- Auditoría docstrings: `scripts/audit_docstrings.py`
- Navegación de dominios: `scripts/domain_navigator.py`

## Siguiente paso
Puedo generar un catálogo navegable “por intención” (run / validate / audit / benchmark) recorriendo `scripts/` y clasificándolos.
