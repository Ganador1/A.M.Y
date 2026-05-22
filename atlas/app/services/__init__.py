"""Entrypoint de servicios compartidos para compatibilidad retroactiva."""

from __future__ import annotations

# Importar desde las nuevas ubicaciones
from app.domains.biology.services.computational_biology import ComputationalBiologyService
from app.domains.chemistry.services.computational_chemistry import ComputationalChemistryService
from app.domains.physics.services.solid_state_physics import SolidStatePhysicsService

__all__ = [
    "ComputationalBiologyService",
    "ComputationalChemistryService",
    "SolidStatePhysicsService",
]
