> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="advanced-clinical-validation-service---documentación-completa"></a>
# Advanced Clinical Validation Service - Complete Documentation

<a id="descripción-general"></a>
## Overview

The **Advanced Clinical Validation Service** is a critical component of AXIOM META 4 that implements clinical validation algorithms for advanced cardiac analysis. It provides validated methods for ejection fraction calculation, myocardial strain analysis, and cardiovascular risk assessment with clinical standards.

<a id="arquitectura-del-servicio"></a>
## Service Architecture

<a id="componentes-principales"></a>
### Main Components

<a id="1-módulo-de-fracción-de-eyección-ef"></a>
#### 1. Ejection Fraction (EF) Module
- **Methods**: Simpson, Area-Length, Teichholz
- **Validation**: Comparison with standard echocardiography
- **Accuracy**: Error < 5% vs reference methods

<a id="2-módulo-de-análisis-de-strain"></a>
#### 2. Strain Analysis Module
- **Techniques**: Speckle tracking, feature tracking
- **Parameters**: Longitudinal, radial, circumferential strain
- **Validation**: Correlation with magnetic resonance imaging

<a id="3-módulo-de-evaluación-de-riesgo"></a>
#### 3. Risk Assessment Module
- **Algorithms**: SCORE, Framingham, ASCVD
- **Factors**: Age, gender, blood pressure, cholesterol
- **Validation**: Long-term population studies

<a id="4-módulo-de-reportes-clínicos"></a>
#### 4. Clinical Reports Module
- **Formats**: Structured PDF, DICOM SR
- **Content**: Quantitative metrics, interpretations
- **Integration**: HIS/RIS, PACS

<a id="api-del-servicio"></a>
## Service API

<a id="clase-principal-advancedclinicalvalidationservice"></a>
### Main Class: `AdvancedClinicalValidationService`

```python
from app.advanced_clinical_validation import AdvancedClinicalValidationService

<a id="inicialización"></a>
# Inicialización
service = AdvancedClinicalValidationService()

<a id="validar-análisis-clínico"></a>
# Validar análisis clínico
validation_result = service.validate_clinical_analysis(
    patient_data=patient_record,
    analysis_results=strain_analysis,
    reference_standard=gold_standard
)
```

<a id="parámetros-de-entrada"></a>
### Input Parameters

<a id="datos-del-paciente"></a>
#### Patient Data
```python
patient_data = {
    'demographics': {
        'age': 65,
        'gender': 'male',
        'weight': 75.5,  # kg
        'height': 175.0,  # cm
        'bmi': 24.6
    },
    'vital_signs': {
        'systolic_bp': 140,
        'diastolic_bp': 85,
        'heart_rate': 72,
        'temperature': 36.8
    },
    'medical_history': {
        'hypertension': True,
        'diabetes': False,
        'smoking': 'former',
        'family_history': ['coronary_artery_disease']
    },
    'medications': [
        {'name': 'Aspirin', 'dose': '100mg', 'frequency': 'daily'},
        {'name': 'Metoprolol', 'dose': '50mg', 'frequency': 'bid'}
    ]
}
```

<a id="resultados-de-análisis"></a>
#### Analysis Results
```python
analysis_results = {
    'ef_calculation': {
        'method': 'simpson',
        'value': 0.45,
        'confidence_interval': [0.42, 0.48],
        'volumes': {
            'edv': 180.0,  # mL
            'esv': 99.0,   # mL
            'sv': 81.0     # mL
        }
    },
    'strain_analysis': {
        'global_longitudinal_strain': -18.5,
        'regional_strain': {
            'basal': {'anterior': -15.2, 'septal': -22.1, 'lateral': -16.8, 'inferior': -19.5},
            'mid': {'anterior': -17.8, 'septal': -20.5, 'lateral': -18.2, 'inferior': -21.1},
            'apical': {'anterior': -19.5, 'septal': -18.9, 'lateral': -20.1, 'inferior': -22.3}
        },
        'bulls_eye_plot': np.array([...])  # 17 segmentos AHA
    },
    'wall_motion_abnormalities': [
        {'segment': 7, 'severity': 'hypokinetic', 'location': 'mid inferolateral'},
        {'segment': 12, 'severity': 'akinetic', 'location': 'apical anterior'}
    ]
}
```

