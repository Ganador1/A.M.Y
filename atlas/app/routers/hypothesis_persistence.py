"""
Router de Persistencia de Hipótesis - Gestión del Ciclo de Vida de Hipótesis Científicas

Módulo FastAPI para persistencia de hipótesis y gestión del ciclo de vida científico.
Proporciona operaciones CRUD integrales para hipótesis científicas almacenadas en base de datos,
incluyendo seguimiento de evidencia, historial de refinamientos y validación colaborativa.

Capacidades principales:
- Gestión completa del ciclo de vida: creación, consulta, actualización y eliminación
- Seguimiento de evidencia: acumulación de evidencia de apoyo o contradicción
- Historial de refinamientos: registro de evolución y mejora de hipótesis
- Validación colaborativa: flujos de trabajo para revisión por pares
- Auditoría completa: trazabilidad para reproducibilidad científica
- Filtrado y paginación: consultas eficientes de hipótesis

Catálogo de Endpoints:
- POST /create: Creación de nuevas hipótesis con metadatos iniciales
- GET /get/{uuid}: Consulta de hipótesis específica por UUID con detalles completos
- POST /list: Consulta y filtrado de hipótesis con soporte de paginación
- POST /update: Actualización de metadatos, estado o contenido de hipótesis
- POST /delete: Eliminación suave de hipótesis (mantiene registro de auditoría)
- POST /add-evidence: Adición de evidencia de apoyo o contradicción
- POST /add-refinement: Registro de refinamiento o evolución de hipótesis

Dependencias:
- HypothesisPersistenceService: Servicio central de persistencia y lógica de negocio
- require_bearer: Dependencia de autenticación para acceso seguro
- Modelos de base de datos: Entidades Hypothesis, Evidence, Refinement

Uso del Servicio:
    Todos los endpoints requieren autenticación y retornan respuestas estructuradas
    con estado de éxito, carga de datos y mensajes de error cuando corresponda.
    Las hipótesis mantienen registros de auditoría completos para reproducibilidad científica.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from app.services.hypothesis_persistence import HypothesisPersistenceService
from app.security import require_bearer

router = APIRouter(dependencies=[Depends(require_bearer)])
service = HypothesisPersistenceService()


@router.post("/create")
async def create(request: Dict[str, Any]):
    res = await service.process_request({"action": "create", **request})
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "create failed"))
    return res


@router.get("/get/{hypothesis_uuid}")
async def get(hypothesis_uuid: str):
    res = await service.process_request({"action": "get", "hypothesis_uuid": hypothesis_uuid})
    if not res.get("success"):
        raise HTTPException(status_code=404, detail=res.get("error", "not found"))
    return res


@router.post("/list")
async def list_items(request: Dict[str, Any]):
    res = await service.process_request({"action": "list", **request})
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "list failed"))
    return res


@router.post("/update")
async def update(request: Dict[str, Any]):
    res = await service.process_request({"action": "update", **request})
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "update failed"))
    return res
@router.post("/delete")
async def delete(request: Dict[str, Any]):
    res = await service.process_request({"action": "delete", **request})
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "delete failed"))
    return res


@router.post("/add-evidence")
async def add_evidence(request: Dict[str, Any]):
    res = await service.process_request({"action": "add_evidence", **request})
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "add_evidence failed"))
    return res


@router.post("/add-refinement")
async def add_refinement(request: Dict[str, Any]):
    res = await service.process_request({"action": "add_refinement", **request})
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "add_refinement failed"))
    return res
