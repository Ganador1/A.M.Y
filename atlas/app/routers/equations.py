"""
Wrapper de Equations Router

Expone el router de ecuaciones del dominio de matemáticas bajo
`app.routers.equations` para compatibilidad con el registro automático.
"""

from app.domains.mathematics.routers.equations import router as equations_router

# Fallback común para cargadores que esperan `router`
router = equations_router

__all__ = ["equations_router", "router"]