<a id="estándares-de-referencia"></a>
### Reference Standards
```python
reference_standard = {
    'modality': 'cardiac_mri',
    'ef_value': 0.47,
    'strain_values': {
        'gls': -19.2,
        'regional': {...}
    },
    'measurement_date': '2024-01-15',
    'operator': 'Dr. Smith',
    'equipment': 'Siemens MAGNETOM Vida'
}
```

<a id="métodos-de-validación"></a>
## Validation Methods

<a id="1-validación-de-fracción-de-eyección"></a>
### 1. Ejection Fraction Validation

<a id="método-simpson"></a>
#### Simpson Method
```python
def _validate_simpson_method(self, volumes: Dict, reference: Dict) -> ValidationResult:
    """
    Validar cálculo de EF usando método de Simpson
    """
    # Calcular EF
    ef_calculated = (volumes['edv'] - volumes['esv']) / volumes['edv']

    # Comparar con referencia
    ef_reference = reference['ef_value']
    absolute_error = abs(ef_calculated - ef_reference)
    relative_error = absolute_error / ef_reference

    # Evaluar precisión
    precision_grade = self._assess_precision(absolute_error, relative_error)

    return ValidationResult(
        method='simpson',
        calculated_value=ef_calculated,
        reference_value=ef_reference,
        absolute_error=absolute_error,
        relative_error=relative_error,
        precision_grade=precision_grade,
        confidence_interval=self._calculate_confidence_interval(ef_calculated, volumes)
    )
```

<a id="método-área-longitud"></a>
#### Area-Length Method
```python
def _validate_area_length_method(self, areas: Dict, length: float) -> ValidationResult:
    """
    Validar cálculo de EF usando método área-longitud
    """
    # Fórmula: V = (5/6) * A1 * (L1 + L2) - (5/6) * A2 * L2
    edv = (5/6) * areas['lvot_area'] * (length + areas['lvot_length'])
    esv = (5/6) * areas['lvot_area_es'] * areas['lvot_length_es']

    ef_calculated = (edv - esv) / edv

    # Validación similar al método Simpson
    return self._validate_ef_calculation(ef_calculated, reference)
```

<a id="2-validación-de-strain-miocárdico"></a>
### 2. Myocardial Strain Validation

<a id="strain-longitudinal-global"></a>
#### Global Longitudinal Strain
```python
def _validate_global_longitudinal_strain(self, gls_measured: float, gls_reference: float) -> ValidationResult:
    """
    Validar strain longitudinal global
    """
    # Criterios de normalidad
    normal_range = (-20.9, -15.9)  # percent

    # Calcular error
    absolute_error = abs(gls_measured - gls_reference)
    relative_error = absolute_error / abs(gls_reference)

    # Evaluar acuerdo
    agreement_grade = self._assess_strain_agreement(
        measured=gls_measured,
        reference=gls_reference,
        tolerance=2.0  # 2% tolerance
    )

    return ValidationResult(
        parameter='GLS',
        measured_value=gls_measured,
        reference_value=gls_reference,
        absolute_error=absolute_error,
        relative_error=relative_error,
        agreement_grade=agreement_grade,
        clinical_interpretation=self._interpret_gls_value(gls_measured)
    )
```

<a id="strain-regional"></a>
#### Regional Strain
```python
def _validate_regional_strain(self, regional_measured: Dict, regional_reference: Dict) -> Dict[str, ValidationResult]:
    """
    Validar strain regional por segmentos AHA
    """
    validation_results = {}

    for segment in self.aha_segments:
        measured = regional_measured.get(segment, 0)
        reference = regional_reference.get(segment, 0)

        # Validación por segmento
        segment_validation = self._validate_single_segment_strain(
            segment=segment,
            measured=measured,
            reference=reference
        )

        validation_results[segment] = segment_validation

    return validation_results
```

<a id="3-validación-de-anomalías-de-movimiento-parietal"></a>
### 3. Wall Motion Abnormality Validation

