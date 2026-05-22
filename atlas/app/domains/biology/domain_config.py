"""
Configuración del dominio Biology
"""

from app.domains.registry import DomainInfo, DomainCategory

DOMAIN_INFO = DomainInfo(
    name="biology",
    category=DomainCategory.BIOLOGY,
    description="Biology computational and molecular services",
    version="2.0.0",
    dependencies=['mathematics', 'chemistry'],
    subdomains=['computational', 'molecular', 'genomics', 'biophysics'],
    enabled=True
)

# Configuración específica del dominio
DOMAIN_SETTINGS = {
    "max_concurrent_operations": 10,
    "cache_ttl": 3600,
    "enable_gpu_acceleration": True,
    "default_precision": "float64"
}
