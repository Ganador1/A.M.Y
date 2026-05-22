"""
Clases de datos y tipos para el servicio de biomecánica
======================================================

Definiciones de tipos y estructuras de datos para análisis biomecánico.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Tuple
from enum import Enum
import numpy as np
from datetime import datetime


class ActivityType(Enum):
    """Tipos de actividades analizables"""
    WALKING = "walking"
    RUNNING = "running"
    JUMPING = "jumping"
    CYCLING = "cycling"
    SWIMMING = "swimming"
    SQUATTING = "squatting"
    STAIRS_ASCENDING = "stairs_ascending"
    STAIRS_DESCENDING = "stairs_descending"
    BALANCE_STANDING = "balance_standing"
    CUSTOM = "custom"


class GaitPhase(Enum):
    """Fases de la marcha"""
    HEEL_STRIKE = "heel_strike"
    LOADING_RESPONSE = "loading_response"
    MID_STANCE = "mid_stance"
    TERMINAL_STANCE = "terminal_stance"
    PRE_SWING = "pre_swing"
    INITIAL_SWING = "initial_swing"
    MID_SWING = "mid_swing"
    TERMINAL_SWING = "terminal_swing"


class JointType(Enum):
    """Tipos de articulaciones"""
    HIP = "hip"
    KNEE = "knee"
    ANKLE = "ankle"
    SHOULDER = "shoulder"
    ELBOW = "elbow"
    WRIST = "wrist"
    SPINE = "spine"
    PELVIS = "pelvis"


class AnalysisType(Enum):
    """Tipos de análisis biomecánico"""
    GAIT_ANALYSIS = "gait_analysis"
    JOINT_KINEMATICS = "joint_kinematics"
    FORCE_ANALYSIS = "force_analysis"
    MUSCLE_ACTIVATION = "muscle_activation"
    BALANCE_ASSESSMENT = "balance_assessment"
    INJURY_RISK = "injury_risk"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    REAL_TIME_FEEDBACK = "real_time_feedback"


@dataclass
class MotionCaptureData:
    """Datos de captura de movimiento"""
    timestamp: datetime
    markers: Dict[str, np.ndarray]  # marker_name -> [time_points, 3] positions
    sampling_rate: int
    subject_id: str
    activity: ActivityType
    duration_seconds: float = 0.0
    marker_labels: List[str] = field(default_factory=list)
    coordinate_system: str = "right_handed_xyz"
    
    def __post_init__(self):
        """Post-procesamiento después de inicialización"""
        if not self.marker_labels:
            self.marker_labels = list(self.markers.keys())
        if self.duration_seconds == 0.0:
            # Calcular duración basada en datos
            if self.markers:
                first_marker = next(iter(self.markers.values()))
                self.duration_seconds = len(first_marker) / self.sampling_rate


@dataclass
class ForceData:
    """Datos de placa de fuerza"""
    force_vectors: Dict[str, np.ndarray]  # Fx, Fy, Fz
    moments: Dict[str, np.ndarray]  # Mx, My, Mz
    center_of_pressure: Dict[str, np.ndarray]  # CoPx, CoPy
    sampling_rate: int
    subject_mass_kg: float
    plate_dimensions: Tuple[float, float] = (0.4, 0.6)  # width, length in meters
    units: Dict[str, str] = field(default_factory=lambda: {
        "force": "N", "moment": "Nm", "cop": "m"
    })


@dataclass
class EMGData:
    """Datos de electromiografía (EMG)"""
    muscle_signals: Dict[str, np.ndarray]  # muscle_name -> signal
    sampling_rate: int
    subject_id: str
    electrode_placement: Dict[str, str]  # muscle_name -> placement_description
    processing_applied: List[str] = field(default_factory=list)  # filters, rectification, etc.
    baseline_period_seconds: float = 2.0


@dataclass 
class AnthropometricData:
    """Datos antropométricos del sujeto"""
    subject_id: str
    height_m: float
    mass_kg: float
    gender: str
    age_years: int
    
    # Medidas segmentales (opcional)
    leg_length_m: Optional[float] = None
    thigh_length_m: Optional[float] = None
    shank_length_m: Optional[float] = None
    foot_length_m: Optional[float] = None
    arm_span_m: Optional[float] = None
    
    # Medidas de composición corporal (opcional)
    body_fat_percent: Optional[float] = None
    muscle_mass_kg: Optional[float] = None
    bone_density: Optional[float] = None


@dataclass
class GaitAnalysisResult:
    """Resultado de análisis de marcha"""
    subject_id: str
    
    # Parámetros temporales
    temporal_parameters: Dict[str, float] = field(default_factory=dict)
    
    # Parámetros espaciales
    spatial_parameters: Dict[str, float] = field(default_factory=dict)
    
    # Ángulos articulares
    joint_angles: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Índices de asimetría
    asymmetry_indices: Dict[str, float] = field(default_factory=dict)
    
    # Variabilidad
    variability_metrics: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Inicializar valores por defecto"""
        if not self.temporal_parameters:
            self.temporal_parameters = {
                "stride_length_m": 0.0,
                "step_length_m": 0.0,
                "cadence_steps_per_min": 0.0,
                "walking_speed_ms": 0.0,
                "stance_phase_percent": 0.0,
                "swing_phase_percent": 0.0,
                "double_support_percent": 0.0
            }


