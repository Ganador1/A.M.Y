> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="dominio-astronomy"></a>
# Domain: Astronomy

<a id="qué-es"></a>
## What it is
Domain oriented toward astronomical analysis: light curves, astrometry, stellar variability, exoplanet detection, and integrated pipelines.

<a id="ubicación-en-el-código"></a>
## Location in the code
- Package: `app/domains/astronomy/`
- Consolidated router: `app/domains/astronomy/routers/api.py` (declares `prefix="/astronomy"`)
- Services: `app/domains/astronomy/services/`

<a id="servicios-principales-clasesarchivos"></a>
## Main services (classes/files)
- `LightkurveAdvancedService`: `app/domains/astronomy/services/lightkurve_advanced_service.py`
- `AstropyPrecisionService`: `app/domains/astronomy/services/astropy_precision_service.py`
- `StellarVariabilityService`: `app/domains/astronomy/services/stellar_variability_service.py`
- `OptimalAperturePhotometryService`: `app/domains/astronomy/services/optimal_aperture_photometry_service.py`
- `BinarySystemAnalysisService`: `app/domains/astronomy/services/binary_system_analysis_service.py`
- `ExoplanetTransitAnalysisService`: `app/domains/astronomy/services/exoplanet_transit_analysis_service.py`
- `AstronomicalMLService`: `app/domains/astronomy/services/astronomical_ml_service.py`
- Orchestration/pipeline pieces: `integrated_astronomy_pipeline.py`, `orchestrator.py`, `advanced_astronomy_workflow.py`

<a id="api-router-consolidado"></a>
## API (consolidated router)
The domain router exposes endpoints under the `prefix` declared in `api.py`. Examples (see the file for the complete list):
- `GET /astronomy/` → domain info
- `GET /astronomy/services` → capabilities
- `POST /astronomy/analyze-telescope-data`
- `POST /astronomy/run-simulation`

<a id="pruebas"></a>
## Tests
- Recommended: create/use `tests/astronomy/` (if it exists) or unit tests per service.

<a id="referencias-cercanas-al-código"></a>
## References close to the code
- `app/domains/astronomy/README.md`
- `app/domains/astronomy/API_GUIDE.md`
- `app/domains/astronomy/SERVICES.md`
- `app/domains/astronomy/EXAMPLES.md`
