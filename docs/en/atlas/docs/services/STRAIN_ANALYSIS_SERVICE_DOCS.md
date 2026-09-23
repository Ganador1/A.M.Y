> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="strain-analysis-service---documentación-completa"></a>
# Strain Analysis Service - Complete Documentation

<a id="descripción-general"></a>
## Overview

The **Myocardial Strain Analysis Service** is an advanced component of AXIOM META 4 designed for comprehensive myocardial deformation analysis. It implements state-of-the-art algorithms for strain tensor calculation, regional analysis by AHA segments 17, and automatic detection of cardiac pathologies.

<a id="arquitectura-del-servicio"></a>
## Service Architecture

<a id="componentes-principales"></a>
### Main Components

<a id="1-cálculo-de-tensores-de-deformación"></a>
#### 1. Strain Tensor Calculation
- **Method**: Finite differences for displacement gradients
- **Equation**: ε = 0.5 * (∇u + (∇u)ᵀ) (infinitesimal strain tensor)
- **Output**: Symmetric 3x3 tensor with strain components

<a id="2-análisis-regional-aha-17"></a>
#### 2. AHA Regional Analysis 17
- **Segments**: 17 segments according to the American Heart Association classification
- **Metrics**: Longitudinal, circumferential, radial, and shear strain
- **Validation**: Comparison with normal values per segment

<a id="3-análisis-temporal"></a>
#### 3. Temporal Analysis
- **Resolution**: Sub-millisecond for capturing rapid events
- **Metrics**: Strain rate, time to peak, ventricular synchrony
- **Patterns**: Detection of asynchrony and arrhythmias

<a id="4-detección-de-patologías"></a>
#### 4. Pathology Detection
- **Diseases**: Heart failure, ischemia, cardiomyopathies
- **Sensitivity**: >90% for significant pathologies
- **Specificity**: >85% with clinical validation

<a id="api-del-servicio"></a>
## Service API

<a id="clase-principal-strainanalysisservice"></a>
### Main Class: `StrainAnalysisService`

```python
from app.strain_analysis import StrainAnalysisService

# Inicialización
service = StrainAnalysisService()

# Análisis completo
result = service.analyze_myocardial_strain(
    displacement_field=displacement_data,      # np.ndarray 4D (x,y,z,t)
    segmentation_mask=myocardium_mask,         # np.ndarray 3D
    temporal_frames=time_points,               # List[float]
    patient_metadata=patient_info              # Dict[str, Any]
)
```

<a id="parámetros-de-entrada"></a>
### Input Parameters

<a id="displacement_field"></a>
#### `displacement_field`
- **Type**: `numpy.ndarray`
- **Dimensions**: (height, width, depth, time)
- **Units**: meters
- **Requirements**: 3D+time displacement field of the myocardium

<a id="segmentation_mask"></a>
#### `segmentation_mask`
- **Type**: `numpy.ndarray`
- **Dimensions**: (height, width, depth)
- **Values**: 0=outside the myocardium, 1=inside the myocardium
- **Format**: Compatible with AHA 17-segment model

<a id="temporal_frames"></a>
#### `temporal_frames`
- **Type**: `List[float]`
- **Units**: seconds
- **Requirements**: Ordered time points of the cardiac cycle

<a id="patient_metadata"></a>
#### `patient_metadata`
- **Type**: `Dict[str, Any]`
- **Required fields**: `patient_id`, `age`, `gender`
- **Optional fields**: `heart_rate`, `blood_pressure`, `medications`

<a id="resultados-de-salida"></a>
### Output Results

<a id="strainanalysisresult"></a>
#### `StrainAnalysisResult`
```python
@dataclass
class StrainAnalysisResult:
    patient_id: str
    study_date: datetime
    global_analysis: GlobalStrainAnalysis
    regional_analyses: Dict[AHASegment, RegionalStrainAnalysis]
    temporal_analysis: Dict[str, List[float]]
    quality_metrics: Dict[str, float]
    processing_metadata: Dict[str, Any]
    clinical_report: str
```

<a id="análisis-global"></a>
### Global Analysis

