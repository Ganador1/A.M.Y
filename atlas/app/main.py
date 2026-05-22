from __future__ import annotations

from fastapi import FastAPI

# Import domain routers
from app.domains.mathematics.routers.api import router as mathematics_router
from app.domains.biology.routers.api import router as biology_router
from app.domains.engineering.routers.core.api import router as engineering_router
from app.domains.chemistry.routers.api import router as chemistry_router
from app.domains.physics.routers.api import router as physics_router
from app.domains.medicine.routers.api import router as medicine_router

# Automatic router registration
from app.routers.router_registry import register_routers
# Include root health checks router
from app.routers.health_checks import router as health_checks_router
from app.routers.lean4_management import router as lean4_router

app = FastAPI(title="AXIOM API", version="4.1")

# Mount domain routers (preserve existing domain endpoints)
app.include_router(mathematics_router)
app.include_router(biology_router)
app.include_router(engineering_router)
app.include_router(chemistry_router)
app.include_router(physics_router)
app.include_router(medicine_router)
# Include root /health endpoints
app.include_router(health_checks_router)
# Include Lean4 management endpoints
app.include_router(lean4_router)

# Activate automatic router registration for granular /api/* routers
register_routers(app)

__all__ = ["app"]