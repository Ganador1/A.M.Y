"""
Configuración del dominio Chemistry
"""

from app.domains.registry import DomainInfo, DomainCategory

DOMAIN_INFO = DomainInfo(
    name="chemistry",
    category=DomainCategory.CHEMISTRY,
    description="Chemistry computational and analytical services",
    version="2.0.0",
    dependencies=['mathematics', 'physics'],
    subdomains=['computational', 'analytical', 'materials', 'crystallography'],
    enabled=True
)

# Configuración específica del dominio
DOMAIN_SETTINGS = {
    "max_concurrent_operations": 10,
    "cache_ttl": 3600,
    "enable_gpu_acceleration": True,
    "default_precision": "float64"
}