<a id="detección-de-anomalías"></a>
#### Abnormality Detection
```python
def _validate_wall_motion_abnormalities(self, detected_abnormalities: List[Dict], reference_abnormalities: List[Dict]) -> ValidationMetrics:
    """
    Validar detección de anomalías de movimiento parietal
    """
    # Calcular métricas de clasificación
    tp, fp, fn, tn = self._calculate_confusion_matrix(
        detected=detected_abnormalities,
        reference=reference_abnormalities
    )

    # Métricas de rendimiento
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    accuracy = (tp + tn) / (tp + tn + fp + fn)

    # F1-score
    f1_score = 2 * (precision * sensitivity) / (precision + sensitivity) if (precision + sensitivity) > 0 else 0

    return ValidationMetrics(
        sensitivity=sensitivity,
        specificity=specificity,
        precision=precision,
        accuracy=accuracy,
        f1_score=f1_score,
        confusion_matrix={'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn}
    )
```

<a id="interpretación-clínica"></a>
## Clinical Interpretation

<a id="rangos-de-normalidad"></a>
### Normality Ranges

<a id="fracción-de-eyección"></a>
#### Ejection Fraction
```python
def _interpret_ef_value(self, ef_value: float) -> ClinicalInterpretation:
    """
    Interpretar valor de fracción de eyección
    """
    if ef_value >= 0.55:
        category = 'normal'
        risk_level = 'low'
        recommendations = ['seguir controles rutinarios']
    elif 0.45 <= ef_value < 0.55:
        category = 'borderline'
        risk_level = 'moderate'
        recommendations = ['evaluar factores de riesgo', 'considerar ecocardiograma de seguimiento']
    elif 0.35 <= ef_value < 0.45:
        category = 'reduced_mild'
        risk_level = 'high'
        recommendations = ['iniciar tratamiento médico', 'evaluar indicación de dispositivo']
    else:  # ef_value < 0.35
        category = 'severely_reduced'
        risk_level = 'critical'
        recommendations = ['evaluación urgente por cardiología', 'considerar trasplante cardíaco']

    return ClinicalInterpretation(
        category=category,
        risk_level=risk_level,
        recommendations=recommendations,
        follow_up_interval=self._calculate_follow_up_interval(ef_value)
    )
```

<a id="strain-longitudinal-global-1"></a>
#### Global Longitudinal Strain
```python
def _interpret_gls_value(self, gls_value: float) -> ClinicalInterpretation:
    """
    Interpretar valor de strain longitudinal global
    """
    if gls_value > -15.9:  # Más negativo = mejor función
        category = 'impaired'
        risk_level = 'high'
        recommendations = ['evaluar causa de disfunción', 'considerar optimización terapéutica']
    elif -20.9 <= gls_value <= -15.9:
        category = 'normal'
        risk_level = 'low'
        recommendations = ['mantener estilo de vida saludable']
    else:  # gls_value < -20.9
        category = 'supranormal'
        risk_level = 'low'
        recommendations = ['evaluar si corresponde a atleta o condición fisiológica']

    return ClinicalInterpretation(...)
```

<a id="evaluación-de-riesgo-cardiovascular"></a>
### Cardiovascular Risk Assessment

<a id="sistema-score"></a>
#### SCORE System
```python
def _calculate_score_risk(self, patient_data: Dict) -> RiskAssessment:
    """
    Calcular riesgo cardiovascular usando sistema SCORE
    """
    # Factores de riesgo
    age = patient_data['demographics']['age']
    gender = patient_data['demographics']['gender']
    smoker = patient_data['medical_history']['smoking'] in ['current', 'former']
    systolic_bp = patient_data['vital_signs']['systolic_bp']
    total_cholesterol = patient_data.get('laboratory', {}).get('total_cholesterol', 200)

    # Calcular riesgo a 10 años
    if gender == 'male':
        risk_score = self._male_score_calculation(age, smoker, systolic_bp, total_cholesterol)
    else:
        risk_score = self._female_score_calculation(age, smoker, systolic_bp, total_cholesterol)

    # Categorizar riesgo
    if risk_score < 1:
        category = 'low'
        recommendations = ['estilo de vida saludable', 'controles anuales']
    elif 1 <= risk_score < 5:
        category = 'moderate'
        recommendations = ['modificar factores de riesgo', 'considerar tratamiento farmacológico']
    elif 5 <= risk_score < 10:
        category = 'high'
        recommendations = ['tratamiento intensivo', 'evaluación especializada']
    else:  # risk_score >= 10
        category = 'very_high'
        recommendations = ['manejo multidisciplinario', 'considerar intervenciones invasivas']

    return RiskAssessment(
        system='SCORE',
        risk_score=risk_score,
        category=category,
        recommendations=recommendations,
        confidence_interval=self._calculate_risk_ci(risk_score)
    )
```

