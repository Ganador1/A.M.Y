"""
Neuroscience Domain Configuration
=================================

Configuración del dominio Neuroscience para el sistema AXIOM.

Author: AXIOM Team
Date: 2025-09-23
Version: 1.0.0
"""

from app.domains.registry import DomainInfo, DomainCategory

DOMAIN_INFO = DomainInfo(
    name="neuroscience",
    category=DomainCategory.NEUROSCIENCE,
    description="Advanced neuroscience analysis with neuroimaging, BCI, and modeling capabilities",
    version="1.0.0",
    dependencies=['mathematics', 'physics', 'biology', 'medicine'],
    subdomains=['neuroimaging', 'bci', 'modeling', 'neuromorphic'],
    enabled=True
)

# Configuración específica del dominio
DOMAIN_SETTINGS = {
    "max_concurrent_sessions": 50,
    "cache_ttl": 7200,
    "enable_gpu_acceleration": True,
    "default_precision": "float32",
    "max_data_size": "1GB",
    "streaming_buffer_size": 1000,
    "real_time_processing": True,
    "supported_modalities": [
        "fMRI", "EEG", "MEG", "DTI", "PET", "SPECT", "sMRI", "fNIRS"
    ],
    "default_sampling_rate": 250.0,
    "connectivity_methods": [
        "correlation", "coherence", "mutual_information", "granger_causality"
    ],
    "pattern_detection": {
        "oscillation_bands": {
            "delta": [0.5, 4],
            "theta": [4, 8],
            "alpha": [8, 13],
            "beta": [13, 30],
            "gamma": [30, 100]
        },
        "anomaly_threshold": 2.5,
        "confidence_threshold": 0.8
    }
}
