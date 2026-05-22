"""
Dominio Astronomy - Análisis de datos astronómicos y astrofísica computacional

Este dominio proporciona servicios para:
- Análisis de datos telescópicos
- Simulaciones astronómicas
- Detección de exoplanetas
- Análisis de galaxias
- Estudios cosmológicos
- Análisis de formación estelar
"""

from .domain_config import DOMAIN_INFO, DOMAIN_SETTINGS

__version__ = DOMAIN_INFO.version
__description__ = DOMAIN_INFO.description

__all__ = [
    'DOMAIN_INFO',
    'DOMAIN_SETTINGS'
]