<a id="generación-de-reportes"></a>
## Report Generation

<a id="reporte-estructurado"></a>
### Structured Report
```python
def _generate_structured_report(self, validation_results: Dict, patient_data: Dict) -> ClinicalReport:
    """
    Generar reporte clínico estructurado
    """
    report = ClinicalReport()

    # Encabezado
    report.header = self._create_report_header(patient_data)

    # Resumen ejecutivo
    report.executive_summary = self._create_executive_summary(validation_results)

    # Resultados detallados
    report.detailed_results = {
        'ef_validation': self._format_ef_validation(validation_results['ef']),
        'strain_validation': self._format_strain_validation(validation_results['strain']),
        'wall_motion_validation': self._format_wall_motion_validation(validation_results['wall_motion']),
        'risk_assessment': self._format_risk_assessment(validation_results['risk'])
    }

    # Interpretación clínica
    report.clinical_interpretation = self._create_clinical_interpretation(validation_results)

    # Recomendaciones
    report.recommendations = self._generate_recommendations(validation_results, patient_data)

    # Apéndices
    report.appendices = {
        'methodology': self._create_methodology_appendix(),
        'references': self._create_references_appendix(),
        'quality_metrics': self._create_quality_metrics_appendix(validation_results)
    }

    return report
```

<a id="formatos-de-salida"></a>
### Output Formats

<a id="pdf-clínico"></a>
#### Clinical PDF
```python
def _generate_pdf_report(self, clinical_report: ClinicalReport) -> bytes:
    """
    Generar reporte en formato PDF
    """
    # Usar librería de generación PDF (ej: reportlab, fpdf)
    pdf_buffer = io.BytesIO()

    # Crear documento
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Contenido del reporte
    content = []

    # Título
    title = Paragraph("Reporte de Validación Clínica Avanzada", styles['Title'])
    content.append(title)

    # Información del paciente
    patient_info = self._create_patient_info_section(clinical_report.header)
    content.append(patient_info)

    # Resultados
    results_section = self._create_results_section(clinical_report.detailed_results)
    content.append(results_section)

    # Generar PDF
    doc.build(content)

    return pdf_buffer.getvalue()
```

<a id="dicom-structured-report"></a>
#### DICOM Structured Report
```python
def _generate_dicom_sr(self, clinical_report: ClinicalReport) -> pydicom.Dataset:
    """
    Generar reporte estructurado DICOM
    """
    # Crear dataset DICOM SR
    ds = pydicom.Dataset()

    # Encabezado DICOM
    ds.SOPClassUID = '1.2.840.10008.5.1.4.1.1.88.11'  # Comprehensive SR
    ds.SOPInstanceUID = pydicom.uid.generate_uid()
    ds.StudyInstanceUID = clinical_report.header['study_uid']
    ds.SeriesInstanceUID = pydicom.uid.generate_uid()

    # Contenido estructurado
    ds.ContentSequence = self._create_sr_content_sequence(clinical_report)

    return ds
```

<a id="validación-estadística"></a>
## Statistical Validation

<a id="análisis-de-concordancia"></a>
### Agreement Analysis
```python
def _calculate_concordance_statistics(self, measured_values: np.ndarray, reference_values: np.ndarray) -> ConcordanceStats:
    """
    Calcular estadísticas de concordancia
    """
    # Coeficiente de correlación de Pearson
    pearson_r, pearson_p = stats.pearsonr(measured_values, reference_values)

    # Coeficiente de correlación intraclasse
    icc, icc_ci = self._calculate_icc(measured_values, reference_values)

    # Bland-Altman analysis
    bland_altman = self._bland_altman_analysis(measured_values, reference_values)

    # Error absoluto medio
    mae = np.mean(np.abs(measured_values - reference_values))

    # Error relativo medio
    mre = np.mean(np.abs(measured_values - reference_values) / reference_values)

    return ConcordanceStats(
        pearson_correlation={'r': pearson_r, 'p_value': pearson_p},
        intraclass_correlation={'icc': icc, 'confidence_interval': icc_ci},
        bland_altman=bland_altman,
        mean_absolute_error=mae,
        mean_relative_error=mre
    )
```

