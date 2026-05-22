"""
Provenance Router for AXIOM
Endpoints para grafos de reproducibilidad de experimentos y datos
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional  # noqa: F401  (posible uso futuro)

from app.services.provenance import ProvenanceService
# Usar las instancias compartidas de los otros routers para mantener estado en memoria
from app.routers.experiment_tracking import experiment_service
from app.routers.data_versioning import data_versioning_service
from app.security import require_bearer
from app.exceptions.infrastructure.database import DatabaseError


router = APIRouter(dependencies=[Depends(require_bearer)])


@router.get("/experiments")
async def graph_all_experiments(render_html: bool = Query(True, description="Renderizar HTML interactivo")):
    """Devuelve el grafo unificado de todos los experimentos, artefactos y versiones de datos."""
    try:
        # Instanciar sólo el servicio de provenance; reutilizar los servicios compartidos para preservar estado
        prov_service = ProvenanceService()
        result = prov_service.build_all_experiments_graph(
            exp_service=experiment_service,
            data_service=data_versioning_service,
            render_html=render_html,
        )
        if not result.get("success"):
            raise HTTPException(status_code=500, detail="Failed to build provenance graph")
        return result
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/experiment/{experiment_id}")
async def graph_single_experiment(
    experiment_id: str,
    render_html: bool = Query(True, description="Renderizar HTML interactivo"),
):
    """Devuelve el grafo de un experimento específico y su relación con datos versionados."""
    try:
        prov_service = ProvenanceService()
        result = prov_service.build_experiment_graph(
            exp_service=experiment_service,
            experiment_id=experiment_id,
            data_service=data_versioning_service,
            render_html=render_html,
        )
        if not result.get("success"):
            raise HTTPException(status_code=404, detail="Experiment not found or graph unavailable")
        return result
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
