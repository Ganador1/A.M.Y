# Dominio: Astronomy

## Qué es
Dominio orientado a análisis astronómico: curvas de luz, astrometría, variabilidad estelar, detección de exoplanetas y pipelines integrados.

## Ubicación en el código
- Paquete: `app/domains/astronomy/`
- Router consolidado: `app/domains/astronomy/routers/api.py` (declara `prefix="/astronomy"`)
- Servicios: `app/domains/astronomy/services/`

## Servicios principales (clases/archivos)
- `LightkurveAdvancedService`: `app/domains/astronomy/services/lightkurve_advanced_service.py`
- `AstropyPrecisionService`: `app/domains/astronomy/services/astropy_precision_service.py`
- `StellarVariabilityService`: `app/domains/astronomy/services/stellar_variability_service.py`
- `OptimalAperturePhotometryService`: `app/domains/astronomy/services/optimal_aperture_photometry_service.py`
- `BinarySystemAnalysisService`: `app/domains/astronomy/services/binary_system_analysis_service.py`
- `ExoplanetTransitAnalysisService`: `app/domains/astronomy/services/exoplanet_transit_analysis_service.py`
- `AstronomicalMLService`: `app/domains/astronomy/services/astronomical_ml_service.py`
- Piezas de orquestación/pipeline: `integrated_astronomy_pipeline.py`, `orchestrator.py`, `advanced_astronomy_workflow.py`

## API (router consolidado)
El router del dominio expone endpoints bajo el `prefix` declarado en `api.py`. Ejemplos (ver el archivo para el listado completo):
- `GET /astronomy/` → info del dominio
- `GET /astronomy/services` → capacidades
- `POST /astronomy/analyze-telescope-data`
- `POST /astronomy/run-simulation`

## Pruebas
- Recomendado: crear/usar `tests/astronomy/` (si existe) o pruebas unitarias por servicio.

## Referencias cercanas al código
- `app/domains/astronomy/README.md`
- `app/domains/astronomy/API_GUIDE.md`
- `app/domains/astronomy/SERVICES.md`
- `app/domains/astronomy/EXAMPLES.md`
