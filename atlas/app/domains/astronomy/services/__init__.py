"""
AXIOM Astronomy - Servicios de Análisis Astronómico
===================================================

Este módulo contiene todos los servicios especializados para análisis astronómico,
organizados por fases de desarrollo según el roadmap AXIOM.

Servicios Disponibles:
- Fase 1 (Fundación): Servicios básicos de análisis astronómico
- Fase 2 (Expansión): Servicios avanzados multi-dominio
- Fase 3 (Machine Learning): Servicios de IA y detección automática
- Fase 4 (Integración): Pipeline unificado de análisis

Autor: AXIOM Development Team
Fecha: Octubre 2025
Versión: 1.0.0
"""

# Fase 1: Servicios de Fundación
from .lightkurve_advanced_service import LightkurveAdvancedService
from .astropy_precision_service import AstropyPrecisionService
from .stellar_variability_service import StellarVariabilityService

# Fase 2: Servicios de Expansión
from .optimal_aperture_photometry_service import OptimalAperturePhotometryService
from .binary_system_analysis_service import BinarySystemAnalysisService
from .exoplanet_transit_analysis_service import ExoplanetTransitAnalysisService
from .advanced_statistics_service import AdvancedStatisticsService
from .multiwavelength_analysis_service import MultiWavelengthAnalysisService

# Fase 3: Servicios de Machine Learning
from .astrometric_analysis_service import AstrometricAnalysisService
from .astronomical_ml_service import AstronomicalMLService

# Fase 4: Servicios de Integración
from .integrated_astronomy_pipeline import IntegratedAstronomyPipeline
from .advanced_astronomy_workflow import AdvancedAstronomyWorkflow

# Create main astronomy service instance
from .orchestrator import AstronomyDomainOrchestrator
astronomy_service = AstronomyDomainOrchestrator()

__all__ = [
    # Fase 1
    "LightkurveAdvancedService",
    "AstropyPrecisionService", 
    "StellarVariabilityService",
    
    # Fase 2
    "OptimalAperturePhotometryService",
    "BinarySystemAnalysisService",
    "ExoplanetTransitAnalysisService",
    "AdvancedStatisticsService",
    "MultiWavelengthAnalysisService",
    
    # Fase 3
    "AstrometricAnalysisService",
    "AstronomicalMLService",
    
    # Fase 4
    "IntegratedAstronomyPipeline",
    "AdvancedAstronomyWorkflow",
    
    # Main service instance
    "astronomy_service",
]