<a id="análisis-de-bland-altman"></a>
### Bland-Altman Analysis
```python
def _bland_altman_analysis(self, measured: np.ndarray, reference: np.ndarray) -> BlandAltmanResult:
    """
    Realizar análisis de Bland-Altman
    """
    # Calcular diferencias
    differences = measured - reference
    mean_difference = np.mean(differences)
    std_difference = np.std(differences)

    # Límites de concordancia
    upper_limit = mean_difference + 1.96 * std_difference
    lower_limit = mean_difference - 1.96 * std_difference

    # Promedio de medidas
    average_values = (measured + reference) / 2

    return BlandAltmanResult(
        mean_difference=mean_difference,
        std_difference=std_difference,
        upper_limit=upper_limit,
        lower_limit=lower_limit,
        differences=differences,
        average_values=average_values
    )
```

<a id="integración-con-sistemas"></a>
## System Integration

<a id="hisris-integration"></a>
### HIS/RIS Integration
```python
def _integrate_with_his(self, clinical_report: ClinicalReport, patient_id: str) -> IntegrationResult:
    """
    Integrar resultados con sistema HIS/RIS
    """
    # Conectar a HIS
    his_connection = self._establish_his_connection()

    # Crear entrada de resultados
    result_entry = {
        'patient_id': patient_id,
        'study_date': clinical_report.header['study_date'],
        'modality': 'CARDIAC_VALIDATION',
        'results': clinical_report.detailed_results,
        'interpretation': clinical_report.clinical_interpretation,
        'recommendations': clinical_report.recommendations
    }

    # Enviar a HIS
    integration_status = his_connection.send_results(result_entry)

    return IntegrationResult(
        success=integration_status['success'],
        message=integration_status['message'],
        transaction_id=integration_status.get('transaction_id'),
        timestamp=datetime.now()
    )
```

<a id="pacs-integration"></a>
### PACS Integration
```python
def _integrate_with_pacs(self, dicom_sr: pydicom.Dataset, study_uid: str) -> IntegrationResult:
    """
    Integrar reporte DICOM con PACS
    """
    # Conectar a PACS
    pacs_connection = self._establish_pacs_connection()

    # Enviar DICOM SR
    send_status = pacs_connection.send_dicom_object(dicom_sr, study_uid)

    return IntegrationResult(
        success=send_status['success'],
        message=send_status['message'],
        sop_instance_uid=dicom_sr.SOPInstanceUID,
        timestamp=datetime.now()
    )
```

<a id="monitoreo-de-calidad"></a>
## Quality Monitoring

<a id="métricas-de-rendimiento"></a>
### Performance Metrics
```python
def _calculate_performance_metrics(self, validation_results: List[ValidationResult]) -> QualityMetrics:
    """
    Calcular métricas de rendimiento del servicio
    """
    # Precisión general
    accuracies = [result.relative_error for result in validation_results]
    mean_accuracy = np.mean(accuracies)
    accuracy_std = np.std(accuracies)

    # Tasa de éxito de validación
    success_rate = len([r for r in validation_results if r.agreement_grade == 'excellent']) / len(validation_results)

    # Tiempo de procesamiento
    processing_times = [result.processing_time for result in validation_results]
    mean_processing_time = np.mean(processing_times)

    return QualityMetrics(
        mean_accuracy=mean_accuracy,
        accuracy_std=accuracy_std,
        success_rate=success_rate,
        mean_processing_time=mean_processing_time,
        total_validations=len(validation_results)
    )
```

