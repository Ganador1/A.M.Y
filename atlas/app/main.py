from __future__ import annotations

import os

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


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _is_production_mode() -> bool:
    return os.getenv("ATLAS_ENV", os.getenv("ENVIRONMENT", "development")).strip().lower() in {
        "prod",
        "production",
    }


def _docs_url(path: str) -> str | None:
    if _is_production_mode() and not _env_flag("ATLAS_ENABLE_PUBLIC_DOCS", False):
        return None
    return path


app = FastAPI(
    title="A.M.Y API",
    version="4.1",
    docs_url=_docs_url("/docs"),
    redoc_url=_docs_url("/redoc"),
    openapi_url=_docs_url("/openapi.json"),
)

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

from app.middleware.setup import configure_security_middleware
configure_security_middleware(app)

__all__ = ["app"]
