"""
Domain Registry
===============

Registro y gestión de dominios científicos para el sistema AXIOM.

Author: AXIOM Team
Date: 2025-09-23
Version: 1.0.0
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


class DomainCategory(Enum):
    """Categorías de dominios científicos."""
    MATHEMATICS = "mathematics"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"
    MEDICINE = "medicine"
    ENGINEERING = "engineering"
    ASTRONOMY = "astronomy"
    NEUROSCIENCE = "neuroscience"
    COMPUTER_SCIENCE = "computer_science"
    INTERDISCIPLINARY = "interdisciplinary"


@dataclass
class DomainInfo:
    """Información de un dominio científico."""
    name: str
    category: DomainCategory
    description: str
    version: str
    dependencies: List[str] = None
    subdomains: List[str] = None
    enabled: bool = True
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.subdomains is None:
            self.subdomains = []
        if self.metadata is None:
            self.metadata = {}


class DomainRegistry:
    """Registro centralizado de dominios científicos."""

    def __init__(self):
        self._domains: Dict[str, DomainInfo] = {}

    def register_domain(self, domain_info: DomainInfo) -> None:
        """Registrar un dominio."""
        self._domains[domain_info.name] = domain_info

    def get_domain(self, name: str) -> Optional[DomainInfo]:
        """Obtener información de un dominio."""
        return self._domains.get(name)

    def list_domains(self) -> List[DomainInfo]:
        """Listar todos los dominios registrados."""
        return list(self._domains.values())

    def get_domains_by_category(self, category: DomainCategory) -> List[DomainInfo]:
        """Obtener dominios por categoría."""
        return [domain for domain in self._domains.values() 
                if domain.category == category]

    def is_domain_enabled(self, name: str) -> bool:
        """Verificar si un dominio está habilitado."""
        domain = self.get_domain(name)
        return domain.enabled if domain else False


# Instancia global del registro
_registry = DomainRegistry()


def get_registry() -> DomainRegistry:
    """Obtener la instancia del registro de dominios."""
    return _registry
