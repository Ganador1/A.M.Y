"""
FastAPI routers

Carga segura de routers para evitar que módulos opcionales con errores
bloqueen la inicialización de la aplicación y los tests.
"""

import importlib
import logging
from app.exceptions.domain.physics import QuantumError

logger = logging.getLogger(__name__)

_router_modules = [
    "advanced_algorithms",
    "advanced_lab_automation",
    "advanced_math_nlp",
    "agent2_bridge_router",
    "alphafold3",
    "biomedical_nlp",
    "clinicalbert",
    "computational_chemistry",
    "experimental_toolkit",
    "hardware_abstraction",
    "math_nlp",
    "math_physics",
    "neuro_simulation",
    "quantum_algorithms",
    "quantum_computing",
    "router_registry",
    "synthesis_equipment",
    "validation_matrix",
]

__all__ = []

for _mod_name in _router_modules:
    try:
        _mod = importlib.import_module(f"{__name__}.{_mod_name}")
        globals()[_mod_name] = _mod
        __all__.append(_mod_name)
    except Exception as e:  # Catch any import-time errors to avoid breaking test collection
        logger.warning(f"Router '{_mod_name}' import failed: {e}")
        continue
