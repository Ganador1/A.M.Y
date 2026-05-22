"""
Service Locator for AXIOM ATLAS Scientific Domains
===================================================

Provides a unified interface for discovering and instantiating domain services.
Supports lazy loading, dependency injection, and configuration-driven service resolution.

Usage:
    from app.domains.service_locator import ServiceLocator
    
    locator = ServiceLocator.get_instance()
    
    # Get service by name
    chemistry_service = locator.get_service("ComputationalChemistryService")
    
    # Get all services for a domain
    bio_services = locator.get_domain_services("biology")
    
    # Get service with custom config
    genomics = locator.get_service("GenomicsService", config={"reference": "GRCh37"})

Design Principles:
    1. Lazy Loading: Services are only instantiated when first requested
    2. Singleton by default: Same instance returned for same service name
    3. Configuration injection: Pass config dicts to customize services
    4. Domain grouping: Services are organized by scientific domain
    5. BaseService enforcement: Only services inheriting from BaseService are registered
"""

from __future__ import annotations

import importlib
import threading
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

from app.core.bootstrap_logging import logger
from app.services.base_service import BaseService

T = TypeVar("T", bound=BaseService)


@dataclass
class ServiceDefinition:
    """Metadata about a registered service."""
    
    name: str
    domain: str
    module_path: str
    class_name: str
    factory: Optional[Callable[..., BaseService]] = None
    singleton: bool = True
    tags: List[str] = field(default_factory=list)
    description: str = ""
    
    def __hash__(self) -> int:
        return hash((self.name, self.domain, self.module_path))


