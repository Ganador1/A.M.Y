# Astronomy: catálogo de servicios

Este dominio tiene una colección amplia de servicios. Los más relevantes están en:

- `app/domains/astronomy/services/lightkurve_advanced_service.py`
- `app/domains/astronomy/services/astrometric_analysis_service.py`
- `app/domains/astronomy/services/stellar_variability_service.py`
- `app/domains/astronomy/services/optimal_aperture_photometry_service.py`
- `app/domains/astronomy/services/exoplanet_transit_analysis_service.py`
- `app/domains/astronomy/services/multiwavelength_analysis_service.py`
- `app/domains/astronomy/services/astronomical_ml_service.py`

## Orquestación
- `app/domains/astronomy/services/integrated_astronomy_pipeline.py`
- `app/domains/astronomy/services/orchestrator.py`
- `app/domains/astronomy/services/advanced_astronomy_workflow.py`

## Recomendación de uso
- Para API: usar el router consolidado `app/domains/astronomy/routers/api.py`.
- Para invocación directa desde Python: importar servicios individuales o la fachada `app/domains/astronomy/services/astronomy_service`.
