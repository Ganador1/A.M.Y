# Shim router to expose optimization_router for router_registry
from app.domains.mathematics.routers.optimization import router as optimization_router

__all__ = ["optimization_router"]