class ServiceLocator:
    """
    Centralized service discovery and instantiation for AXIOM ATLAS.
    
    Thread-safe singleton implementation with lazy service loading.
    """
    
    _instance: Optional["ServiceLocator"] = None
    _lock = threading.Lock()
    
    def __init__(self) -> None:
        self._definitions: Dict[str, ServiceDefinition] = {}
        self._instances: Dict[str, BaseService] = {}
        self._domain_index: Dict[str, List[str]] = {}
        self._initialized = False
        logger.debug("ServiceLocator created")
    
    @classmethod
    def get_instance(cls) -> "ServiceLocator":
        """Get or create the singleton ServiceLocator instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    cls._instance._register_default_services()
        return cls._instance
    
    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (for testing)."""
        with cls._lock:
            if cls._instance is not None:
                cls._instance._instances.clear()
                cls._instance._definitions.clear()
                cls._instance._domain_index.clear()
            cls._instance = None
    
    def register(
        self,
        name: str,
        domain: str,
        module_path: str,
        class_name: str,
        *,
        factory: Optional[Callable[..., BaseService]] = None,
        singleton: bool = True,
        tags: Optional[List[str]] = None,
        description: str = "",
    ) -> None:
        """
        Register a service definition.
        
        Args:
            name: Unique service identifier
            domain: Scientific domain (biology, chemistry, physics, etc.)
            module_path: Full module path (e.g., "app.domains.chemistry.services.computational_chemistry")
            class_name: Class name within the module
            factory: Optional factory function for custom instantiation
            singleton: If True, same instance is returned for subsequent calls
            tags: Optional tags for service discovery
            description: Human-readable description
        """
        definition = ServiceDefinition(
            name=name,
            domain=domain,
            module_path=module_path,
            class_name=class_name,
            factory=factory,
            singleton=singleton,
            tags=tags or [],
            description=description,
        )
        
        self._definitions[name] = definition
        
        # Update domain index
        if domain not in self._domain_index:
            self._domain_index[domain] = []
        if name not in self._domain_index[domain]:
            self._domain_index[domain].append(name)
        
        logger.debug(f"Registered service: {name} in domain {domain}")
    
    def get_service(
        self,
        name: str,
        *,
        config: Optional[Dict[str, Any]] = None,
        force_new: bool = False,
    ) -> BaseService:
        """
        Get a service instance by name.
        
        Args:
            name: Service name
            config: Optional configuration dict passed to constructor
            force_new: If True, create new instance even for singletons
            
        Returns:
            Instantiated service
            
        Raises:
            KeyError: If service not registered
            ImportError: If service module cannot be loaded
        """
        if name not in self._definitions:
            raise KeyError(f"Service '{name}' not registered. Available: {list(self._definitions.keys())}")
        
        definition = self._definitions[name]
        
        # Return cached instance if singleton and no force_new
        cache_key = f"{name}:{hash(frozenset((config or {}).items()))}"
        if definition.singleton and not force_new and cache_key in self._instances:
            return self._instances[cache_key]
        
        # Instantiate service
        service = self._instantiate(definition, config)
        
        # Cache if singleton
        if definition.singleton and not force_new:
            self._instances[cache_key] = service
        
        return service
    
    def get_domain_services(self, domain: str) -> List[BaseService]:
        """Get all services for a scientific domain."""
        service_names = self._domain_index.get(domain, [])
        return [self.get_service(name) for name in service_names]
    
    def list_services(self, domain: Optional[str] = None) -> List[str]:
        """List all registered service names, optionally filtered by domain."""
        if domain:
            return self._domain_index.get(domain, [])
        return list(self._definitions.keys())
    
    def list_domains(self) -> List[str]:
        """List all registered domains."""
        return list(self._domain_index.keys())
    
    def get_definition(self, name: str) -> Optional[ServiceDefinition]:
        """Get service definition metadata."""
        return self._definitions.get(name)
    
    def _instantiate(
        self,
        definition: ServiceDefinition,
        config: Optional[Dict[str, Any]] = None,
    ) -> BaseService:
        """Instantiate a service from its definition."""
        try:
            if definition.factory:
                return definition.factory(config or {})
            
            # Dynamic import
            module = importlib.import_module(definition.module_path)
            service_class = getattr(module, definition.class_name)
            
            # Verify it's a BaseService subclass
            if not issubclass(service_class, BaseService):
                logger.warning(
                    f"Service {definition.name} does not inherit from BaseService. "
                    "Consider updating it for full compatibility."
                )
            
            # Instantiate with config if provided
            if config:
                return service_class(config=config)
            return service_class()
            
        except Exception as e:
            logger.error(f"Failed to instantiate service {definition.name}: {e}")
            raise
    
    def _register_default_services(self) -> None:
        """Register known AXIOM ATLAS services."""
        if self._initialized:
            return
        
        # =====================
        # CHEMISTRY DOMAIN
        # =====================
        self.register(
            name="ComputationalChemistryService",
            domain="chemistry",
            module_path="app.domains.chemistry.services.computational_chemistry",
            class_name="ComputationalChemistryService",
            tags=["rdkit", "molecular", "pyscf"],
            description="Molecular analysis with RDKit, PySCF, and OpenMM",
        )
        self.register(
            name="MaterialsDiscoveryService",
            domain="chemistry",
            module_path="app.domains.chemistry.services.materials_discovery_service",
            class_name="MaterialsDiscoveryService",
            tags=["materials", "discovery"],
            description="Materials discovery and screening",
        )
        self.register(
            name="GNOMEMaterialsService",
            domain="chemistry",
            module_path="app.domains.chemistry.services.gnome_materials_service",
            class_name="GNOMEMaterialsService",
            tags=["gnome", "materials", "381k"],
            description="GNOME database with 381K+ materials",
        )
        self.register(
            name="ChemMLService",
            domain="chemistry",
            module_path="app.domains.chemistry.services.chemml_service",
            class_name="ChemMLService",
            tags=["ml", "predictions"],
            description="ML predictions for chemical properties",
        )
        self.register(
            name="AdvancedNMRService",
            domain="chemistry",
            module_path="app.domains.chemistry.services.advanced_nmr_service",
            class_name="AdvancedNMRService",
            tags=["nmr", "spectroscopy"],
            description="NMR spectroscopy analysis",
        )
        self.register(
            name="AdvancedSpectrometers",
            domain="chemistry",
            module_path="app.domains.chemistry.services.advanced_spectrometers",
            class_name="AdvancedSpectrometers",
            tags=["spectrometers", "nmr", "ms", "uv-vis"],
            description="Advanced spectrometer simulation service",
        )
        self.register(
            name="DifferentialScanningCalorimetryService",
            domain="chemistry",
            module_path="app.domains.chemistry.services.differential_scanning_calorimetry_service",
            class_name="DifferentialScanningCalorimetryService",
            tags=["dsc", "thermal", "calorimetry"],
            description="Differential Scanning Calorimetry service",
        )
        self.register(
            name="MolecularDynamicsService",
            domain="chemistry",
            module_path="app.domains.chemistry.services.molecular_dynamics",
            class_name="MolecularDynamicsService",
            tags=["md", "simulation", "openmm"],
            description="Molecular dynamics simulation service",
        )
        
        # =====================
        # BIOLOGY DOMAIN
        # =====================
        self.register(
            name="GenomicsService",
            domain="biology",
            module_path="app.domains.biology.services.genomics_service",
            class_name="GenomicsService",
            tags=["genomics", "deepvariant"],
            description="Genomics analysis with DeepVariant dry-run",
        )
        self.register(
            name="DNABERT2GenomicsService",
            domain="biology",
            module_path="app.domains.biology.services.dnabert2_service",
            class_name="DNABERT2GenomicsService",
            tags=["dnabert", "transformers", "genomics"],
            description="DNABERT2 for DNA sequence analysis",
        )
        self.register(
            name="ComputationalBiologyService",
            domain="biology",
            module_path="app.domains.biology.services.computational_biology",
            class_name="ComputationalBiologyService",
            tags=["biopython", "sequence"],
            description="Computational biology with BioPython",
        )
        
        # =====================
        # MATHEMATICS DOMAIN
        # =====================
        self.register(
            name="ArithmeticService",
            domain="mathematics",
            module_path="app.domains.mathematics.services.arithmetic",
            class_name="ArithmeticService",
            singleton=True,
            tags=["arithmetic", "basic"],
            description="Basic arithmetic operations",
        )
        
        # =====================
        # CLIMATE DOMAIN
        # =====================
        self.register(
            name="ClimateEvidenceService",
            domain="climate",
            module_path="app.domains.climate.services.climate_evidence_service",
            class_name="ClimateEvidenceService",
            tags=["climate", "evidence"],
            description="Climate evidence analysis",
        )
        
        # =====================
        # ENGINEERING DOMAIN
        # =====================
        self.register(
            name="SynthesisEquipmentService",
            domain="engineering",
            module_path="app.domains.engineering.services.synthesis_equipment",
            class_name="SynthesisEquipmentService",
            tags=["synthesis", "equipment"],
            description="Synthesis equipment management",
        )

        # =====================
        # NEUROSCIENCE DOMAIN
        # =====================
        self.register(
            name="NeuroscienceLightService",
            domain="neuroscience",
            module_path="app.domains.neuroscience.services.neuroscience_light_service",
            class_name="NeuroscienceLightService",
            tags=["neuroscience", "eeg", "light"],
            description="Lightweight EEG analysis service",
        )

        # =====================
        # ASTRONOMY DOMAIN
        # =====================
        self.register(
            name="AstronomicalMLService",
            domain="astronomy",
            module_path="app.domains.astronomy.services.astronomical_ml_service",
            class_name="AstronomicalMLService",
            tags=["astronomy", "ml", "classification"],
            description="Astronomical Machine Learning Service",
        )

        # =====================
        # MEDICINE DOMAIN
        # =====================
        self.register(
            name="AdvancedMedicalImagingService",
            domain="medicine",
            module_path="app.domains.medicine.imaging.advanced_medical_imaging_service",
            class_name="AdvancedMedicalImagingService",
            tags=["medicine", "imaging", "dicom", "nifti"],
            description="Advanced Medical Imaging Service",
        )
        self.register(
            name="ClinicalBERTService",
            domain="medicine",
            module_path="app.domains.medicine.services.clinicalbert_service",
            class_name="ClinicalBERTService",
            tags=["medicine", "nlp", "bert", "clinical"],
            description="ClinicalBERT Service for text analysis",
        )
        self.register(
            name="AlphaFold3ProteinStructureService",
            domain="medicine",
            module_path="app.domains.medicine.services.alphafold3_service",
            class_name="AlphaFold3ProteinStructureService",
            tags=["medicine", "protein", "alphafold", "structure"],
            description="AlphaFold 3 Protein Structure Service",
        )

        # =====================
        # PHYSICS DOMAIN
        # =====================
        self.register(
            name="ParticlePhysicsService",
            domain="physics",
            module_path="app.domains.physics.quantum.particle_physics_service",
            class_name="ParticlePhysicsService",
            tags=["physics", "particle", "quantum", "root"],
            description="Advanced Particle Physics Service",
        )
        self.register(
            name="QuantumComputingService",
            domain="physics",
            module_path="app.domains.physics.quantum.quantum_computing_service",
            class_name="QuantumComputingService",
            tags=["physics", "quantum", "qiskit", "cirq"],
            description="Quantum Computing Service",
        )
        self.register(
            name="SolidStatePhysicsService",
            domain="physics",
            module_path="app.domains.physics.computational.solid_state_physics_service",
            class_name="SolidStatePhysicsService",
            tags=["physics", "solid_state", "dft", "ase", "gpaw"],
            description="Solid State Physics Service",
        )
        self.register(
            name="PlasmaPhysicsService",
            domain="physics",
            module_path="app.domains.physics.plasma.plasma_physics_service",
            class_name="PlasmaPhysicsService",
            tags=["physics", "plasma", "mhd", "pinn"],
            description="Plasma Physics Service",
        )
        self.register(
            name="PhysicsInformedNNService",
            domain="physics",
            module_path="app.domains.physics.computational.physics_informed_nn_service",
            class_name="PhysicsInformedNNService",
            tags=["physics", "computational", "pinn", "neural_networks"],
            description="Physics Informed Neural Networks Service",
        )
        self.register(
            name="GravitationalLensingService",
            domain="physics",
            module_path="app.domains.physics.services.gravitational_lensing",
            class_name="GravitationalLensingService",
            tags=["physics", "astronomy", "lensing", "relativity"],
            description="Gravitational Lensing Analysis Service",
        )
        self.register(
            name="QuantumPhysicsService",
            domain="physics",
            module_path="app.domains.physics.services.quantum_physics",
            class_name="QuantumPhysicsService",
            tags=["physics", "quantum", "qutip", "mechanics"],
            description="Quantum Physics Service with QuTiP",
        )

        # =====================
        # CHEMISTRY DOMAIN
        # =====================
        self.register(
            name="ChemMLService",
            domain="chemistry",
            module_path="app.domains.chemistry.services.chemml_service",
            class_name="ChemMLService",
            tags=["chemistry", "ml", "deepchem", "drug_discovery"],
            description="Chemical Machine Learning Service",
        )
        self.register(
            name="MaterialsDiscoveryService",
            domain="chemistry",
            module_path="app.domains.chemistry.services.materials_discovery_service",
            class_name="MaterialsDiscoveryService",
            tags=["chemistry", "materials", "gnome", "pymatgen"],
            description="Materials Discovery Service",
        )
        self.register(
            name="XRayCrystallographyService",
            domain="chemistry",
            module_path="app.domains.chemistry.services.xray_crystallography_service",
            class_name="XRayCrystallographyService",
            tags=["chemistry", "crystallography", "xray", "diffraction"],
            description="X-Ray Crystallography Service",
        )

        # =====================
        # ENGINEERING DOMAIN
        # =====================
        self.register(
            name="AdditiveManufacturingService",
            domain="engineering",
            module_path="app.domains.engineering.services.additive_manufacturing_service",
            class_name="AdditiveManufacturingService",
            tags=["engineering", "manufacturing", "additive", "simulation"],
            description="Additive Manufacturing Service",
        )
        
        self._initialized = True
        logger.info(f"ServiceLocator initialized with {len(self._definitions)} services")


# Convenience function for quick access
def get_service(name: str, **kwargs: Any) -> BaseService:
    """Quick access to a service by name."""
    return ServiceLocator.get_instance().get_service(name, **kwargs)


def list_services(domain: Optional[str] = None) -> List[str]:
    """List available services."""
    return ServiceLocator.get_instance().list_services(domain)


__all__ = [
    "ServiceLocator",
    "ServiceDefinition",
    "get_service",
    "list_services",
]
