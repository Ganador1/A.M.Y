"""
Synthesis Equipment Router - Compatibility Wrapper
This module re-exports the router from app.domains.engineering.routers.synthesis_equipment
to maintain backward compatibility with imports expecting app.routers.synthesis_equipment.
"""

from app.domains.engineering.routers.synthesis_equipment import router

__all__ = ["router"]