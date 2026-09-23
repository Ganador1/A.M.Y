"""
Configuración del dominio Mathematics
"""

from app.domains.registry import DomainInfo, DomainCategory

DOMAIN_INFO = DomainInfo(
    name="mathematics",
    category=DomainCategory.MATHEMATICS,
    description="Mathematical computational services and algorithms",
    version="2.0.0",
    dependencies=[],
    subdomains=['pure', 'applied', 'computational', 'topology'],
    enabled=True
)

# Configuración específica del dominio
DOMAIN_SETTINGS = {
    "max_concurrent_operations": 10,
    "cache_ttl": 3600,
    "enable_gpu_acceleration": True,
    "default_precision": "float64"
}