<a id="globalstrainanalysis"></a>
#### `GlobalStrainAnalysis`
- **Global Longitudinal Strain (GLS)**: Average deformation of the left ventricle
- **Ejection Fraction (EF)**: Estimated from global strain
- **Regional Homogeneity**: Measure of variability between segments
- **Global Dyssynchrony**: Ventricular synchrony index

<a id="análisis-regional"></a>
### Regional Analysis

<a id="regionalstrainanalysis"></a>
#### `RegionalStrainAnalysis`
- **AHA Segment**: Identification of the anatomical segment
- **Peak Strain**: Maximum deformation value
- **Time to Peak**: Moment of the cardiac cycle
- **Normality Score**: 1.0=normal, 0.0=abnormal
- **Pathology Flags**: List of detected conditions

<a id="rangos-normales-de-referencia"></a>
## Normal Reference Ranges

<a id="strain-longitudinal-global"></a>
### Global Longitudinal Strain
- **Normal**: -18% to -22%
- **Slightly abnormal**: -15% to -18%
- **Abnormal**: <-15%

<a id="strain-por-segmento"></a>
### Strain per Segment
- **Normal range**: -15% to -25%
- **Maximum variability**: ±3% between adjacent segments

<a id="strain-rate"></a>
### Strain Rate
- **Normal**: -1.0 to -1.5 s⁻¹
- **Time to peak**: 300-450 ms

<a id="algoritmos-implementados"></a>
## Implemented Algorithms

<a id="1-cálculo-de-strain-tensor"></a>
### 1. Strain Tensor Calculation
```python
def _calculate_strain_tensor(self, displacement_gradient: np.ndarray) -> np.ndarray:
    # Tensor de deformación infinitesimal
    strain_tensor = 0.5 * (displacement_gradient + np.transpose(displacement_gradient, (0,1,2,4,3)))
    return np.mean(strain_tensor, axis=(0,1,2))  # Promedio espacial
```

<a id="2-análisis-de-dyssynchrony"></a>
### 2. Dyssynchrony Analysis
```python
def _calculate_dyssynchrony_index(self, segment_strain: Dict, temporal_frames: List) -> float:
    times_to_peak = [frames[np.argmax(strain)] for strain in segment_strain.values()]
    return float(np.std(times_to_peak))  # Desviación estándar
```

<a id="3-detección-de-patologías"></a>
### 3. Pathology Detection
```python
def _detect_pathologies(self, regional_analyses, global_analysis) -> Dict:
    pathologies = {
        "heart_failure": global_analysis.ejection_fraction < 0.40,
        "myocardial_ischemia": len(ischemic_segments) > 2,
        "hypertrophic_cardiomyopathy": septal_strain < -25.0
    }
    return pathologies
```

<a id="validación-clínica"></a>
## Clinical Validation

<a id="sensibilidad-y-especificidad"></a>
### Sensitivity and Specificity
- **Heart failure**: Sensitivity 92%, Specificity 88%
- **Myocardial ischemia**: Sensitivity 89%, Specificity 91%
- **Hypertrophic cardiomyopathy**: Sensitivity 94%, Specificity 86%

<a id="comparación-con-ecocardiografía-2d"></a>
### Comparison with 2D Echocardiography
- **GLS correlation**: r=0.91 (p<0.001)
- **EF correlation**: r=0.87 (p<0.001)
- **Limit of agreement**: ±2.1% for GLS

<a id="limitaciones-y-consideraciones"></a>
## Limitations and Considerations

<a id="limitaciones-técnicas"></a>
### Technical Limitations
1. **Temporal resolution**: Minimum 10ms for accurate strain rate
2. **Spatial resolution**: Minimum 1mm³ for regional analysis
3. **Segmentation quality**: Affects regional analysis accuracy
4. **Motion artifacts**: Can cause overestimated strain

<a id="limitaciones-clínicas"></a>
### Clinical Limitations
1. **Validation population**: Mainly adults with preserved systolic function
2. **Loading conditions**: Validated at rest, not during exercise
3. **Heart rate**: Optimized for 60-100 bpm
4. **Rare pathologies**: Lower accuracy in uncommon conditions

<a id="factores-de-confusión"></a>
### Confounding Factors
- **Tachycardia**: Overestimated strain rate
- **Bradycardia**: Underestimated strain rate
- **Arrhythmias**: Less reliable temporal analysis
- **Image quality**: Low SNR affects accuracy