@dataclass
class JointKinematics:
    """Cinemática articular"""
    joint: JointType
    angles: Dict[str, np.ndarray]  # flexion_extension, abduction_adduction, etc.
    angular_velocities: Dict[str, np.ndarray]
    angular_accelerations: Dict[str, np.ndarray]
    range_of_motion: Dict[str, float]
    peak_values: Dict[str, Dict[str, float]]  # peak_flexion, peak_extension, etc.


@dataclass
class ForceAnalysis:
    """Resultado de análisis de fuerzas"""
    subject_id: str
    
    # Fuerzas pico
    peak_forces: Dict[str, float] = field(default_factory=dict)
    
    # Tasas de carga
    loading_rates: Dict[str, float] = field(default_factory=dict)
    
    # Impulso
    impulse_parameters: Dict[str, float] = field(default_factory=dict)
    
    # Centro de presión
    center_of_pressure_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class MusculoskeletalModel:
    """Modelo musculoesquelético"""
    subject_id: str
    anthropometrics: AnthropometricData
    
    # Fuerzas musculares
    muscle_forces: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Momentos articulares
    joint_moments: Dict[str, float] = field(default_factory=dict)
    
    # Potencia articular
    joint_powers: Dict[str, float] = field(default_factory=dict)
    
    # Activaciones musculares predichas
    muscle_activations: Dict[str, float] = field(default_factory=dict)


@dataclass
class MovementPattern:
    """Patrón de movimiento detectado"""
    pattern_name: str
    start_frame: int
    end_frame: int
    confidence: float
    characteristics: Dict[str, Any] = field(default_factory=dict)
    frequency: float = 0.0  # Hz
    amplitude: float = 0.0
    phase_offset: float = 0.0


@dataclass
class InjuryRiskAssessment:
    """Evaluación de riesgo de lesiones"""
    subject_id: str
    overall_risk_score: float  # 0-1 scale
    
    risk_factors: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Recomendaciones específicas
    recommendations: List[str] = field(default_factory=list)
    
    # Áreas de preocupación
    concern_areas: List[str] = field(default_factory=list)
    
    # Seguimiento recomendado
    follow_up_timeline: str = "3_months"


@dataclass
class PerformanceMetrics:
    """Métricas de rendimiento deportivo"""
    subject_id: str
    sport_specific_metrics: Dict[str, float] = field(default_factory=dict)
    efficiency_metrics: Dict[str, float] = field(default_factory=dict)
    technique_scores: Dict[str, float] = field(default_factory=dict)
    improvement_areas: List[str] = field(default_factory=list)
    training_recommendations: List[str] = field(default_factory=list)


@dataclass
class BiomechanicsAnalysisRequest:
    """Solicitud de análisis biomecánico"""
    subject_id: str
    analysis_type: AnalysisType
    motion_data: Optional[MotionCaptureData] = None
    force_data: Optional[ForceData] = None
    emg_data: Optional[EMGData] = None
    anthropometric_data: Optional[AnthropometricData] = None
    
    # Parámetros del análisis
    filtering_enabled: bool = True
    cutoff_frequency: float = 6.0  # Hz for lowpass filter
    normalize_to_body_weight: bool = True
    compare_to_normative_data: bool = False
    
    # Opciones específicas
    analysis_options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BiomechanicsAnalysisResult:
    """Resultado comprehensivo de análisis biomecánico"""
    request: BiomechanicsAnalysisRequest
    analysis_timestamp: datetime
    processing_time_seconds: float
    
    # Resultados específicos según el tipo de análisis
    gait_analysis: Optional[GaitAnalysisResult] = None
    joint_kinematics: Optional[Dict[str, JointKinematics]] = None
    force_analysis: Optional[ForceAnalysis] = None
    musculoskeletal_model: Optional[MusculoskeletalModel] = None
    injury_risk: Optional[InjuryRiskAssessment] = None
    performance_metrics: Optional[PerformanceMetrics] = None
    movement_patterns: Optional[List[MovementPattern]] = None
    
    # Metadata del análisis
    quality_assessment: Dict[str, float] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


# Constantes de referencia para análisis
NORMATIVE_GAIT_DATA = {
    "healthy_adult": {
        "walking_speed_ms": {"mean": 1.3, "std": 0.2},
        "cadence_steps_per_min": {"mean": 110, "std": 10},
        "stride_length_m": {"mean": 1.4, "std": 0.15},
        "stance_phase_percent": {"mean": 60, "std": 3},
        "swing_phase_percent": {"mean": 40, "std": 3}
    },
    "elderly": {
        "walking_speed_ms": {"mean": 1.0, "std": 0.25},
        "cadence_steps_per_min": {"mean": 100, "std": 12},
        "stride_length_m": {"mean": 1.2, "std": 0.18}
    }
}

INJURY_RISK_THRESHOLDS = {
    "loading_rate_bw_per_s": 75,  # body weights per second
    "peak_vertical_force_bw": 2.5,  # body weights
    "asymmetry_index_percent": 10,  # percentage
    "ankle_stiffness_nm_per_rad": 0.15,
    "knee_adduction_moment_nm_per_kg": 0.5
}

MUSCLE_GROUPS = {
    "hip_extensors": ["gluteus_maximus", "hamstrings", "adductor_magnus"],
    "hip_flexors": ["iliopsoas", "rectus_femoris", "sartorius"],
    "knee_extensors": ["quadriceps", "vastus_lateralis", "vastus_medialis", "rectus_femoris"],
    "knee_flexors": ["hamstrings", "biceps_femoris", "semitendinosus"],
    "ankle_plantarflexors": ["gastrocnemius", "soleus", "tibialis_posterior"],
    "ankle_dorsiflexors": ["tibialis_anterior", "extensor_digitorum_longus"]
}
