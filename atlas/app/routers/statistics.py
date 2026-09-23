"""
Wrapper para el router de estadísticas del dominio de matemáticas.
Expone `statistics_router` para el registro dinámico en `router_registry`.
"""

from app.domains.mathematics.routers.statistics import router as statistics_router

__all__ = ["statistics_router"]