<a id="alertas-de-calidad"></a>
### Quality Alerts
```python
def _monitor_quality_alerts(self, quality_metrics: QualityMetrics) -> List[QualityAlert]:
    """
    Monitorear y generar alertas de calidad
    """
    alerts = []

    # Alerta de precisión baja
    if quality_metrics.mean_accuracy > self.accuracy_threshold:
        alerts.append(QualityAlert(
            type='accuracy_degradation',
            severity='high',
            message=f'Precisión promedio degradada: {quality_metrics.mean_accuracy:.2%}',
            recommended_action='Revisar algoritmos de validación'
        ))

    # Alerta de tiempo de procesamiento alto
    if quality_metrics.mean_processing_time > self.processing_time_threshold:
        alerts.append(QualityAlert(
            type='performance_degradation',
            severity='medium',
            message=f'Tiempo de procesamiento elevado: {quality_metrics.mean_processing_time:.2f}s',
            recommended_action='Optimizar algoritmos'
        ))

    return alerts
```

<a id="casos-de-uso"></a>
## Use Cases

<a id="1-validación-de-análisis-de-strain"></a>
### 1. Strain Analysis Validation
```python
<a id="caso-paciente-con-sospecha-de-miocardiopatía"></a>
# Caso: Paciente con sospecha de miocardiopatía
validation_case = {
    'patient': {
        'age': 55,
        'symptoms': ['disnea', 'fatiga'],
        'ecg': 'normal',
        'troponin': 'elevado'
    },
    'analysis': {
        'gls': -12.5,  # Reducido
        'regional_strain': 'patrón apical-sparing'
    },
    'reference': {
        'modality': 'rm_cardiac',
        'gls': -13.2
    }
}

result = service.validate_clinical_analysis(**validation_case)
print(f"Validación: {result.agreement_grade}")
print(f"Interpretación: {result.clinical_interpretation}")
```

<a id="2-evaluación-de-riesgo-post-infarto"></a>
### 2. Post-Infarction Risk Assessment
```python
<a id="caso-paciente-post-iam-con-fe-reducida"></a>
# Caso: Paciente post-IAM con FE reducida
risk_case = {
    'patient': {
        'age': 62,
        'gender': 'male',
        'ef': 0.35,
        'comorbidities': ['hipertension', 'diabetes'],
        'laboratory': {
            'ldl': 180,
            'hdl': 35,
            'creatinine': 1.8
        }
    }
}

risk_assessment = service.assess_cardiovascular_risk(risk_case)
print(f"Riesgo SCORE: {risk_assessment.risk_score}%")
print(f"Categoría: {risk_assessment.category}")
```

<a id="limitaciones-y-consideraciones"></a>
## Limitations and Considerations

<a id="limitaciones-técnicas"></a>
### Technical Limitations
1. **Image quality dependency**: Accuracy depends on acquisition quality
2. **Inter-observer variability**: Differences between operators
3. **Algorithm limitations**: Does not replace expert clinical judgment
4. **Limited validation**: Mainly in adult populations

<a id="consideraciones-clínicas"></a>
### Clinical Considerations
1. **Clinical context**: Results should be interpreted in context
2. **Multimodal correlation**: Comparison with multiple modalities is recommended
3. **Longitudinal follow-up**: Important to evaluate changes over time
4. **Confounding factors**: Consider comorbid conditions

<a id="consideraciones-éticas"></a>
### Ethical Considerations
1. **Confidentiality**: Protection of patient data
2. **Consent**: Clear information about data use
3. **Transparency**: Explanation of algorithms and limitations
4. **Responsibility**: Appropriate use as a support tool

<a id="referencias"></a>
## References

<a id="guías-clínicas"></a>
### Clinical Guidelines
1. **ESC Guidelines**: "2016 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure"
2. **ASE/EACVI**: "Recommendations for cardiac chamber quantification by echocardiography"
3. **AHA/ACC**: "Guidelines for the evaluation and management of chronic heart failure"

<a id="literatura-científica"></a>
### Scientific Literature
1. **Thiele et al. (2019)**: "Strain imaging in cardio-oncology"
2. **Kalam et al. (2020)**: "Prognostic implications of global longitudinal strain"
3. **Voigt et al. (2015)**: "Definitions for a common standard for 2D speckle tracking echocardiography"

<a id="estándares"></a>
### Standards
1. **DICOM**: "Structured Reporting supplements"
2. **HL7 FHIR**: "Cardiac imaging resources"
3. **IHE**: "Cardiac Cath Workflow Profile"

---

**Version**: 1.0.0
**Date**: December 2024
**Author**: AXIOM META 4 Development Team
**License**: MIT License