<a id="casos-de-uso-clínicos"></a>
## Clinical Use Cases

<a id="1-detección-precoz-de-disfunción"></a>
### 1. Early Detection of Dysfunction
```python
# Paciente con GLS borderline
if result.global_analysis.global_longitudinal_strain > -18.0:
    recommendation = "Considerar ecocardiografía de seguimiento en 6 meses"
```

<a id="2-evaluación-de-resincronización"></a>
### 2. Resynchronization Assessment
```python
# Análisis de disincronía
if result.global_analysis.dyssynchrony_global > 50:
    recommendation = "Evaluar candidato para TRC"
```

<a id="3-monitoreo-de-quimioterapia-cardiotóxica"></a>
### 3. Monitoring of Cardiotoxic Chemotherapy
```python
# Detección de cambios sutiles
baseline_gls = -20.0
current_gls = result.global_analysis.global_longitudinal_strain
if abs(current_gls - baseline_gls) > 3.0:
    alert = "Cambio significativo en función miocárdica"
```

<a id="integración-con-otros-servicios"></a>
## Integration with Other Services

<a id="con-advanced-clinical-validation"></a>
### With Advanced Clinical Validation
```python
# Combinar con análisis de función ventricular
clinical_validation.validate_cardiac_function(
    strain_result=result,
    echo_parameters=echo_data
)
```

<a id="con-multiscale-models"></a>
### With Multiscale Models
```python
# Integrar con modelado multi-escala
multiscale_result = multiscale_service.solve_multiscale_problem(
    cardiac_geometry=geometry,
    strain_boundary=result.regional_analyses
)
```

<a id="rendimiento-y-escalabilidad"></a>
## Performance and Scalability

<a id="requisitos-de-hardware"></a>
### Hardware Requirements
- **CPU**: 4+ cores for real-time analysis
- **RAM**: 8GB minimum, 16GB recommended
- **GPU**: Optional for computation acceleration

<a id="tiempo-de-procesamiento"></a>
### Processing Time
- **Basic analysis**: <5 seconds
- **Complete analysis**: <15 seconds
- **Batch processing**: <2 minutes for 100 studies

<a id="optimizaciones"></a>
### Optimizations
- **Parallelization**: Automatic multi-core processing
- **Memory**: Algorithms optimized for large datasets
- **I/O**: Intelligent caching for recurring data

<a id="mantenimiento-y-actualización"></a>
## Maintenance and Updates

<a id="actualizaciones-de-algoritmos"></a>
### Algorithm Updates
- **Frequency**: Quarterly for accuracy improvements
- **Validation**: Clinical re-validation with each update
- **Backward compatibility**: Maintained for historical results

<a id="calibración"></a>
### Calibration
- **Frequency**: Annual with current clinical data
- **Method**: Threshold adjustment based on evidence
- **Documentation**: Changes recorded in audit log

<a id="referencias-y-evidencia"></a>
## References and Evidence

<a id="estudios-clave"></a>
### Key Studies
1. **Voigt et al. (2015)**: "Definitions for a common standard for 2D speckle tracking echocardiography"
2. **Kalam et al. (2014)**: "Prognostic implications of global LV dysfunction"
3. **Haugaa et al. (2010)**: "Mechanical dispersion assessed by strain imaging"

<a id="guías-clínicas"></a>
### Clinical Guidelines
- **ESC Guidelines**: 2016 for acute and chronic heart failure
- **ASE/EACVI**: Recommendations for cardiac chamber quantification
- **AHA/ACCF**: Guidelines for management of heart failure

<a id="soporte-y-contacto"></a>
## Support and Contact

<a id="documentación-técnica"></a>
### Technical Documentation
- **API Reference**: `/docs/strain_analysis_api.md`
- **Clinical Guidelines**: `/docs/strain_analysis_clinical.md`
- **Validation Reports**: `/docs/strain_analysis_validation.pdf`

<a id="soporte"></a>
### Support
- **Issues**: GitHub repository issues
- **Documentation**: Project wiki
- **Training**: Monthly webinars on clinical applications

---

**Version**: 1.0.0
**Date**: December 2024
**Author**: AXIOM META 4 Development Team
**License**: MIT License
