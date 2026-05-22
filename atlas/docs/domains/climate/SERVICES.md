# Climate: catálogo de servicios

## `ClimateEvidenceService`
- Archivo: `app/domains/climate/services/climate_evidence_service.py`
- Responsabilidad típica:
  - Cargar dataset (GISTEMP)
  - Calcular estadísticas y puntajes de evidencia
  - Devolver resultados estandarizados

## Recomendación
- Para validaciones y reproducibilidad: fijar rutas de dataset en config/entorno.
