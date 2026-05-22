"""
Compatibility wrapper for materials_discovery_service
Re-exports from app.domains.chemistry.materials.materials_discovery_service
"""

from app.domains.chemistry.materials.materials_discovery_service import (
    MaterialsDiscoveryService,
    MaterialComposition,
    MaterialStructure,
    MaterialProperties,
    MaterialCandidate
)

__all__ = [
    'MaterialsDiscoveryService',
    'MaterialComposition',
    'MaterialStructure', 
    'MaterialProperties',
    'MaterialCandidate'
]