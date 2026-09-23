> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="-guía-completa-del-sistema-axiom---análisis-astronómico-avanzado"></a>
# 🚀 Complete Guide to the AXIOM System - Advanced Astronomical Analysis

<a id="-índice"></a>
## 📋 Table of Contents
1. [Introduction to the AXIOM System](#introducción)
2. [Installation and Configuration](#instalación)
3. [System Architecture](#arquitectura)
4. [Quick Start Guide](#inicio-rápido)
5. [Available Services](#servicios)
6. [Integrated Pipeline](#pipeline)
7. [Advanced Workflows](#workflows)
8. [Data Connectors](#conectores)
9. [Practical Use Cases](#casos-de-uso)
10. [APIs and Databases](#apis)
11. [Best Practices](#mejores-prácticas)
12. [Troubleshooting](#troubleshooting)

---

<a id="-introducción-al-sistema-axiom-introducción"></a>
## 🌟 Introduction to the AXIOM System {#introducción}

The AXIOM System (Advanced eXploration and Investigation for Observational Mathematics) is a complete astronomical analysis platform that integrates:

- **12 specialized services** organized into 4 phases
- **Unified pipeline** for end-to-end analysis
- **Automated workflows** for common use cases
- **Native connectors** to astronomical APIs and databases
- **Machine Learning** integrated for classification and detection
- **Parallel processing** for large datasets

<a id="-características-principales"></a>
### ✨ Main Features

- 🔬 **Multidimensional Analysis**: Photometry, astrometry, spectroscopy
- 🤖 **Integrated AI**: Automatic classification of astronomical objects
- 🚀 **Scalability**: From individual objects to complete surveys
- 🌐 **Connectivity**: SIMBAD, VizieR, Gaia, TESS, Kepler, ESA Archives
- 📊 **Visualization**: Interactive graphics and automatic reports
- ⚡ **Performance**: Parallel processing and advanced optimizations

---

<a id="-instalación-y-configuración-instalación"></a>
## 💻 Installation and Configuration {#instalación}

<a id="requisitos-del-sistema"></a>
### System Requirements

```bash
<a id="python-38"></a>
# Python 3.8+
python --version

<a id="dependencias-principales"></a>
# Dependencias principales
pip install numpy scipy matplotlib astropy lightkurve
pip install scikit-learn pandas astroquery requests
pip install concurrent.futures typing pathlib
```

<a id="configuración-básica"></a>
### Basic Configuration

```python
import os
from pathlib import Path

<a id="configurar-directorio-de-trabajo"></a>
# Configurar directorio de trabajo
AXIOM_BASE_DIR = Path("./axiom_analysis")
AXIOM_BASE_DIR.mkdir(exist_ok=True)

<a id="configurar-variables-de-entorno-opcional"></a>
# Configurar variables de entorno (opcional)
os.environ['AXIOM_CACHE_DIR'] = str(AXIOM_BASE_DIR / "cache")
os.environ['AXIOM_OUTPUT_DIR'] = str(AXIOM_BASE_DIR / "outputs")
```

---

<a id="-arquitectura-del-sistema-arquitectura"></a>
## 🏗️ System Architecture {#arquitectura}

<a id="estructura-por-fases"></a>
### Structure by Phases

```
AXIOM System Architecture
├── FASE 1: FUNDACIÓN
│   ├── LightkurveAdvancedService      # Análisis de curvas de luz
│   ├── AstropyPrecisionService        # Cálculos astronómicos precisos
│   └── StellarVariabilityService      # Detección de variabilidad
│
├── FASE 2: EXPANSIÓN
│   ├── OptimalAperturePhotometryService  # Fotometría optimizada
│   ├── BinarySystemAnalysisService       # Análisis de binarias
│   ├── ExoplanetTransitAnalysisService   # Detección de tránsitos
│   ├── AdvancedStatisticsService         # Estadísticas avanzadas
│   └── MultiWavelengthAnalysisService    # Análisis multibanda
│
├── FASE 3: MACHINE LEARNING
│   ├── AstrometricAnalysisService     # Análisis astrométrico
│   └── AstronomicalMLService          # Clasificación ML
│
└── FASE 4: INTEGRACIÓN
    ├── IntegratedAstronomyPipeline    # Pipeline unificado
    └── AdvancedAstronomyWorkflow      # Workflows automatizados
```

---

<a id="-guía-de-inicio-rápido-inicio-rápido"></a>
## 🚦 Quick Start Guide {#inicio-rápido}

<a id="ejemplo-básico"></a>
### Basic Example

```python
<a id="1-importar-servicios-principales"></a>
# 1. Importar servicios principales
from app.domains.astronomy.services import (
    IntegratedAstronomyPipeline,
    AdvancedAstronomyWorkflow
)

<a id="2-inicializar-el-pipeline"></a>
# 2. Inicializar el pipeline
pipeline = IntegratedAstronomyPipeline("./outputs")

<a id="3-análisis-básico-de-un-objeto"></a>
# 3. Análisis básico de un objeto
result = await pipeline.analyze_object(
    object_id="HD 209458",
    coordinates=(330.79, 18.88),
    analysis_mode="standard_analysis"
)

<a id="4-ver-resultados"></a>
# 4. Ver resultados
print(f"Calidad del análisis: {result.overall_quality}")
print(f"Servicios ejecutados: {len(result.service_results)}")
```

<a id="workflow-automatizado"></a>
### Automated Workflow

```python
<a id="1-inicializar-sistema-de-workflows"></a>
# 1. Inicializar sistema de workflows
workflow_system = AdvancedAstronomyWorkflow()

<a id="2-crear-workflow-para-búsqueda-de-exoplanetas"></a>
# 2. Crear workflow para búsqueda de exoplanetas
objects = ["TIC 307210830", "TIC 441420236", "TIC 308538095"]
execution_id = workflow_system.create_workflow_execution(
    "exoplanet_search_v1",
    objects,
    priority=Priority.HIGH
)

<a id="3-ejecutar-workflow"></a>
# 3. Ejecutar workflow
report = workflow_system.execute_workflow(execution_id)

<a id="4-revisar-resultados"></a>
# 4. Revisar resultados
print(f"Objetos procesados: {report.total_objects}")
print(f"Hallazgos científicos: {len(report.scientific_findings)}")
```

---

<a id="-servicios-disponibles-servicios"></a>
## 🔧 Available Services {#servicios}

<a id="fase-1-servicios-de-fundación"></a>
### PHASE 1: Foundation Services

<a id="lightkurveadvancedservice"></a>
#### LightkurveAdvancedService
**Purpose**: Advanced analysis of light curves

```python
from app.domains.astronomy.services import LightkurveAdvancedService

service = LightkurveAdvancedService()

<a id="análisis-básico"></a>
# Análisis básico
result = service.analyze_lightcurve(
    target="Kepler-442",
    mission="Kepler",
    remove_outliers=True,
    detrend=True
)

<a id="características-avanzadas"></a>
# Características avanzadas
advanced_result = service.advanced_periodogram_analysis(
    result.lightcurve,
    method="lombscargle",
    confidence_levels=[0.99, 0.999]
)
```

<a id="astropyprecisionservice"></a>
#### AstropyPrecisionService
**Purpose**: High-precision astronomical calculations

```python
from app.domains.astronomy.services import AstropyPrecisionService

service = AstropyPrecisionService()

<a id="conversiones-de-coordenadas"></a>
# Conversiones de coordenadas
coords = service.convert_coordinates(
    ra=83.82, dec=-5.39,
    from_frame="icrs",
    to_frame="galactic"
)

<a id="cálculos-de-distancia"></a>
# Cálculos de distancia
distance = service.calculate_distance_modulus(
    apparent_mag=8.5,
    absolute_mag=4.8
)
```

<a id="stellarvariabilityservice"></a>
#### StellarVariabilityService
**Purpose**: Detection and analysis of stellar variability

```python
from app.domains.astronomy.services import StellarVariabilityService

service = StellarVariabilityService()

<a id="detectar-variabilidad"></a>
# Detectar variabilidad
variability = service.detect_variability(
    lightcurve_data,
    methods=["amplitude", "period", "chi_squared"]
)

<a id="clasificar-tipo-de-variable"></a>
# Clasificar tipo de variable
classification = service.classify_variable_type(
    lightcurve_data,
    period=variability.best_period
)
```

<a id="fase-2-servicios-de-expansión"></a>
### PHASE 2: Expansion Services

<a id="optimalaperturephotometryservice"></a>
#### OptimalAperturePhotometryService
**Purpose**: Photometry with optimized aperture

```python
from app.domains.astronomy.services import OptimalAperturePhotometryService

service = OptimalAperturePhotometryService()

<a id="optimizar-apertura"></a>
# Optimizar apertura
optimal_aperture = service.optimize_aperture(
    target_pixel_file,
    optimization_method="snr_based",
    background_method="median"
)

<a id="fotometría-de-precisión"></a>
# Fotometría de precisión
photometry = service.precision_photometry(
    target_pixel_file,
    aperture=optimal_aperture,
    quality_flags=True
)
```

<a id="exoplanettransitanalysisservice"></a>
#### ExoplanetTransitAnalysisService
**Purpose**: Detection and analysis of exoplanet transits

```python
from app.domains.astronomy.services import ExoplanetTransitAnalysisService

service = ExoplanetTransitAnalysisService()

<a id="búsqueda-de-tránsitos"></a>
# Búsqueda de tránsitos
transits = service.search_transits(
    lightcurve,
    period_range=(0.5, 50),
    duration_range=(0.1, 12),
    snr_threshold=7.0
)

<a id="caracterizar-planeta"></a>
# Caracterizar planeta
planet = service.characterize_planet(
    lightcurve,
    transit_params=transits.best_fit,
    stellar_params={"mass": 1.1, "radius": 1.05}
)
```

<a id="fase-3-machine-learning"></a>
### PHASE 3: Machine Learning

<a id="astronomicalmlservice"></a>
#### AstronomicalMLService
**Purpose**: Automatic classification with AI

```python
from app.domains.astronomy.services import AstronomicalMLService

service = AstronomicalMLService()

<a id="clasificar-objeto-astronómico"></a>
# Clasificar objeto astronómico
classification = service.classify_object(
    features=extracted_features,
    classifier_type="stellar_classification",
    confidence_threshold=0.8
)

<a id="detectar-anomalías"></a>
# Detectar anomalías
anomalies = service.detect_anomalies(
    lightcurve_data,
    method="isolation_forest",
    contamination=0.1
)
```

---

<a id="-pipeline-integrado-pipeline"></a>
## 🔄 Integrated Pipeline {#pipeline}

<a id="configuraciones-de-análisis"></a>
### Analysis Configurations

```python
from app.domains.astronomy.services.integrated_astronomy_pipeline import (
    AnalysisConfiguration, AnalysisMode, DataType
)

<a id="configuración-rápida"></a>
# Configuración rápida
quick_config = AnalysisConfiguration(
    analysis_mode=AnalysisMode.QUICK_SCAN,
    data_types=[DataType.PHOTOMETRY],
    quality_threshold=0.6,
    enable_parallel=True
)

<a id="configuración-completa"></a>
# Configuración completa
comprehensive_config = AnalysisConfiguration(
    analysis_mode=AnalysisMode.COMPREHENSIVE_ANALYSIS,
    data_types=[DataType.PHOTOMETRY, DataType.ASTROMETRY, DataType.SPECTROSCOPY],
    quality_threshold=0.8,
    enable_parallel=True,
    max_execution_time=3600,
    generate_plots=True,
    save_intermediate_results=True
)
```

<a id="análisis-de-objetos-múltiples"></a>
### Analysis of Multiple Objects

```python
<a id="lista-de-objetos-a-analizar"></a>
# Lista de objetos a analizar
targets = [
    {"id": "HD 189733", "coords": (300.18, 22.71)},
    {"id": "WASP-12", "coords": (97.64, 29.67)},
    {"id": "Kepler-442b", "coords": (297.84, 41.91)}
]

<a id="procesamiento-paralelo"></a>
# Procesamiento paralelo
results = []
for target in targets:
    result = await pipeline.analyze_object(
        object_id=target["id"],
        coordinates=target["coords"],
        configuration=comprehensive_config
    )
    results.append(result)

<a id="generar-reporte-consolidado"></a>
# Generar reporte consolidado
consolidated_report = pipeline.generate_consolidated_report(results)
```

---

<a id="-workflows-avanzados-workflows"></a>
## ⚙️ Advanced Workflows {#workflows}

<a id="workflows-predefinidos"></a>
### Predefined Workflows

<a id="1-stellar-survey-analysis"></a>
#### 1. Stellar Survey Analysis
```python
<a id="workflow-para-survey-estelar-completo"></a>
# Workflow para survey estelar completo
stellar_objects = [f"Gaia_DR3_{i}" for i in range(1000, 1100)]

execution_id = workflow_system.create_workflow_execution(
    "stellar_survey_v1",
    stellar_objects,
    priority=Priority.NORMAL,
    batch_config=BatchConfiguration(
        batch_size=20,
        max_concurrent_batches=4,
        auto_scaling=True
    )
)
```

<a id="2-exoplanet-discovery-pipeline"></a>
#### 2. Exoplanet Discovery Pipeline
```python
<a id="búsqueda-sistemática-de-exoplanetas"></a>
# Búsqueda sistemática de exoplanetas
candidate_stars = load_kepler_targets("main_sequence", magnitude_limit=12)

execution_id = workflow_system.create_workflow_execution(
    "exoplanet_search_v1",
    candidate_stars,
    priority=Priority.HIGH,
    custom_parameters={
        "transit_detection": {
            "snr_threshold": 7.0,
            "period_range": [0.5, 365],
            "depth_threshold": 0.001
        }
    }
)
```

<a id="3-variable-star-monitoring"></a>
#### 3. Variable Star Monitoring
```python
<a id="monitoreo-continuo-de-estrellas-variables"></a>
# Monitoreo continuo de estrellas variables
variable_targets = ["RR_Lyrae_sample", "Cepheid_sample", "Eclipsing_binaries"]

monitoring_execution = workflow_system.create_workflow_execution(
    "variable_monitoring_v1",
    variable_targets,
    priority=Priority.URGENT,
    custom_parameters={
        "monitoring_duration": 365,  # días
        "cadence": "daily",
        "alert_threshold": 0.1  # magnitudes
    }
)
```

<a id="workflows-personalizados"></a>
### Custom Workflows

```python
from app.domains.astronomy.services.advanced_astronomy_workflow import WorkflowStep

<a id="crear-workflow-personalizado"></a>
# Crear workflow personalizado
custom_steps = [
    WorkflowStep(
        step_id="data_quality",
        service_name="astropy_precision",
        parameters={"quality_check": True}
    ),
    WorkflowStep(
        step_id="photometry",
        service_name="optimal_aperture",
        dependencies=["data_quality"],
        parameters={"precision_mode": True}
    ),
    WorkflowStep(
        step_id="analysis",
        service_name="stellar_variability",
        dependencies=["photometry"],
        parameters={"deep_analysis": True}
    )
]

<a id="registrar-template-personalizado"></a>
# Registrar template personalizado
custom_template = WorkflowTemplate(
    template_id="my_custom_analysis",
    name="Análisis Personalizado",
    description="Mi workflow específico",
    workflow_type=WorkflowType.CUSTOM_WORKFLOW,
    steps=custom_steps
)
```

---

<a id="-conectores-de-datos-conectores"></a>
## 🌐 Data Connectors {#conectores}

<a id="configuración-de-apis"></a>
### API Configuration

```python
import os

<a id="configurar-claves-de-api-opcional-para-servicios-públicos"></a>
# Configurar claves de API (opcional para servicios públicos)
os.environ['ESA_API_KEY'] = 'your_esa_api_key'
os.environ['NASA_API_KEY'] = 'your_nasa_api_key'

<a id="urls-de-servicios"></a>
# URLs de servicios
ASTRONOMICAL_APIS = {
    'simbad': 'https://simbad.u-strasbg.fr/simbad/sim-tap',
    'vizier': 'https://vizier.u-strasbg.fr/viz-bin/votable',
    'esa_archive': 'https://archives.esac.esa.int',
    'nasa_exoplanetarchive': 'https://exoplanetarchive.ipac.caltech.edu/TAP',
    'gaia_archive': 'https://gea.esac.esa.int/tap-server/tap'
}
```

<a id="uso-de-conectores"></a>
### Using Connectors

```python
from app.connectors.astronomical_data_connector import AstronomicalDataConnector

<a id="inicializar-conector"></a>
# Inicializar conector
connector = AstronomicalDataConnector()

<a id="buscar-en-simbad"></a>
# Buscar en SIMBAD
simbad_data = connector.query_simbad(
    object_name="HD 209458",
    radius="5 arcmin",
    fields=["main_id", "coordinates", "mag_V", "spec_type"]
)

<a id="obtener-datos-de-gaia"></a>
# Obtener datos de Gaia
gaia_data = connector.query_gaia(
    coordinates=(330.79, 18.88),
    radius=0.01,  # grados
    data_release="DR3"
)

<a id="datos-de-tess"></a>
# Datos de TESS
tess_data = connector.get_tess_lightcurve(
    tic_id="441420236",
    sectors="all",
    quality_mask=True
)
```

---

<a id="-casos-de-uso-prácticos-casos-de-uso"></a>
## 📊 Practical Use Cases {#casos-de-uso}

<a id="caso-1-caracterización-de-exoplanetas"></a>
### Case 1: Exoplanet Characterization

```python
async def characterize_exoplanet_system(target_name):
    """Análisis completo de un sistema exoplanetario."""
    
    # 1. Obtener información básica
    connector = AstronomicalDataConnector()
    stellar_params = connector.query_stellar_parameters(target_name)
    
    # 2. Descargar datos de observación
    lightcurve = connector.get_tess_lightcurve(target_name)
    
    # 3. Pipeline de análisis completo
    pipeline = IntegratedAstronomyPipeline()
    result = await pipeline.analyze_object(
        object_id=target_name,
        coordinates=stellar_params['coordinates'],
        analysis_mode="comprehensive_analysis",
        custom_data={"lightcurve": lightcurve}
    )
    
    # 4. Análisis específico de tránsitos
    transit_service = ExoplanetTransitAnalysisService()
    transit_analysis = transit_service.detailed_transit_analysis(
        lightcurve,
        stellar_params=stellar_params
    )
    
    # 5. Generar reporte científico
    report = generate_exoplanet_report(result, transit_analysis, stellar_params)
    
    return report

<a id="ejecutar-análisis"></a>
# Ejecutar análisis
report = await characterize_exoplanet_system("TOI-715")
print(f"Planetas detectados: {len(report.detected_planets)}")
```

<a id="caso-2-survey-de-variables-en-cúmulo"></a>
### Case 2: Variable Survey in Cluster

```python
def analyze_cluster_variables(cluster_name, radius_arcmin=30):
    """Análisis de estrellas variables en un cúmulo."""
    
    # 1. Obtener miembros del cúmulo
    connector = AstronomicalDataConnector()
    cluster_members = connector.query_cluster_members(
        cluster_name=cluster_name,
        radius=radius_arcmin,
        probability_threshold=0.7
    )
    
    # 2. Crear workflow de monitoreo
    workflow_system = AdvancedAstronomyWorkflow()
    execution_id = workflow_system.create_workflow_execution(
        "variable_monitoring_v1",
        [member['source_id'] for member in cluster_members],
        priority=Priority.HIGH
    )
    
    # 3. Ejecutar análisis
    report = workflow_system.execute_workflow(execution_id)
    
    # 4. Clasificar variables encontradas
    variables = []
    for obj_id, result in report.results.items():
        if result.get('variability_detected'):
            var_type = classify_variable_type(result)
            variables.append({
                'id': obj_id,
                'type': var_type,
                'period': result.get('period'),
                'amplitude': result.get('amplitude')
            })
    
    return variables

<a id="analizar-pleiades"></a>
# Analizar Pleiades
pleiades_variables = analyze_cluster_variables("Pleiades", radius_arcmin=60)
print(f"Variables encontradas: {len(pleiades_variables)}")
```

<a id="caso-3-búsqueda-de-binarias-eclipsantes"></a>
### Case 3: Search for Eclipsing Binaries

```python
def eclipsing_binary_search(field_coordinates, search_radius):
    """Búsqueda sistemática de binarias eclipsantes."""
    
    # 1. Obtener objetos en el campo
    connector = AstronomicalDataConnector()
    field_objects = connector.query_field_objects(
        coordinates=field_coordinates,
        radius=search_radius,
        magnitude_limit=16,
        variability_flag=True
    )
    
    # 2. Pipeline especializado para binarias
    binary_service = BinarySystemAnalysisService()
    candidates = []
    
    for obj in field_objects:
        # Obtener curva de luz
        lightcurve = connector.get_object_lightcurve(obj['id'])
        
        # Análisis de eclipses
        eclipse_analysis = binary_service.detect_eclipses(
            lightcurve,
            min_depth=0.01,
            eclipse_detection_threshold=5.0
        )
        
        if eclipse_analysis['eclipses_detected']:
            # Análisis orbital completo
            orbital_params = binary_service.fit_binary_orbit(
                lightcurve,
                eclipse_times=eclipse_analysis['eclipse_times']
            )
            
            candidates.append({
                'object_id': obj['id'],
                'coordinates': obj['coordinates'],
                'orbital_period': orbital_params['period'],
                'eclipse_depth_primary': orbital_params['depth_1'],
                'eclipse_depth_secondary': orbital_params['depth_2'],
                'confidence': orbital_params['fit_quality']
            })
    
    return candidates

<a id="búsqueda-en-región-específica"></a>
# Búsqueda en región específica
candidates = eclipsing_binary_search(
    field_coordinates=(45.0, 30.0),
    search_radius=2.0  # grados
)
```

---

<a id="-apis-y-bases-de-datos-apis"></a>
## 🔗 APIs and Databases {#apis}

<a id="simbad---base-de-datos-de-objetos-astronómicos"></a>
### SIMBAD - Database of Astronomical Objects

```python
<a id="búsqueda-básica-en-simbad"></a>
# Búsqueda básica en SIMBAD
simbad_query = """
SELECT main_id, ra, dec, pmra, pmdec, plx, rvz_radvel, sp_type, mag_V
FROM basic 
WHERE CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', 83.82, -5.39, 0.1)) = 1
"""

simbad_results = connector.execute_simbad_query(simbad_query)
```

<a id="gaia-data-release-3"></a>
### Gaia Data Release 3

```python
<a id="query-avanzado-a-gaia-dr3"></a>
# Query avanzado a Gaia DR3
gaia_query = """
SELECT source_id, ra, dec, pmra, pmdec, parallax, 
       phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag,
       teff_gspphot, logg_gspphot, mh_gspphot,
       radius_gspphot, lum_gspphot
FROM gaiadr3.gaia_source 
WHERE CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', 266.42, -29.01, 0.5)) = 1
  AND phot_g_mean_mag < 15
  AND parallax > 10
"""

gaia_results = connector.execute_gaia_query(gaia_query)
```

<a id="nasa-exoplanet-archive"></a>
### NASA Exoplanet Archive

```python
<a id="obtener-datos-de-exoplanetas-confirmados"></a>
# Obtener datos de exoplanetas confirmados
exoplanet_query = """
SELECT pl_name, hostname, pl_orbper, pl_rade, pl_masse, 
       pl_eqt, st_teff, st_rad, st_mass, disc_year
FROM ps 
WHERE disc_year >= 2020 
  AND pl_rade IS NOT NULL 
  AND pl_masse IS NOT NULL
"""

exoplanet_data = connector.query_nasa_exoplanet_archive(exoplanet_query)
```

<a id="tess-data-access"></a>
### TESS Data Access

```python
<a id="acceso-directo-a-datos-tess"></a>
# Acceso directo a datos TESS
tess_sectors = connector.get_tess_sectors_for_target("TIC 441420236")
lightcurves = []

for sector in tess_sectors:
    lc = connector.download_tess_lightcurve(
        tic_id="441420236",
        sector=sector,
        cadence="2min",
        quality_flags=True
    )
    lightcurves.append(lc)

<a id="combinar-sectores"></a>
# Combinar sectores
combined_lc = connector.combine_tess_sectors(lightcurves)
```

---

<a id="-mejores-prácticas-mejores-prácticas"></a>
## ⭐ Best Practices {#mejores-prácticas}

<a id="1-gestión-de-datos"></a>
### 1. Data Management

```python
<a id="configurar-cache-inteligente"></a>
# Configurar cache inteligente
from app.utils.data_cache import AstronomicalDataCache

cache = AstronomicalDataCache(
    cache_dir="./axiom_cache",
    max_size_gb=10,
    retention_days=30
)

<a id="usar-cache-para-consultas-repetitivas"></a>
# Usar cache para consultas repetitivas
@cache.cached_query
def get_stellar_parameters(object_name):
    return connector.query_simbad(object_name)
```

<a id="2-manejo-de-errores"></a>
### 2. Error Handling

```python
from app.utils.error_handling import AxiomException, RetryableError

try:
    result = await pipeline.analyze_object(object_id)
except RetryableError as e:
    # Reintentar con backoff exponencial
    result = await pipeline.analyze_object(object_id, retry=True)
except AxiomException as e:
    # Log del error y continuar con el siguiente objeto
    logger.error(f"Error procesando {object_id}: {e}")
    continue
```

<a id="3-optimización-de-performance"></a>
### 3. Performance Optimization

```python
<a id="configurar-paralelización-óptima"></a>
# Configurar paralelización óptima
import multiprocessing as mp

optimal_workers = min(mp.cpu_count(), len(targets), 8)
pipeline.configure_parallel_processing(max_workers=optimal_workers)

<a id="usar-procesamiento-por-lotes-para-grandes-datasets"></a>
# Usar procesamiento por lotes para grandes datasets
batch_size = 50
for i in range(0, len(large_target_list), batch_size):
    batch = large_target_list[i:i+batch_size]
    batch_results = await pipeline.analyze_batch(batch)
    process_batch_results(batch_results)
```

<a id="4-validación-de-calidad"></a>
### 4. Quality Validation

```python
<a id="configurar-umbrales-de-calidad"></a>
# Configurar umbrales de calidad
quality_config = {
    'min_data_points': 1000,
    'max_noise_level': 0.01,
    'min_snr': 5.0,
    'required_coverage': 0.8
}

<a id="validar-antes-del-análisis"></a>
# Validar antes del análisis
if not validate_data_quality(lightcurve, quality_config):
    logger.warning(f"Datos de baja calidad para {object_id}")
    continue
```

---

<a id="-solución-de-problemas-troubleshooting"></a>
## 🔧 Troubleshooting {#troubleshooting}

<a id="problemas-comunes"></a>
### Common Problems

<a id="1-error-de-conexión-a-apis"></a>
#### 1. API Connection Error
```python
<a id="configurar-timeouts-y-reintentos"></a>
# Configurar timeouts y reintentos
connector = AstronomicalDataConnector(
    timeout=30,
    max_retries=3,
    retry_delay=2.0
)

<a id="usar-mirrors-alternativos"></a>
# Usar mirrors alternativos
if not connector.test_connection('simbad'):
    connector.use_mirror('simbad', 'backup')
```

<a id="2-memoria-insuficiente"></a>
#### 2. Insufficient Memory
```python
<a id="procesamiento-streaming-para-grandes-datasets"></a>
# Procesamiento streaming para grandes datasets
def stream_analysis(target_list, chunk_size=100):
    for chunk in chunks(target_list, chunk_size):
        yield pipeline.analyze_batch(chunk)
        gc.collect()  # Liberar memoria
```

<a id="3-datos-faltantes-o-corruptos"></a>
#### 3. Missing or Corrupt Data
```python
<a id="validación-robusta-de-datos"></a>
# Validación robusta de datos
def validate_lightcurve(lc):
    checks = [
        len(lc.time) > 100,
        not np.all(np.isnan(lc.flux)),
        np.std(lc.flux) > 0,
        len(lc.time) == len(lc.flux)
    ]
    return all(checks)
```

<a id="logging-y-diagnóstico"></a>
### Logging and Diagnostics

```python
import logging

<a id="configurar-logging-detallado"></a>
# Configurar logging detallado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('axiom_analysis.log'),
        logging.StreamHandler()
    ]
)

<a id="diagnóstico-del-sistema"></a>
# Diagnóstico del sistema
def system_diagnostics():
    diagnostics = {
        'available_memory': get_available_memory(),
        'disk_space': get_disk_space(),
        'api_status': test_all_api_connections(),
        'service_health': test_all_services()
    }
    return diagnostics
```

---

<a id="-ejemplos-de-salida"></a>
## 🎯 Output Examples

<a id="reporte-de-análisis-individual"></a>
### Individual Analysis Report
```json
{
  "object_id": "HD 209458",
  "analysis_timestamp": "2025-09-25T10:30:00Z",
  "overall_quality": 0.89,
  "execution_time": 45.3,
  "services_executed": [
    "lightkurve_advanced",
    "stellar_variability", 
    "exoplanet_transit",
    "astronomical_ml"
  ],
  "results": {
    "stellar_classification": "G0V",
    "variability_detected": false,
    "transits_detected": true,
    "planet_candidates": [
      {
        "period": 3.524746,
        "radius_ratio": 0.12156,
        "impact_parameter": 0.721,
        "confidence": 0.96
      }
    ]
  },
  "recommendations": [
    "Confirmar tránsito con observaciones adicionales",
    "Analizar velocidades radiales para masa planetaria"
  ]
}
```

<a id="reporte-de-workflow"></a>
### Workflow Report
```json
{
  "workflow_id": "exoplanet_search_20250925_103000",
  "total_objects": 150,
  "successful_analyses": 147,
  "execution_time": 1847.2,
  "scientific_findings": [
    "12 nuevos candidatos planetarios detectados",
    "3 sistemas multi-planetarios identificados",
    "1 binaria eclipsante descubierta"
  ],
  "statistics": {
    "planet_detection_rate": 0.08,
    "false_positive_rate": 0.02,
    "average_snr": 8.4
  }
}
```

---

<a id="-recursos-adicionales"></a>
## 📚 Additional Resources

- **API Documentation**: Links to official documentation for SIMBAD, Gaia, TESS
- **Tutorials**: Jupyter Notebooks with detailed examples
- **Publications**: Scientific papers using the AXIOM system
- **Community**: User and contributor forum
- **Source Code**: GitHub repository with updated examples

---

**The AXIOM System is ready to revolutionize your astronomical research!** 🚀✨

To get started, run the examples in the "Quick Start" section and explore the different services according to your specific research needs.
