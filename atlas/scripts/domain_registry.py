"""
Sistema de Registro de Dominios Científicos para ATLAS/AXIOM
Permite auto-descubrimiento y gestión centralizada de dominios
"""

from typing import Dict, List, Optional, Type
from dataclasses import dataclass, field
from enum import Enum
import importlib
from pathlib import Path


class DomainCategory(Enum):
    """Categorías principales de dominios científicos"""
    MATHEMATICS = "mathematics"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"
    MEDICINE = "medicine"
    EARTH_SCIENCES = "earth_sciences"
    ASTRONOMY = "astronomy"
    NEUROSCIENCE = "neuroscience"
    ENGINEERING = "engineering"
    INTERDISCIPLINARY = "interdisciplinary"


@dataclass
class DomainInfo:
    """Información de un dominio científico"""
    name: str
    category: DomainCategory
    description: str
    version: str = "1.0.0"
    dependencies: List[str] = field(default_factory=list)
    subdomains: List[str] = field(default_factory=list)
    services: List[str] = field(default_factory=list)
    routers: List[str] = field(default_factory=list)
    models: List[str] = field(default_factory=list)
    enabled: bool = True


class DomainRegistry:
    """Registro centralizado de dominios científicos"""
    
    def __init__(self):
        self._domains: Dict[str, DomainInfo] = {}
        self._load_domains()
    
    def _load_domains(self):
        """Carga automática de dominios desde el sistema de archivos"""
        domains_path = Path(__file__).parent / "domains"
        
        if not domains_path.exists():
            return
        
        for domain_path in domains_path.iterdir():
            if domain_path.is_dir() and not domain_path.name.startswith("_"):
                self._discover_domain(domain_path)
    
    def _discover_domain(self, domain_path: Path):
        """Descubre y registra un dominio automáticamente"""
        domain_name = domain_path.name
        
        # Buscar archivo de configuración del dominio
        config_file = domain_path / "domain_config.py"
        if config_file.exists():
            self._load_domain_config(domain_name, config_file)
        else:
            self._auto_discover_domain(domain_name, domain_path)
    
    def _load_domain_config(self, domain_name: str, config_file: Path):
        """Carga configuración explícita del dominio"""
        try:
            spec = importlib.util.spec_from_file_location("domain_config", config_file)
            config = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config)
            
            domain_info = getattr(config, "DOMAIN_INFO", None)
            if domain_info:
                self._domains[domain_name] = domain_info
        except Exception as e:
            print(f"Error loading domain config for {domain_name}: {e}")
            self._auto_discover_domain(domain_name, config_file.parent)
    
    def _auto_discover_domain(self, domain_name: str, domain_path: Path):
        """Auto-descubrimiento de dominio basado en estructura de archivos"""
        # Determinar categoría basada en el nombre
        category = self._infer_category(domain_name)
        
        # Descubrir componentes
        subdomains = self._discover_subdomains(domain_path)
        services = self._discover_services(domain_path)
        routers = self._discover_routers(domain_path)
        models = self._discover_models(domain_path)
        
        domain_info = DomainInfo(
            name=domain_name,
            category=category,
            description=f"Auto-discovered domain: {domain_name}",
            subdomains=subdomains,
            services=services,
            routers=routers,
            models=models
        )
        
        self._domains[domain_name] = domain_info
    
    def _infer_category(self, domain_name: str) -> DomainCategory:
        """Infiere la categoría del dominio basado en su nombre"""
        category_mapping = {
            "mathematics": DomainCategory.MATHEMATICS,
            "math": DomainCategory.MATHEMATICS,
            "physics": DomainCategory.PHYSICS,
            "quantum": DomainCategory.PHYSICS,
            "chemistry": DomainCategory.CHEMISTRY,
            "biology": DomainCategory.BIOLOGY,
            "bio": DomainCategory.BIOLOGY,
            "medicine": DomainCategory.MEDICINE,
            "medical": DomainCategory.MEDICINE,
            "earth": DomainCategory.EARTH_SCIENCES,
            "geo": DomainCategory.EARTH_SCIENCES,
            "astronomy": DomainCategory.ASTRONOMY,
            "astro": DomainCategory.ASTRONOMY,
            "neuroscience": DomainCategory.NEUROSCIENCE,
            "neuro": DomainCategory.NEUROSCIENCE,
            "engineering": DomainCategory.ENGINEERING
        }
        
        for key, category in category_mapping.items():
            if key in domain_name.lower():
                return category
        
        return DomainCategory.INTERDISCIPLINARY
    
    def _discover_subdomains(self, domain_path: Path) -> List[str]:
        """Descubre subdominios en la estructura de carpetas"""
        subdomains = []
        for item in domain_path.iterdir():
            if item.is_dir() and not item.name.startswith("_"):
                subdomains.append(item.name)
        return subdomains
    
    def _discover_services(self, domain_path: Path) -> List[str]:
        """Descubre servicios en el dominio"""
        services_path = domain_path / "services"
        if not services_path.exists():
            return []
        
        services = []
        for service_file in services_path.glob("*.py"):
            if not service_file.name.startswith("_"):
                services.append(service_file.stem)
        return services
    
    def _discover_routers(self, domain_path: Path) -> List[str]:
        """Descubre routers en el dominio"""
        routers_path = domain_path / "routers"
        if not routers_path.exists():
            return []
        
        routers = []
        for router_file in routers_path.glob("*.py"):
            if not router_file.name.startswith("_"):
                routers.append(router_file.stem)
        return routers
    
    def _discover_models(self, domain_path: Path) -> List[str]:
        """Descubre modelos en el dominio"""
        models_path = domain_path / "models"
        if not models_path.exists():
            return []
        
        models = []
        for model_file in models_path.glob("*.py"):
            if not model_file.name.startswith("_"):
                models.append(model_file.stem)
        return models
    
    def register_domain(self, domain_info: DomainInfo):
        """Registra un dominio manualmente"""
        self._domains[domain_info.name] = domain_info
    
    def get_domain(self, name: str) -> Optional[DomainInfo]:
        """Obtiene información de un dominio"""
        return self._domains.get(name)
    
    def get_domains_by_category(self, category: DomainCategory) -> List[DomainInfo]:
        """Obtiene todos los dominios de una categoría"""
        return [domain for domain in self._domains.values() 
                if domain.category == category and domain.enabled]
    
    def get_all_domains(self) -> Dict[str, DomainInfo]:
        """Obtiene todos los dominios registrados"""
        return self._domains.copy()
    
    def enable_domain(self, name: str):
        """Habilita un dominio"""
        if name in self._domains:
            self._domains[name].enabled = True
    
    def disable_domain(self, name: str):
        """Deshabilita un dominio"""
        if name in self._domains:
            self._domains[name].enabled = False
    
    def get_domain_dependencies(self, name: str) -> List[str]:
        """Obtiene las dependencias de un dominio"""
        domain = self.get_domain(name)
        return domain.dependencies if domain else []
    
    def validate_dependencies(self) -> Dict[str, List[str]]:
        """Valida que todas las dependencias estén disponibles"""
        missing_deps = {}
        
        for domain_name, domain_info in self._domains.items():
            missing = []
            for dep in domain_info.dependencies:
                if dep not in self._domains or not self._domains[dep].enabled:
                    missing.append(dep)
            
            if missing:
                missing_deps[domain_name] = missing
        
        return missing_deps
    
    def get_domain_tree(self) -> Dict:
        """Genera un árbol jerárquico de dominios por categoría"""
        tree = {}
        
        for category in DomainCategory:
            domains = self.get_domains_by_category(category)
            if domains:
                tree[category.value] = {}
                for domain in domains:
                    tree[category.value][domain.name] = {
                        "description": domain.description,
                        "subdomains": domain.subdomains,
                        "services": len(domain.services),
                        "routers": len(domain.routers),
                        "models": len(domain.models)
                    }
        
        return tree


# Instancia global del registro
domain_registry = DomainRegistry()


def get_available_domains() -> List[str]:
    """Función de conveniencia para obtener dominios disponibles"""
    return [name for name, domain in domain_registry.get_all_domains().items() 
            if domain.enabled]


def get_domain_info(name: str) -> Optional[DomainInfo]:
    """Función de conveniencia para obtener información de dominio"""
    return domain_registry.get_domain(name)


# Ejemplo de configuración de dominio
MATHEMATICS_DOMAIN = DomainInfo(
    name="mathematics",
    category=DomainCategory.MATHEMATICS,
    description="Mathematical computational services and algorithms",
    version="2.0.0",
    dependencies=[],
    subdomains=["pure", "applied", "computational", "topology"],
    services=["computation", "analysis", "visualization"],
    routers=["api"],
    models=["requests", "responses"]
)