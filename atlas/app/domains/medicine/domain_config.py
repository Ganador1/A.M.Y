"""
Configuración Avanzada del Dominio Medicine
==========================================

Sistema de configuración comprehensivo para el dominio médico con:
- Configuración de servicios médicos especializados
- Thresholds de validación clínica
- Parámetros de calidad de imagen médica
- Configuración de análisis genómico
- Settings de medicina personalizada
- Configuración de real-time processing
- Integration settings para AXIOM META 4
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from app.domains.registry import DomainInfo, DomainCategory


class MedicalImageModality(Enum):
    """Modalidades de imagen médica soportadas"""
    CT = "computed_tomography"
    MRI = "magnetic_resonance_imaging"
    XRAY = "x_ray"
    ULTRASOUND = "ultrasound"
    PET = "positron_emission_tomography"
    SPECT = "single_photon_emission_computed_tomography"
    MAMMOGRAPHY = "mammography"
    FLUOROSCOPY = "fluoroscopy"
    OCT = "optical_coherence_tomography"


class GenomicsAnalysisType(Enum):
    """Tipos de análisis genómico"""
    WGS = "whole_genome_sequencing"
    WES = "whole_exome_sequencing"
    TARGETED = "targeted_sequencing"
    RNA_SEQ = "rna_sequencing"
    CHIP_SEQ = "chip_sequencing"
    BISULFITE_SEQ = "bisulfite_sequencing"
    SINGLE_CELL = "single_cell_sequencing"


class ClinicalValidationLevel(Enum):
    """Niveles de validación clínica"""
    RESEARCH = "research_only"
    CLINICAL_TRIAL = "clinical_trial"
    FDA_CLEARED = "fda_cleared"
    CE_MARKED = "ce_marked"
    CLINICAL_USE = "clinical_use"


@dataclass
class MedicalImagingConfig:
    """Configuración de imaging médico"""
    # Configuración de calidad
    min_image_quality_score: float = 0.85
    max_noise_level: float = 0.15
    min_contrast_ratio: float = 2.0

    # DICOM Configuration
    dicom_transfer_syntax: str = "1.2.840.10008.1.2.1"  # Explicit VR Little Endian
    dicom_storage_commitment: bool = True
    dicom_compression_ratio: float = 10.0

    # Segmentation thresholds
    segmentation_confidence_threshold: float = 0.90
    min_segmentation_volume_ml: float = 0.1
    max_segmentation_overlap: float = 0.05

    # Modality-specific settings
    modality_settings: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        MedicalImageModality.CT.value: {
            "window_width": 400,
            "window_center": 40,
            "slice_thickness_mm": 1.0,
            "reconstruction_kernel": "B30f"
        },
        MedicalImageModality.MRI.value: {
            "te_ms": 80,
            "tr_ms": 3000,
            "flip_angle_degrees": 90,
            "matrix_size": [256, 256]
        },
        MedicalImageModality.XRAY.value: {
            "kvp": 120,
            "mas": 100,
            "filtration": "2.5mm_al_equivalent"
        }
    })

    # AI/ML Model settings
    ai_model_confidence_threshold: float = 0.95
    enable_gpu_acceleration: bool = True
    batch_size: int = 8
    max_image_size_mb: int = 500


@dataclass
class GenomicsConfig:
    """Configuración de análisis genómico"""
    # Variant calling thresholds
    min_base_quality: int = 20
    min_mapping_quality: int = 30
    min_coverage_depth: int = 10
    variant_quality_threshold: float = 30.0

    # DeepVariant settings
    deepvariant_model_type: str = "WGS"  # WGS, WES, PACBIO, HYBRID_PACBIO_ILLUMINA
    deepvariant_min_fraction_snps: float = 0.12
    deepvariant_min_fraction_indels: float = 0.06

    # Mutect2 (somatic variants) settings
    mutect2_tumor_lod_threshold: float = 6.3
    mutect2_normal_lod_threshold: float = 2.2
    mutect2_min_base_quality_score: int = 10

    # Structural variants
    sv_min_size_bp: int = 50
    sv_max_size_bp: int = 1000000
    sv_min_support_reads: int = 4

    # Pharmacogenomics
    pgx_star_allele_calling: bool = True
    pgx_copy_number_analysis: bool = True
    pgx_confidence_threshold: float = 0.95

    # Reference genomes
    default_reference_genome: str = "GRCh38"
    supported_references: List[str] = field(default_factory=lambda: [
        "GRCh38", "GRCh37", "T2T-CHM13"
    ])

    # Analysis types configuration
    analysis_settings: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        GenomicsAnalysisType.WGS.value: {
            "expected_coverage": 30,
            "analysis_duration_hours": 8,
            "memory_gb": 64
        },
        GenomicsAnalysisType.WES.value: {
            "expected_coverage": 100,
            "analysis_duration_hours": 4,
            "memory_gb": 32
        },
        GenomicsAnalysisType.RNA_SEQ.value: {
            "min_reads_million": 20,
            "analysis_duration_hours": 6,
            "memory_gb": 48
        }
    })


@dataclass
class PersonalizedMedicineConfig:
    """Configuración de medicina personalizada"""
    # Drug-gene interaction thresholds
    pgx_actionability_threshold: float = 0.90
    drug_interaction_severity_threshold: str = "moderate"

    # Clinical decision suppor
    recommendation_confidence_threshold: float = 0.85
    enable_clinical_alerts: bool = True
    max_concurrent_drug_analyses: int = 50

    # Pharmacokinetic modeling
    enable_pk_modeling: bool = True
    pk_simulation_iterations: int = 1000
    pk_confidence_interval: float = 0.95

    # Cancer genomics
    tumor_mutational_burden_threshold: float = 10.0  # mutations per Mb
    microsatellite_instability_threshold: float = 30.0
    homologous_recombination_deficiency_threshold: float = 42.0

    # Therapy matching
    therapy_evidence_levels: List[str] = field(default_factory=lambda: [
        "Level_1", "Level_2A", "Level_2B", "Level_3A", "Level_3B", "Level_4"
    ])
    clinical_trial_matching: bool = True

    # Precision oncology
    neoantigen_prediction: bool = True
    immune_infiltration_analysis: bool = True
    pathway_enrichment_analysis: bool = True


@dataclass
class BiomechanicsConfig:
    """Configuración de biomecánica"""
    # Motion analysis
    sampling_rate_hz: float = 1000.0
    motion_capture_precision_mm: float = 0.1
    force_measurement_precision_n: float = 0.5

    # Musculoskeletal modeling
    muscle_activation_threshold: float = 0.05
    joint_angle_precision_degrees: float = 0.1
    enable_muscle_force_estimation: bool = True

    # Gait analysis
    gait_cycle_detection_threshold: float = 0.8
    symmetry_index_threshold: float = 0.9
    enable_real_time_feedback: bool = True

    # Finite element analysis
    mesh_density: str = "medium"  # low, medium, high, ultra
    solver_tolerance: float = 1e-6
    max_iterations: int = 1000

    # Prosthetics and orthotics
    enable_prosthetic_design: bool = True
    orthotic_fitting_precision: float = 0.5  # mm
    material_property_database: bool = True


@dataclass
class RealTimeProcessingConfig:
    """Configuración de procesamiento en tiempo real"""
    # Stream processing
    max_concurrent_streams: int = 100
    stream_buffer_size: int = 10000
    stream_timeout_seconds: int = 300

    # Real-time thresholds
    max_processing_latency_ms: float = 100.0
    heartbeat_interval_seconds: int = 30
    enable_adaptive_quality: bool = True

    # Medical device integration
    enable_device_streaming: bool = True
    supported_protocols: List[str] = field(default_factory=lambda: [
        "HL7_FHIR", "DICOM_DIMSE", "IEEE_11073", "MQTT", "WebSocket"
    ])

    # Alert system
    enable_critical_alerts: bool = True
    alert_escalation_timeout_minutes: int = 5
    max_alert_queue_size: int = 1000


@dataclass
class ClinicalValidationConfig:
    """Configuración de validación clínica"""
    # Validation thresholds
    dice_coefficient_threshold: float = 0.85
    hausdorff_distance_threshold_mm: float = 5.0
    mean_surface_distance_threshold_mm: float = 2.0
    volume_difference_threshold_percent: float = 10.0

    # Clinical accuracy requirements
    sensitivity_threshold: float = 0.90
    specificity_threshold: float = 0.95
    positive_predictive_value_threshold: float = 0.85
    negative_predictive_value_threshold: float = 0.95

    # Regulatory compliance
    validation_level: ClinicalValidationLevel = ClinicalValidationLevel.CLINICAL_TRIAL
    enable_audit_logging: bool = True
    require_expert_review: bool = True

    # Quality assurance
    inter_observer_variability_threshold: float = 0.15
    intra_observer_variability_threshold: float = 0.10
    phantom_study_frequency_days: int = 30


@dataclass
class AxiomIntegrationConfig:
    """Configuración de integración con AXIOM META 4"""
    # Research automation
    enable_hypothesis_generation: bool = True
    auto_experiment_design: bool = True
    cross_domain_analysis: bool = True

    # Knowledge graph integration
    enable_medical_kg_updates: bool = True
    kg_confidence_threshold: float = 0.80
    max_kg_relations_per_analysis: int = 100

    # Meta-analysis capabilities
    enable_meta_analysis: bool = True
    min_studies_for_meta_analysis: int = 3
    heterogeneity_threshold: float = 0.75

    # Reproducibility tracking
    enable_full_provenance: bool = True
    automatic_method_documentation: bool = True
    result_reproducibility_validation: bool = True


# ====================================================================
# CONFIGURACIÓN PRINCIPAL DEL DOMINIO
# ====================================================================

DOMAIN_INFO = DomainInfo(
    name="medicine",
    category=DomainCategory.MEDICINE,
    description="Advanced medical computational services with AI/ML integration",
    version="3.0.0",
    dependencies=['mathematics', 'biology', 'chemistry', 'physics'],
    subdomains=['imaging', 'genomics', 'personalized', 'biomechanics'],
    enabled=True
)

# Configuraciones especializadas
MEDICAL_IMAGING_CONFIG = MedicalImagingConfig()
GENOMICS_CONFIG = GenomicsConfig()
PERSONALIZED_MEDICINE_CONFIG = PersonalizedMedicineConfig()
BIOMECHANICS_CONFIG = BiomechanicsConfig()
REAL_TIME_CONFIG = RealTimeProcessingConfig()
CLINICAL_VALIDATION_CONFIG = ClinicalValidationConfig()
AXIOM_INTEGRATION_CONFIG = AxiomIntegrationConfig()

# Configuración unificada del dominio
DOMAIN_SETTINGS = {
    # Core domain settings
    "max_concurrent_operations": 50,
    "cache_ttl_seconds": 7200,
    "enable_gpu_acceleration": True,
    "default_precision": "float64",
    "memory_limit_gb": 128,

    # Registry settings
    "registry_persistence_path": "data/medicine_registry_state.json",
    "max_concurrent_sessions": 100,
    "default_session_duration_hours": 24,
    "session_cleanup_interval_hours": 1,

    # Data storage
    "data_storage_path": Path("data/medicine/"),
    "temp_storage_path": Path("temp/medicine/"),
    "results_retention_days": 90,
    "enable_data_compression": True,

    # Security and compliance
    "enable_hipaa_compliance": True,
    "enable_gdpr_compliance": True,
    "encrypt_patient_data": True,
    "audit_log_retention_days": 2555,  # 7 years

    # Performance monitoring
    "enable_performance_monitoring": True,
    "metrics_collection_interval_seconds": 60,
    "performance_alert_thresholds": {
        "cpu_usage_percent": 80,
        "memory_usage_percent": 85,
        "disk_usage_percent": 90,
        "api_response_time_ms": 5000
    },

    # Integration settings
    "enable_external_apis": True,
    "api_rate_limits": {
        "genomics_apis": 100,  # requests per minute
        "imaging_apis": 50,
        "drug_databases": 200
    },

    # Specialized configurations
    "imaging": MEDICAL_IMAGING_CONFIG,
    "genomics": GENOMICS_CONFIG,
    "personalized": PERSONALIZED_MEDICINE_CONFIG,
    "biomechanics": BIOMECHANICS_CONFIG,
    "real_time": REAL_TIME_CONFIG,
    "validation": CLINICAL_VALIDATION_CONFIG,
    "axiom_integration": AXIOM_INTEGRATION_CONFIG
}

# Service endpoint configurations
SERVICE_ENDPOINTS = {
    "advanced_medical_imaging": {
        "endpoint": "/api/medicine/imaging",
        "timeout_seconds": 300,
        "max_request_size_mb": 500,
        "rate_limit_per_minute": 30
    },
    "genomics_analysis": {
        "endpoint": "/api/medicine/genomics",
        "timeout_seconds": 28800,  # 8 hours for WGS
        "max_request_size_mb": 10000,  # 10GB for large genomic files
        "rate_limit_per_minute": 5
    },
    "personalized_medicine": {
        "endpoint": "/api/medicine/personalized",
        "timeout_seconds": 600,
        "max_request_size_mb": 100,
        "rate_limit_per_minute": 20
    },
    "biomechanics_modeling": {
        "endpoint": "/api/medicine/biomechanics",
        "timeout_seconds": 1800,
        "max_request_size_mb": 200,
        "rate_limit_per_minute": 10
    }
}

# Clinical standards and compliance
CLINICAL_STANDARDS = {
    "dicom": {
        "version": "3.0",
        "conformance_statement": True,
        "supported_sop_classes": [
            "1.2.840.10008.5.1.4.1.1.2",    # CT Image Storage
            "1.2.840.10008.5.1.4.1.1.4",    # MR Image Storage
            "1.2.840.10008.5.1.4.1.1.12.1", # X-Ray Angiographic Image Storage
        ]
    },
    "hl7_fhir": {
        "version": "R4",
        "supported_resources": ["Patient", "Observation", "DiagnosticReport", "Medication"]
    },
    "snomed_ct": {
        "version": "International_20240301",
        "enable_terminology_validation": True
    },
    "loinc": {
        "version": "2.78",
        "enable_lab_code_validation": True
    }
}

# Error handling and logging
ERROR_HANDLING = {
    "max_retry_attempts": 3,
    "retry_backoff_factor": 2.0,
    "timeout_grace_period_seconds": 30,
    "enable_detailed_error_logging": True,
    "error_notification_channels": ["email", "slack", "dashboard"]
}

# Development and testing settings
DEVELOPMENT_SETTINGS = {
    "enable_debug_mode": False,
    "enable_test_data_generation": True,
    "mock_external_services": False,
    "enable_performance_profiling": True,
    "test_data_retention_days": 7
}
