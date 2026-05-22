# 🚀 Guía Completa del Sistema AXIOM - Análisis Astronómico Avanzado

## 📋 Índice
1. [Introducción al Sistema AXIOM](#introducción)
2. [Instalación y Configuración](#instalación)
3. [Arquitectura del Sistema](#arquitectura)
4. [Guía de Inicio Rápido](#inicio-rápido)
5. [Servicios Disponibles](#servicios)
6. [Pipeline Integrado](#pipeline)
7. [Workflows Avanzados](#workflows)
8. [Conectores de Datos](#conectores)
9. [Casos de Uso Prácticos](#casos-de-uso)
10. [APIs y Bases de Datos](#apis)
11. [Mejores Prácticas](#mejores-prácticas)
12. [Solución de Problemas](#troubleshooting)

---

## 🌟 Introducción al Sistema AXIOM {#introducción}

El Sistema AXIOM (Advanced eXploration and Investigation for Observational Mathematics) es una plataforma completa de análisis astronómico que integra:

- **12 servicios especializados** organizados en 4 fases
- **Pipeline unificado** para análisis end-to-end
- **Workflows automatizados** para casos de uso comunes
- **Conectores nativos** a APIs y bases de datos astronómicas
- **Machine Learning** integrado para clasificación y detección
- **Procesamiento paralelo** para grandes datasets

### ✨ Características Principales

- 🔬 **Análisis Multidimensional**: Fotometría, astrometría, espectroscopía
- 🤖 **IA Integrada**: Clasificación automática de objetos astronómicos
- 🚀 **Escalabilidad**: Desde objetos individuales hasta surveys completos
- 🌐 **Conectividad**: SIMBAD, VizieR, Gaia, TESS, Kepler, ESA Archives
- 📊 **Visualización**: Gráficos interactivos y reportes automáticos
- ⚡ **Performance**: Procesamiento paralelo y optimizaciones avanzadas

---

## 💻 Instalación y Configuración {#instalación}

### Requisitos del Sistema

```bash
# Python 3.8+
python --version

# Dependencias principales
pip install numpy scipy matplotlib astropy lightkurve
pip install scikit-learn pandas astroquery requests
pip install concurrent.futures typing pathlib
```

### Configuración Básica

```python
import os
from pathlib import Path

# Configurar directorio de trabajo
AXIOM_BASE_DIR = Path("./axiom_analysis")
AXIOM_BASE_DIR.mkdir(exist_ok=True)

# Configurar variables de entorno (opcional)
os.environ['AXIOM_CACHE_DIR'] = str(AXIOM_BASE_DIR / "cache")
os.environ['AXIOM_OUTPUT_DIR'] = str(AXIOM_BASE_DIR / "outputs")
```

---

## 🏗️ Arquitectura del Sistema {#arquitectura}

### Estructura por Fases

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

## 🚦 Guía de Inicio Rápido {#inicio-rápido}

### Ejemplo Básico

```python
# 1. Importar servicios principales
from app.domains.astronomy.services import (
    IntegratedAstronomyPipeline,
    AdvancedAstronomyWorkflow
)

# 2. Inicializar el pipeline
pipeline = IntegratedAstronomyPipeline("./outputs")

# 3. Análisis básico de un objeto
result = await pipeline.analyze_object(
    object_id="HD 209458",
    coordinates=(330.79, 18.88),
    analysis_mode="standard_analysis"
)

# 4. Ver resultados
print(f"Calidad del análisis: {result.overall_quality}")
print(f"Servicios ejecutados: {len(result.service_results)}")
```

### Workflow Automatizado

```python
# 1. Inicializar sistema de workflows
workflow_system = AdvancedAstronomyWorkflow()

# 2. Crear workflow para búsqueda de exoplanetas
objects = ["TIC 307210830", "TIC 441420236", "TIC 308538095"]
execution_id = workflow_system.create_workflow_execution(
    "exoplanet_search_v1",
    objects,
    priority=Priority.HIGH
)

# 3. Ejecutar workflow
report = workflow_system.execute_workflow(execution_id)

# 4. Revisar resultados
print(f"Objetos procesados: {report.total_objects}")
print(f"Hallazgos científicos: {len(report.scientific_findings)}")
```

---

## 🔧 Servicios Disponibles {#servicios}

### FASE 1: Servicios de Fundación

#### LightkurveAdvancedService
**Propósito**: Análisis avanzado de curvas de luz

```python
from app.domains.astronomy.services import LightkurveAdvancedService

service = LightkurveAdvancedService()

# Análisis básico
result = service.analyze_lightcurve(
    target="Kepler-442",
    mission="Kepler",
    remove_outliers=True,
    detrend=True
)

# Características avanzadas
advanced_result = service.advanced_periodogram_analysis(
    result.lightcurve,
    method="lombscargle",
    confidence_levels=[0.99, 0.999]
)
```

#### AstropyPrecisionService
**Propósito**: Cálculos astronómicos de alta precisión

```python
from app.domains.astronomy.services import AstropyPrecisionService

service = AstropyPrecisionService()

# Conversiones de coordenadas
coords = service.convert_coordinates(
    ra=83.82, dec=-5.39,
    from_frame="icrs",
    to_frame="galactic"
)

# Cálculos de distancia
distance = service.calculate_distance_modulus(
    apparent_mag=8.5,
    absolute_mag=4.8
)
```

#### StellarVariabilityService
**Propósito**: Detección y análisis de variabilidad estelar

```python
from app.domains.astronomy.services import StellarVariabilityService

service = StellarVariabilityService()

# Detectar variabilidad
variability = service.detect_variability(
    lightcurve_data,
    methods=["amplitude", "period", "chi_squared"]
)

# Clasificar tipo de variable
classification = service.classify_variable_type(
    lightcurve_data,
    period=variability.best_period
)
```

### FASE 2: Servicios de Expansión

#### OptimalAperturePhotometryService
**Propósito**: Fotometría con apertura optimizada

```python
from app.domains.astronomy.services import OptimalAperturePhotometryService

service = OptimalAperturePhotometryService()

# Optimizar apertura
optimal_aperture = service.optimize_aperture(
    target_pixel_file,
    optimization_method="snr_based",
    background_method="median"
)

# Fotometría de precisión
photometry = service.precision_photometry(
    target_pixel_file,
    aperture=optimal_aperture,
    quality_flags=True
)
```

#### ExoplanetTransitAnalysisService
**Propósito**: Detección y análisis de tránsitos exoplanetarios

```python
from app.domains.astronomy.services import ExoplanetTransitAnalysisService

service = ExoplanetTransitAnalysisService()

# Búsqueda de tránsitos
transits = service.search_transits(
    lightcurve,
    period_range=(0.5, 50),
    duration_range=(0.1, 12),
    snr_threshold=7.0
)

# Caracterizar planeta
planet = service.characterize_planet(
    lightcurve,
    transit_params=transits.best_fit,
    stellar_params={"mass": 1.1, "radius": 1.05}
)
```

### FASE 3: Machine Learning

#### AstronomicalMLService
**Propósito**: Clasificación automática con IA

```python
from app.domains.astronomy.services import AstronomicalMLService

service = AstronomicalMLService()

# Clasificar objeto astronómico
classification = service.classify_object(
    features=extracted_features,
    classifier_type="stellar_classification",
    confidence_threshold=0.8
)

# Detectar anomalías
anomalies = service.detect_anomalies(
    lightcurve_data,
    method="isolation_forest",
    contamination=0.1
)
```

---

## 🔄 Pipeline Integrado {#pipeline}

### Configuraciones de Análisis

```python
from app.domains.astronomy.services.integrated_astronomy_pipeline import (
    AnalysisConfiguration, AnalysisMode, DataType
)

# Configuración rápida
quick_config = AnalysisConfiguration(
    analysis_mode=AnalysisMode.QUICK_SCAN,
    data_types=[DataType.PHOTOMETRY],
    quality_threshold=0.6,
    enable_parallel=True
)

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

### Análisis de Objetos Múltiples

```python
# Lista de objetos a analizar
targets = [
    {"id": "HD 189733", "coords": (300.18, 22.71)},
    {"id": "WASP-12", "coords": (97.64, 29.67)},
    {"id": "Kepler-442b", "coords": (297.84, 41.91)}
]

# Procesamiento paralelo
results = []
for target in targets:
    result = await pipeline.analyze_object(
        object_id=target["id"],
        coordinates=target["coords"],
        configuration=comprehensive_config
    )
    results.append(result)

# Generar reporte consolidado
consolidated_report = pipeline.generate_consolidated_report(results)
```

---

## ⚙️ Workflows Avanzados {#workflows}

### Workflows Predefinidos

#### 1. Stellar Survey Analysis
```python
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

#### 2. Exoplanet Discovery Pipeline
```python
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

#### 3. Variable Star Monitoring
```python
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

### Workflows Personalizados

```python
from app.domains.astronomy.services.advanced_astronomy_workflow import WorkflowStep

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

## 🌐 Conectores de Datos {#conectores}

### Configuración de APIs

```python
import os

# Configurar claves de API (opcional para servicios públicos)
os.environ['ESA_API_KEY'] = 'your_esa_api_key'
os.environ['NASA_API_KEY'] = 'your_nasa_api_key'

# URLs de servicios
ASTRONOMICAL_APIS = {
    'simbad': 'https://simbad.u-strasbg.fr/simbad/sim-tap',
    'vizier': 'https://vizier.u-strasbg.fr/viz-bin/votable',
    'esa_archive': 'https://archives.esac.esa.int',
    'nasa_exoplanetarchive': 'https://exoplanetarchive.ipac.caltech.edu/TAP',
    'gaia_archive': 'https://gea.esac.esa.int/tap-server/tap'
}
```

### Uso de Conectores

```python
from app.connectors.astronomical_data_connector import AstronomicalDataConnector

# Inicializar conector
connector = AstronomicalDataConnector()

# Buscar en SIMBAD
simbad_data = connector.query_simbad(
    object_name="HD 209458",
    radius="5 arcmin",
    fields=["main_id", "coordinates", "mag_V", "spec_type"]
)

# Obtener datos de Gaia
gaia_data = connector.query_gaia(
    coordinates=(330.79, 18.88),
    radius=0.01,  # grados
    data_release="DR3"
)

# Datos de TESS
tess_data = connector.get_tess_lightcurve(
    tic_id="441420236",
    sectors="all",
    quality_mask=True
)
```

---

## 📊 Casos de Uso Prácticos {#casos-de-uso}

### Caso 1: Caracterización de Exoplanetas

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

# Ejecutar análisis
report = await characterize_exoplanet_system("TOI-715")
print(f"Planetas detectados: {len(report.detected_planets)}")
```

### Caso 2: Survey de Variables en Cúmulo

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

# Analizar Pleiades
pleiades_variables = analyze_cluster_variables("Pleiades", radius_arcmin=60)
print(f"Variables encontradas: {len(pleiades_variables)}")
```

### Caso 3: Búsqueda de Binarias Eclipsantes

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

# Búsqueda en región específica
candidates = eclipsing_binary_search(
    field_coordinates=(45.0, 30.0),
    search_radius=2.0  # grados
)
```

---

## 🔗 APIs y Bases de Datos {#apis}

### SIMBAD - Base de Datos de Objetos Astronómicos

```python
# Búsqueda básica en SIMBAD
simbad_query = """
SELECT main_id, ra, dec, pmra, pmdec, plx, rvz_radvel, sp_type, mag_V
FROM basic 
WHERE CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', 83.82, -5.39, 0.1)) = 1
"""

simbad_results = connector.execute_simbad_query(simbad_query)
```

### Gaia Data Release 3

```python
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

### NASA Exoplanet Archive

```python
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

### TESS Data Access

```python
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

# Combinar sectores
combined_lc = connector.combine_tess_sectors(lightcurves)
```

---

## ⭐ Mejores Prácticas {#mejores-prácticas}

### 1. Gestión de Datos

```python
# Configurar cache inteligente
from app.utils.data_cache import AstronomicalDataCache

cache = AstronomicalDataCache(
    cache_dir="./axiom_cache",
    max_size_gb=10,
    retention_days=30
)

# Usar cache para consultas repetitivas
@cache.cached_query
def get_stellar_parameters(object_name):
    return connector.query_simbad(object_name)
```

### 2. Manejo de Errores

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

### 3. Optimización de Performance

```python
# Configurar paralelización óptima
import multiprocessing as mp

optimal_workers = min(mp.cpu_count(), len(targets), 8)
pipeline.configure_parallel_processing(max_workers=optimal_workers)

# Usar procesamiento por lotes para grandes datasets
batch_size = 50
for i in range(0, len(large_target_list), batch_size):
    batch = large_target_list[i:i+batch_size]
    batch_results = await pipeline.analyze_batch(batch)
    process_batch_results(batch_results)
```

### 4. Validación de Calidad

```python
# Configurar umbrales de calidad
quality_config = {
    'min_data_points': 1000,
    'max_noise_level': 0.01,
    'min_snr': 5.0,
    'required_coverage': 0.8
}

# Validar antes del análisis
if not validate_data_quality(lightcurve, quality_config):
    logger.warning(f"Datos de baja calidad para {object_id}")
    continue
```

---

## 🔧 Solución de Problemas {#troubleshooting}

### Problemas Comunes

#### 1. Error de Conexión a APIs
```python
# Configurar timeouts y reintentos
connector = AstronomicalDataConnector(
    timeout=30,
    max_retries=3,
    retry_delay=2.0
)

# Usar mirrors alternativos
if not connector.test_connection('simbad'):
    connector.use_mirror('simbad', 'backup')
```

#### 2. Memoria Insuficiente
```python
# Procesamiento streaming para grandes datasets
def stream_analysis(target_list, chunk_size=100):
    for chunk in chunks(target_list, chunk_size):
        yield pipeline.analyze_batch(chunk)
        gc.collect()  # Liberar memoria
```

#### 3. Datos Faltantes o Corruptos
```python
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

### Logging y Diagnóstico

```python
import logging

# Configurar logging detallado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('axiom_analysis.log'),
        logging.StreamHandler()
    ]
)

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

## 🎯 Ejemplos de Salida

### Reporte de Análisis Individual
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

### Reporte de Workflow
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

## 📚 Recursos Adicionales

- **Documentación de APIs**: Enlaces a documentación oficial de SIMBAD, Gaia, TESS
- **Tutoriales**: Notebooks Jupyter con ejemplos detallados
- **Publicaciones**: Papers científicos usando el sistema AXIOM
- **Comunidad**: Foro de usuarios y contribuidores
- **Código Fuente**: Repositorio GitHub con ejemplos actualizados

---

**¡El Sistema AXIOM está listo para revolucionar tu investigación astronómica!** 🚀✨

Para comenzar, ejecuta los ejemplos de la sección "Inicio Rápido" y explora los diferentes servicios según tus necesidades específicas de investigación.