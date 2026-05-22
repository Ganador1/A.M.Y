"""
Configuración del dominio Astronomy
"""

from app.domains.registry import DomainInfo, DomainCategory

DOMAIN_INFO = DomainInfo(
    name="astronomy",
    category=DomainCategory.ASTRONOMY,
    description="Astronomical data analysis and computational astrophysics services",
    version="1.1.0",
    dependencies=['mathematics', 'physics'],
    subdomains=['observational', 'theoretical', 'computational'],
    enabled=True,
    metadata={
        "capabilities": [
            "telescope_data_analysis",
            "astronomical_simulation",
            "advanced_exoplanet_detection",
            "galaxy_morphology",
            "cosmology_inference",
            "star_formation_characterization",
        ],
        "ml_ready": True,
        "default_facade": "AstronomicalAnalysisFacade",
    }
)

# Configuración específica del dominio
DOMAIN_SETTINGS = {
    "max_telescope_data_size": 1000000,  # puntos de datos máximo
    "supported_telescopes": ["HST", "JWST", "ALMA", "VLA", "Chandra"],
    "default_coordinate_system": "ICRS",
    "max_simulation_time": 3600,  # segundos
    "cache_ttl": 3600,
    "enable_gpu_acceleration": False,
    "default_precision": "float64",
    "default_analysis_timeout_s": 30,
    "quality_metrics_enabled": True,
}

