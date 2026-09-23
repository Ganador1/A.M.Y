"""
Biomechanics Module - Análisis biomecánico comprehensivo
======================================================

Módulo para análisis de movimiento, marcha, fuerzas y evaluación de riesgo de lesiones.
"""

from .biomechanics_types import (
    # Enums
    ActivityType, GaitPhase, JointType, AnalysisType,
    
    # Clases de datos
    MotionCaptureData, ForceData, EMGData, AnthropometricData,
    GaitAnalysisResult, JointKinematics, ForceAnalysis,
    MusculoskeletalModel, MovementPattern, InjuryRiskAssessment,
    PerformanceMetrics, BiomechanicsAnalysisRequest, BiomechanicsAnalysisResult,
    
    # Constantes
    NORMATIVE_GAIT_DATA, INJURY_RISK_THRESHOLDS, MUSCLE_GROUPS
)

from .biomechanical_models import BiomechanicsService, biomechanical_model

__all__ = [
    # Service
    "BiomechanicsService",
    "biomechanical_model",
    
    # Enums
    "ActivityType",
    "GaitPhase", 
    "JointType",
    "AnalysisType",
    
    # Data classes
    "MotionCaptureData",
    "ForceData",
    "EMGData",
    "AnthropometricData",
    "GaitAnalysisResult",
    "JointKinematics",
    "ForceAnalysis",
    "MusculoskeletalModel",
    "MovementPattern",
    "InjuryRiskAssessment",
    "PerformanceMetrics",
    "BiomechanicsAnalysisRequest",
    "BiomechanicsAnalysisResult",
    
    # Constants
    "NORMATIVE_GAIT_DATA",
    "INJURY_RISK_THRESHOLDS",
    "MUSCLE_GROUPS"
]