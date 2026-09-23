"""
Configuración del dominio Physics
"""

from app.domains.registry import DomainInfo, DomainCategory

DOMAIN_INFO = DomainInfo(
    name="physics",
    category=DomainCategory.PHYSICS,
    description="Physics simulation and computational services",
    version="2.0.0",
    dependencies=['mathematics'],
    subdomains=['classical', 'quantum', 'plasma', 'computational'],
    enabled=True
)

# Configuración específica del dominio
DOMAIN_SETTINGS = {
    "max_concurrent_operations": 10,
    "cache_ttl": 3600,
    "enable_gpu_acceleration": True,
    "default_precision": "float64"
}
