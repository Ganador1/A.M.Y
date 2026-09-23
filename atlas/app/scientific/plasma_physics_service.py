#!/usr/bin/env python3
"""
Compatibilidad: app.scientific.plasma_physics_service
Reexporta la implementación canónica ubicada en app.domains.physics.plasma.plasma_physics_service.

Este módulo existe para mantener compatibilidad hacia atrás con imports legacy
(`app.scientific.plasma_physics_service`). La implementación real vive en el
espacio de dominios y aquí sólo se reexpone la API pública.
"""

from app.domains.physics.plasma.plasma_physics_service import (
    PlasmaRegime,
    PlasmaSpecies,
    PlasmaParameters,
    PlasmaSolution,
    TransportCoefficients,
    PlasmaEquations,
    IdealMHDEquations,
    ResistiveMHDEquations,
    TwoFluidEquations,
    PlasmaPINNSolver,
    PlasmaPhysicsService,
    plasma_physics_service,
    solve_plasma_problem,
)

__all__ = [
    "PlasmaRegime",
    "PlasmaSpecies",
    "PlasmaParameters",
    "PlasmaSolution",
    "TransportCoefficients",
    "PlasmaEquations",
    "IdealMHDEquations",
    "ResistiveMHDEquations",
    "TwoFluidEquations",
    "PlasmaPINNSolver",
    "PlasmaPhysicsService",
    "plasma_physics_service",
    "solve_plasma_problem",
]

# Nota: si en el futuro se elimina este wrapper, actualiza los imports a
# "app.domains.physics.plasma.plasma_physics_service" directamente.

