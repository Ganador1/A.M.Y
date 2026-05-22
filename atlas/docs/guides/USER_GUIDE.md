# 👥 AXIOM System User Guide - Advanced Astronomical Analysis

## 📋 Table of Contents
1. [Introduction to AXIOM System](#introduction)
2. [Installation and Configuration](#installation)
3. [System Architecture](#architecture)
4. [Quick Start Guide](#quick-start)
5. [Available Services](#services)
6. [Integrated Pipeline](#pipeline)
7. [Advanced Workflows](#workflows)
8. [Data Connectors](#connectors)
9. [Practical Use Cases](#use-cases)
10. [APIs and Databases](#apis)
11. [Best Practices](#best-practices)
12. [Troubleshooting](#troubleshooting)

---

## 🌟 Introduction to AXIOM System {#introduction}

The AXIOM System (Advanced eXploration and Investigation for Observational Mathematics) is a complete astronomical analysis platform that integrates:

- **12 specialized services** organized into 4 phases
- **Unified pipeline** for end-to-end analysis
- **Automated workflows** for common use cases
- **Native connectors** to astronomical APIs and databases
- **Integrated Machine Learning** for classification and detection
- **Parallel processing** for large datasets

### ✨ Key Features

- 🔬 **Multidimensional Analysis**: Photometry, astrometry, spectroscopy
- 🤖 **Integrated AI**: Automatic classification of astronomical objects
- 🚀 **Scalability**: From individual objects to complete surveys
- 🌐 **Connectivity**: SIMBAD, VizieR, Gaia, TESS, Kepler, ESA Archives
- 📊 **Visualization**: Interactive charts and automatic reports
- ⚡ **Performance**: Parallel processing and advanced optimizations

---

## 💻 Installation and Configuration {#installation}

### System Requirements

```bash
# Python 3.8+
python --version

# Main dependencies
pip install numpy scipy matplotlib astropy lightkurve
pip install scikit-learn pandas astroquery requests
pip install concurrent.futures typing pathlib
```

### Basic Configuration

```python
import os
from pathlib import Path

# Configure working directory
AXIOM_BASE_DIR = Path("./axiom_analysis")
AXIOM_BASE_DIR.mkdir(exist_ok=True)

# Configure environment variables (optional)
os.environ['AXIOM_CACHE_DIR'] = str(AXIOM_BASE_DIR / "cache")
os.environ['AXIOM_OUTPUT_DIR'] = str(AXIOM_BASE_DIR / "outputs")
```

---

## 🏗️ System Architecture {#architecture}

### Phase Structure

```
AXIOM System Architecture
├── PHASE 1: FOUNDATION
│   ├── LightkurveAdvancedService      # Light curve analysis
│   ├── AstropyPrecisionService        # Precise astronomical calculations
│   └── StellarVariabilityService      # Variability detection
│
├── PHASE 2: EXPANSION
│   ├── OptimalAperturePhotometryService  # Optimized photometry
│   ├── BinarySystemAnalysisService       # Binary analysis
│   ├── ExoplanetTransitAnalysisService   # Transit detection
│   ├── AdvancedStatisticsService         # Advanced statistics
│   └── MultiWavelengthAnalysisService    # Multi-band analysis
│
├── PHASE 3: MACHINE LEARNING
│   ├── AstrometricAnalysisService     # Astrometric analysis
│   └── AstronomicalMLService          # ML classification
│
└── PHASE 4: INTEGRATION
    ├── IntegratedAstronomyPipeline    # Unified pipeline
    └── AdvancedAstronomyWorkflow      # Automated workflows
```

---

## 🚦 Quick Start Guide {#quick-start}

### Basic Example

```python
# 1. Import main services
from app.domains.astronomy.services import (
    IntegratedAstronomyPipeline,
    AdvancedAstronomyWorkflow
)

# 2. Initialize the pipeline
pipeline = IntegratedAstronomyPipeline("./outputs")

# 3. Basic analysis of an object
result = await pipeline.analyze_object(
    object_id="HD 209458",
    coordinates=(330.79, 18.88),
    analysis_mode="standard_analysis"
)

# 4. View results
print(f"Analysis Quality: {result.overall_quality}")
print(f"Services executed: {len(result.service_results)}")
```

### Automated Workflow

```python
# 1. Initialize workflow system
workflow_system = AdvancedAstronomyWorkflow()

# 2. Create workflow for exoplanet search
objects = ["TIC 307210830", "TIC 441420236", "TIC 308538095"]
execution_id = workflow_system.create_workflow_execution(
    "exoplanet_search_v1",
    objects,
    priority=Priority.HIGH
)

# 3. Execute workflow
report = workflow_system.execute_workflow(execution_id)

# 4. Review results
print(f"Processed objects: {report.total_objects}")
print(f"Scientific findings: {len(report.scientific_findings)}")
```

---

## 🔧 Available Services {#services}

### PHASE 1: Foundation Services

#### LightkurveAdvancedService
**Purpose**: Advanced light curve analysis

```python
from app.domains.astronomy.services import LightkurveAdvancedService

service = LightkurveAdvancedService()

# Basic analysis
result = service.analyze_lightcurve(
    target="Kepler-442",
    mission="Kepler",
    remove_outliers=True,
    detrend=True
)

# Advanced features
advanced_result = service.advanced_periodogram_analysis(
    result.lightcurve,
    method="lombscargle",
    confidence_levels=[0.99, 0.999]
)
```

#### AstropyPrecisionService
**Purpose**: High-precision astronomical calculations

```python
from app.domains.astronomy.services import AstropyPrecisionService

service = AstropyPrecisionService()

# Coordinate conversions
coords = service.convert_coordinates(
    ra=83.82, dec=-5.39,
    from_frame="icrs",
    to_frame="galactic"
)

# Distance calculations
distance = service.calculate_distance_modulus(
    apparent_mag=8.5,
    absolute_mag=4.8
)
```

#### StellarVariabilityService
**Purpose**: Detection and analysis of stellar variability

```python
from app.domains.astronomy.services import StellarVariabilityService

service = StellarVariabilityService()

# Detect variability
variability = service.detect_variability(
    lightcurve_data,
    methods=["amplitude", "period", "chi_squared"]
)

# Classify variable type
classification = service.classify_variable_type(
    lightcurve_data,
    period=variability.best_period
)
```

### PHASE 2: Expansion Services

#### OptimalAperturePhotometryService
**Purpose**: Photometry with optimized aperture

```python
from app.domains.astronomy.services import OptimalAperturePhotometryService

service = OptimalAperturePhotometryService()

# Optimize aperture
optimal_aperture = service.optimize_aperture(
    target_pixel_file,
    optimization_method="snr_based",
    background_method="median"
)

# Precision photometry
photometry = service.precision_photometry(
    target_pixel_file,
    aperture=optimal_aperture,
    quality_flags=True
)
```

#### ExoplanetTransitAnalysisService
**Purpose**: Detection and analysis of exoplanetary transits

```python
from app.domains.astronomy.services import ExoplanetTransitAnalysisService

service = ExoplanetTransitAnalysisService()

# Transit search
transits = service.search_transits(
    lightcurve,
    period_range=(0.5, 50),
    duration_range=(0.1, 12),
    snr_threshold=7.0
)

# Characterize planet
planet = service.characterize_planet(
    lightcurve,
    transit_params=transits.best_fit,
    stellar_params={"mass": 1.1, "radius": 1.05}
)
```

### PHASE 3: Machine Learning

#### AstronomicalMLService
**Purpose**: Automatic classification with AI

```python
from app.domains.astronomy.services import AstronomicalMLService

service = AstronomicalMLService()

# Classify astronomical object
classification = service.classify_object(
    features=extracted_features,
    classifier_type="stellar_classification",
    confidence_threshold=0.8
)

# Detect anomalies
anomalies = service.detect_anomalies(
    lightcurve_data,
    method="isolation_forest",
    contamination=0.1
)
```

---

## 🔄 Integrated Pipeline {#pipeline}

### Analysis Configurations

```python
from app.domains.astronomy.services.integrated_astronomy_pipeline import (
    AnalysisConfiguration, AnalysisMode, DataType
)

# Quick configuration
quick_config = AnalysisConfiguration(
    analysis_mode=AnalysisMode.QUICK_SCAN,
    data_types=[DataType.PHOTOMETRY],
    quality_threshold=0.6,
    enable_parallel=True
)

# Comprehensive configuration
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

### Check Multiple Objects Analysis

```python
# List of objects to analyze
targets = [
    {"id": "HD 189733", "coords": (300.18, 22.71)},
    {"id": "WASP-12", "coords": (97.64, 29.67)},
    {"id": "Kepler-442b", "coords": (297.84, 41.91)}
]

# Parallel processing
results = []
for target in targets:
    result = await pipeline.analyze_object(
        object_id=target["id"],
        coordinates=target["coords"],
        configuration=comprehensive_config
    )
    results.append(result)

# Generate consolidated report
consolidated_report = pipeline.generate_consolidated_report(results)
```

---

## ⚙️ Advanced Workflows {#workflows}

### Predefined Workflows

#### 1. Stellar Survey Analysis
```python
# Workflow for complete stellar survey
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
# Systematic exoplanet search
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
# Continuous monitoring of variable stars
variable_targets = ["RR_Lyrae_sample", "Cepheid_sample", "Eclipsing_binaries"]

monitoring_execution = workflow_system.create_workflow_execution(
    "variable_monitoring_v1",
    variable_targets,
    priority=Priority.URGENT,
    custom_parameters={
        "monitoring_duration": 365,  # days
        "cadence": "daily",
        "alert_threshold": 0.1  # magnitudes
    }
)
```

### Custom Workflows

```python
from app.domains.astronomy.services.advanced_astronomy_workflow import WorkflowStep

# Create custom workflow
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

# Register custom template
custom_template = WorkflowTemplate(
    template_id="my_custom_analysis",
    name="Custom Analysis",
    description="My specific workflow",
    workflow_type=WorkflowType.CUSTOM_WORKFLOW,
    steps=custom_steps
)
```

---

## 🌐 Data Connectors {#connectors}

### API Configuration

```python
import os

# Configure API keys (optional for public services)
os.environ['ESA_API_KEY'] = 'your_esa_api_key'
os.environ['NASA_API_KEY'] = 'your_nasa_api_key'

# Service URLs
ASTRONOMICAL_APIS = {
    'simbad': 'https://simbad.u-strasbg.fr/simbad/sim-tap',
    'vizier': 'https://vizier.u-strasbg.fr/viz-bin/votable',
    'esa_archive': 'https://archives.esac.esa.int',
    'nasa_exoplanetarchive': 'https://exoplanetarchive.ipac.caltech.edu/TAP',
    'gaia_archive': 'https://gea.esac.esa.int/tap-server/tap'
}
```

### Using Connectors

```python
from app.connectors.astronomical_data_connector import AstronomicalDataConnector

# Initialize connector
connector = AstronomicalDataConnector()

# Query SIMBAD
simbad_data = connector.query_simbad(
    object_name="HD 209458",
    radius="5 arcmin",
    fields=["main_id", "coordinates", "mag_V", "spec_type"]
)

# Get data from Gaia
gaia_data = connector.query_gaia(
    coordinates=(330.79, 18.88),
    radius=0.01,  # degrees
    data_release="DR3"
)

# Data from TESS
tess_data = connector.get_tess_lightcurve(
    tic_id="441420236",
    sectors="all",
    quality_mask=True
)
```

---

## 📊 Practical Use Cases {#use-cases}

### Case 1: Exoplanet Characterization

```python
async def characterize_exoplanet_system(target_name):
    """Complete analysis of an exoplanetary system."""
    
    # 1. Get basic information
    connector = AstronomicalDataConnector()
    stellar_params = connector.query_stellar_parameters(target_name)
    
    # 2. Download observation data
    lightcurve = connector.get_tess_lightcurve(target_name)
    
    # 3. Comprehensive analysis pipeline
    pipeline = IntegratedAstronomyPipeline()
    result = await pipeline.analyze_object(
        object_id=target_name,
        coordinates=stellar_params['coordinates'],
        analysis_mode="comprehensive_analysis",
        custom_data={"lightcurve": lightcurve}
    )
    
    # 4. Specific transit analysis
    transit_service = ExoplanetTransitAnalysisService()
    transit_analysis = transit_service.detailed_transit_analysis(
        lightcurve,
        stellar_params=stellar_params
    )
    
    # 5. Generate scientific report
    report = generate_exoplanet_report(result, transit_analysis, stellar_params)
    
    return report

# Execute analysis
report = await characterize_exoplanet_system("TOI-715")
print(f"Planets detected: {len(report.detected_planets)}")
```

### Case 2: Cluster Variable Survey

```python
def analyze_cluster_variables(cluster_name, radius_arcmin=30):
    """Analysis of variable stars in a cluster."""
    
    # 1. Get cluster members
    connector = AstronomicalDataConnector()
    cluster_members = connector.query_cluster_members(
        cluster_name=cluster_name,
        radius=radius_arcmin,
        probability_threshold=0.7
    )
    
    # 2. Create monitoring workflow
    workflow_system = AdvancedAstronomyWorkflow()
    execution_id = workflow_system.create_workflow_execution(
        "variable_monitoring_v1",
        [member['source_id'] for member in cluster_members],
        priority=Priority.HIGH
    )
    
    # 3. Execute analysis
    report = workflow_system.execute_workflow(execution_id)
    
    # 4. Classify found variables
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

# Analyze Pleiades
pleiades_variables = analyze_cluster_variables("Pleiades", radius_arcmin=60)
print(f"Variables found: {len(pleiades_variables)}")
```

### Case 3: Eclipsing Binary Search

```python
def eclipsing_binary_search(field_coordinates, search_radius):
    """Systematic search for eclipsing binaries."""
    
    # 1. Get objects in the field
    connector = AstronomicalDataConnector()
    field_objects = connector.query_field_objects(
        coordinates=field_coordinates,
        radius=search_radius,
        magnitude_limit=16,
        variability_flag=True
    )
    
    # 2. Specialized pipeline for binaries
    binary_service = BinarySystemAnalysisService()
    candidates = []
    
    for obj in field_objects:
        # Get light curve
        lightcurve = connector.get_object_lightcurve(obj['id'])
        
        # Eclipse analysis
        eclipse_analysis = binary_service.detect_eclipses(
            lightcurve,
            min_depth=0.01,
            eclipse_detection_threshold=5.0
        )
        
        if eclipse_analysis['eclipses_detected']:
            # Complete orbital analysis
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

# Search specific region
candidates = eclipsing_binary_search(
    field_coordinates=(45.0, 30.0),
    search_radius=2.0  # degrees
)
```

---

## 🔗 APIs and Databases {#apis}

### SIMBAD - Astronomical Object Database

```python
# Basic SIMBAD query
simbad_query = """
SELECT main_id, ra, dec, pmra, pmdec, plx, rvz_radvel, sp_type, mag_V
FROM basic 
WHERE CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', 83.82, -5.39, 0.1)) = 1
"""

simbad_results = connector.execute_simbad_query(simbad_query)
```

### Gaia Data Release 3

```python
# Advanced Gaia DR3 query
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
# Get data of confirmed exoplanets
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
# Direct access to TESS data
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

# Combine sectors
combined_lc = connector.combine_tess_sectors(lightcurves)
```

---

## ⭐ Best Practices {#best-practices}

### 1. Data Management

```python
# Configure intelligent cache
from app.utils.data_cache import AstronomicalDataCache

cache = AstronomicalDataCache(
    cache_dir="./axiom_cache",
    max_size_gb=10,
    retention_days=30
)

# Use cache for repetitive queries
@cache.cached_query
def get_stellar_parameters(object_name):
    return connector.query_simbad(object_name)
```

### 2. Error Handling

```python
from app.utils.error_handling import AxiomException, RetryableError

try:
    result = await pipeline.analyze_object(object_id)
except RetryableError as e:
    # Retry with exponential backoff
    result = await pipeline.analyze_object(object_id, retry=True)
except AxiomException as e:
    # Log error and continue with next object
    logger.error(f"Error processing {object_id}: {e}")
    continue
```

### 3. Performance Optimization

```python
# Configure optimal parallelization
import multiprocessing as mp

optimal_workers = min(mp.cpu_count(), len(targets), 8)
pipeline.configure_parallel_processing(max_workers=optimal_workers)

# Use batch processing for large datasets
batch_size = 50
for i in range(0, len(large_target_list), batch_size):
    batch = large_target_list[i:i+batch_size]
    batch_results = await pipeline.analyze_batch(batch)
    process_batch_results(batch_results)
```

### 4. Quality Validation

```python
# Configure quality thresholds
quality_config = {
    'min_data_points': 1000,
    'max_noise_level': 0.01,
    'min_snr': 5.0,
    'required_coverage': 0.8
}

# Validate before analysis
if not validate_data_quality(lightcurve, quality_config):
    logger.warning(f"Low data quality for {object_id}")
    continue
```

---

## 🔧 Troubleshooting {#troubleshooting}

### Common Problems

#### 1. API Connection Error
```python
# Configure timeouts and retries
connector = AstronomicalDataConnector(
    timeout=30,
    max_retries=3,
    retry_delay=2.0
)

# Use alternative mirrors
if not connector.test_connection('simbad'):
    connector.use_mirror('simbad', 'backup')
```

#### 2. Insufficient Memory
```python
# Streaming processing for large datasets
def stream_analysis(target_list, chunk_size=100):
    for chunk in chunks(target_list, chunk_size):
        yield pipeline.analyze_batch(chunk)
        gc.collect()  # Release memory
```

#### 3. Missing or Corrupt Data
```python
# Robust data validation
def validate_lightcurve(lc):
    checks = [
        len(lc.time) > 100,
        not np.all(np.isnan(lc.flux)),
        np.std(lc.flux) > 0,
        len(lc.time) == len(lc.flux)
    ]
    return all(checks)
```

### Logging and Diagnostics

```python
import logging

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('axiom_analysis.log'),
        logging.StreamHandler()
    ]
)

# System diagnostics
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

## 🎯 Example Outputs

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
    "Confirm transit with additional observations",
    "Analyze radial velocities for planetary mass"
  ]
}
```

### Workflow Report
```json
{
  "workflow_id": "exoplanet_search_20250925_103000",
  "total_objects": 150,
  "successful_analyses": 147,
  "execution_time": 1847.2,
  "scientific_findings": [
    "12 new planetary candidates detected",
    "3 multi-planetary systems identified",
    "1 eclipsing binary discovered"
  ],
  "statistics": {
    "planet_detection_rate": 0.08,
    "false_positive_rate": 0.02,
    "average_snr": 8.4
  }
}
```

---

## 📚 Additional Resources

- **API Documentation**: Links to official SIMBAD, Gaia, TESS documentation
- **Tutorials**: Jupyter Notebooks with detailed examples
- **Publications**: Scientific papers using the AXIOM system
- **Community**: Forum for users and contributors
- **Source Code**: GitHub repository with updated examples

---

**AXIOM System is ready to revolutionize your astronomical research!** 🚀✨

To get started, execute the examples in the "Quick Start" section and explore the different services according to your specific research needs.
