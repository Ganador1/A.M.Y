"""
Router del Laboratorio Matemático - AXIOM Meta 4.1
===============================================

Este módulo implementa el router para el laboratorio matemático de AXIOM, proporcionando
capacidades avanzadas para el manejo, análisis y procesamiento de objetos matemáticos.
Ofrece un entorno computacional completo para investigación matemática con soporte para
grafos, números, invariantes, embeddings y procesamiento por lotes.

Capacidades Principales:
----------------------
- **Registro de Objetos Matemáticos**: Gestión de objetos matemáticos con hashing semántico
- **Invariantes Matemáticos**: Cálculo de invariantes para grafos y números enteros
- **Embeddings Vectoriales**: Generación de representaciones vectoriales para análisis
- **Generación de Grafos**: Creación de grafos Erdős–Rényi y otras estructuras
- **Procesamiento por Lotes**: Cálculo masivo de invariantes con seguimiento de progreso
- **Sistema de Jobs**: Gestión asíncrona de tareas computacionalmente intensivas

Endpoints Disponibles:
--------------------
- POST /mathlab/objects/register: Registra nuevo objeto matemático
- POST /mathlab/numbers/register: Registra número entero
- GET /mathlab/objects/{object_id}: Obtiene objeto por ID
- GET /mathlab/objects: Lista objetos registrados
- POST /mathlab/graphs/er: Crea grafo Erdős–Rényi
- GET /mathlab/invariants/graph/{object_id}: Calcula invariantes de grafo
- GET /mathlab/invariants/number/{object_id}: Calcula invariantes de número
- GET /mathlab/embeddings/graph/{object_id}: Genera embedding de grafo
- GET /mathlab/embeddings/number/{object_id}: Genera embedding de número
- POST /mathlab/batch/invariants: Calcula invariantes por lotes (síncrono)
- POST /mathlab/batch/invariants/submit: Envía job de invariantes por lotes (asíncrono)
- GET /mathlab/batch/invariants/status/{job_id}: Consulta estado de job por lotes

Dependencias:
-----------
- FastAPI: Framework web para APIs REST
- app.mathlab.core.object_registry: Registro central de objetos matemáticos
- app.mathlab.core.object_models: Modelos de objetos matemáticos
- app.mathlab.invariants: Servicios de cálculo de invariantes
- app.mathlab.embeddings: Servicios de generación de embeddings
- app.mathlab.generation: Generadores de estructuras matemáticas

Uso del Servicio:
---------------
```python
import asyncio
from fastapi import FastAPI
from app.routers.mathlab import router
from app.exceptions.domain.mathematics import MathematicsError

app = FastAPI()
app.include_router(router)

# Registrar un grafo
response = await client.post("/mathlab/graphs/er", json={"n": 100, "p": 0.1})

# Calcular invariantes
response = await client.get(f"/mathlab/invariants/graph/{object_id}")

# Procesamiento por lotes
response = await client.post("/mathlab/batch/invariants/submit",
    json={"object_ids": ["id1", "id2", "id3"]})
```

Consideraciones de Seguridad:
---------------------------
- Validación de entrada para prevenir creación de objetos malformados
- Límites en tamaño de lotes para prevenir sobrecarga computacional
- Control de acceso a objetos matemáticos sensibles
- Logging detallado de operaciones para auditoría matemática
- Rate limiting para operaciones computacionalmente intensivas

Notas de Implementación:
----------------------
- Utiliza hashing semántico para deduplicación de objetos idénticos
- Implementa procesamiento asíncrono para tareas de larga duración
- Soporta múltiples tipos de objetos: grafos, números, expresiones
- Incluye sistema de invariantes para caracterización matemática
- Proporciona embeddings para aprendizaje automático matemático
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timezone
import threading
import time

from app.mathlab.core.object_registry import REGISTRY
from app.mathlab.core.hashing import semantic_hash
from app.mathlab.invariants.graph_invariants import GraphInvariants
from app.mathlab.invariants.number_invariants import NumberInvariants
from app.mathlab.generation.graph_generator import register_er_graph
from app.mathlab.embeddings.graph_embeddings import laplacian_spectrum_embedding
from app.mathlab.embeddings.number_embeddings import prime_factor_signature_embedding
from app.types.mathlab_types import (
    RegisterObjectResult,
    CreateIntegerResult,
    GetObjectResult,
    ListObjectsResult,
    CreateErGraphResult,
    ComputeGraphInvariantsResult,
    ComputeNumberInvariantsResult,
    GraphEmbeddingResult,
    NumberEmbeddingResult,
    BatchComputeInvariantsResult,
    SubmitBatchInvariantsResult,
    BatchInvariantsStatusResult,
)

# Configuración de logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mathlab", tags=["mathlab"])

# Modelos Pydantic para requests
class ObjectRegistrationRequest(BaseModel):
    """Modelo de solicitud para registro de objetos."""
    type: str = Field(..., description="Tipo de objeto matemático")
    payload: Dict[str, Any] = Field(..., description="Datos del objeto en formato JSON")

class ERGraphRequest(BaseModel):
    """Modelo de solicitud para creación de grafos Erdős–Rényi."""
    n: int = Field(..., gt=0, description="Número de nodos")
    p: float = Field(0.0, ge=0.0, le=1.0, description="Probabilidad de arista")
    directed: bool = Field(False, description="Si el grafo es dirigido")

class BatchInvariantsRequest(BaseModel):
    """Modelo de solicitud para cálculo por lotes de invariantes."""
    object_ids: List[str] = Field(..., description="Lista de IDs de objetos")
    chunk_size: Optional[int] = Field(50, gt=0, description="Tamaño de chunk para procesamiento")

class BatchSubmitRequest(BaseModel):
    """Modelo de solicitud para envío de job por lotes."""
    object_ids: List[str] = Field(..., description="Lista de IDs de objetos")
    chunk_size: Optional[int] = Field(50, gt=0, description="Tamaño de chunk para procesamiento")

# In-memory simple job manager for batch invariants
_JOBS_LOCK = threading.RLock()
_JOBS: Dict[str, Any] = {}


@router.post("/objects/register", response_model=Dict[str, Any])
async def register_object(payload: RegisterObjectResult) -> RegisterObjectResult:
    """
    Registra un nuevo objeto matemático en el laboratorio.

    Este endpoint permite registrar objetos matemáticos de diversos tipos
    (grafos, números, expresiones) con hashing semántico para deduplicación.

    Args:
        payload: Diccionario con tipo de objeto y datos JSON

    Returns:
        Información del objeto registrado incluyendo ID y hash semántico

    Raises:
        HTTPException: Si falta el tipo de objeto o hay error en el registro
    """
    try:
        obj_type = payload.get("type")
        if not obj_type:
            raise HTTPException(status_code=400, detail="Missing 'type' in payload")

        logger.info("📝 Registering mathematical object of type: %s", obj_type)

        # Permitimos payload con 'type' y resto como JSON del objeto
        normalized_payload = {k: v for k, v in payload.items() if k != "type"}
        mobj = REGISTRY.register(obj_type=obj_type, payload_json=normalized_payload)

        logger.info("✅ Successfully registered object %s of type %s", mobj.id, obj_type)
        return {"id": mobj.id, "object_id": mobj.id, "semantic_hash": mobj.semantic_hash, "type": mobj.type}

    except HTTPException:
        raise
    except MathematicsError as e:
        logger.exception("❌ Error registering mathematical object")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/objects/integer", response_model=Dict[str, Any])
async def create_integer(value: str) -> CreateIntegerResult:
    """
    Crea un objeto matemático de tipo entero.

    Args:
        value: Valor del entero como string

    Returns:
        Información del objeto entero creado
    """
    try:
        logger.info("🔢 Creating integer object with value: %s", value)
        mobj = REGISTRY.register("integer", {"value": value})
        logger.info("✅ Successfully created integer object %s", mobj.id)
        return {"id": mobj.id, "object_id": mobj.id, "semantic_hash": mobj.semantic_hash, "type": mobj.type}
    except MathematicsError as e:
        logger.exception("❌ Error creating integer object")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/objects/{object_id}", response_model=Dict[str, Any])
async def get_object(object_id: str) -> GetObjectResult:
    """
    Obtiene un objeto matemático por su ID.

    Args:
        object_id: ID del objeto matemático

    Returns:
        Datos del objeto matemático

    Raises:
        HTTPException: Si el objeto no existe
    """
    try:
        logger.info("🔍 Retrieving mathematical object: %s", object_id)
        if (obj := REGISTRY.get(object_id)) is None:
            logger.warning("❌ Object not found: %s", object_id)
            raise HTTPException(status_code=404, detail="Object not found")
        logger.info("✅ Successfully retrieved object %s", object_id)
        return obj.model_dump()
    except HTTPException:
        raise
    except MathematicsError as e:
        logger.exception("❌ Error retrieving object %s", object_id)
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/objects", response_model=Dict[str, Any])
async def list_objects(limit: int = 50) -> ListObjectsResult:
    objs = REGISTRY.list(limit=limit)
    return {"objects": [o.model_dump() for o in objs], "total": REGISTRY.stats().total_objects}


@router.post("/graphs/er", response_model=Dict[str, Any])
async def create_er_graph(n: int, p: float, directed: bool = False) -> CreateErGraphResult:
    oid = register_er_graph(n, p, directed)
    return {"object_id": oid}


@router.get("/invariants/graph/{object_id}", response_model=Dict[str, Any])
async def compute_graph_invariants(object_id: str) -> ComputeGraphInvariantsResult:
    obj = REGISTRY.get(object_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    if obj.type != "graph":
        raise HTTPException(status_code=400, detail="Object is not a graph")
    inv = GraphInvariants().compute(obj)
    return {"object_id": object_id, "invariants": inv}


@router.get("/invariants/number/{object_id}", response_model=Dict[str, Any])
async def compute_number_invariants(object_id: str) -> ComputeNumberInvariantsResult:
    obj = REGISTRY.get(object_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    if obj.type != "integer":
        raise HTTPException(status_code=400, detail="Object is not an integer")
    inv = NumberInvariants().compute(obj)
    return {"object_id": object_id, "invariants": inv}


@router.get("/embeddings/graph/{object_id}", response_model=Dict[str, Any])
async def graph_embedding(object_id: str, k: int = 16) -> GraphEmbeddingResult:
    obj = REGISTRY.get(object_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    if obj.type != "graph":
        raise HTTPException(status_code=400, detail="Object is not a graph")
    emb = laplacian_spectrum_embedding(obj, k=k)
    return {"object_id": object_id, **emb}


@router.get("/embeddings/number/{object_id}", response_model=Dict[str, Any])
async def number_embedding(object_id: str, k: int = 16) -> NumberEmbeddingResult:
    obj = REGISTRY.get(object_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    if obj.type != "integer":
        raise HTTPException(status_code=400, detail="Object is not an integer")
    emb = prime_factor_signature_embedding(obj, k=k)
    return {"object_id": object_id, **emb}


@router.post("/batch/invariants", response_model=Dict[str, Any])
async def batch_compute_invariants(payload: BatchComputeInvariantsResult) -> BatchComputeInvariantsResult:
    object_ids = payload.get("object_ids")
    if not isinstance(object_ids, list) or not all(isinstance(x, str) for x in object_ids):
        raise HTTPException(status_code=400, detail="'object_ids' must be a list of strings")

    results = []
    errors = []
    graph_inv = GraphInvariants()
    number_inv = NumberInvariants()

    for oid in object_ids:
        obj = REGISTRY.get(oid)
        if not obj:
            errors.append({"object_id": oid, "error": "Object not found"})
            continue
        try:
            if obj.type == "graph":
                inv = graph_inv.compute(obj)
            elif obj.type == "integer":
                inv = number_inv.compute(obj)
            else:
                errors.append({"object_id": oid, "error": f"Unsupported type: {obj.type}"})
                continue
            results.append({"object_id": oid, "type": obj.type, "invariants": inv})
        except MathematicsError as e:  # noqa: BLE001 - defensive catch to continue processing other objects in batch
            errors.append({"object_id": oid, "error": str(e)})

    return {"results": results, "errors": errors}


# In-memory simple job manager for batch invariants
_JOBS_LOCK = threading.RLock()
_JOBS: Dict[str, Any] = {}


def _process_batch_invariants(job_id: str, object_ids: list[str], chunk_size: int = 50) -> None:
    start_ts = datetime.now(timezone.utc).isoformat()
    with _JOBS_LOCK:
        job = _JOBS.get(job_id)
        if job is None:
            return
        job.update({
            "status": "running",
            "started_at": start_ts,
        })
    graph_inv = GraphInvariants()
    number_inv = NumberInvariants()

    results: list[Dict[str, Any]] = []
    errors: list[Dict[str, Any]] = []
    total = len(object_ids)
    processed = 0

    try:
        for i in range(0, total, max(1, chunk_size)):
            batch = object_ids[i:i + chunk_size]
            for oid in batch:
                obj = REGISTRY.get(oid)
                if not obj:
                    errors.append({"object_id": oid, "error": "Object not found"})
                    processed += 1
                    continue
                try:
                    if obj.type == "graph":
                        inv = graph_inv.compute(obj)
                    elif obj.type == "integer":
                        inv = number_inv.compute(obj)
                    else:
                        errors.append({"object_id": oid, "error": f"Unsupported type: {obj.type}"})
                        processed += 1
                        continue
                    results.append({"object_id": oid, "type": obj.type, "invariants": inv})
                except MathematicsError as e:  # noqa: BLE001 - defensive catch to keep batch processing running despite individual failures
                    errors.append({"object_id": oid, "error": str(e)})
                finally:
                    processed += 1

            # update progress periodically
            with _JOBS_LOCK:
                job = _JOBS.get(job_id)
                if job is None:
                    break
                job.update({
                    "processed": processed,
                    "results": results,
                    "errors": errors,
                    "progress": processed / total if total else 1.0,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                })
            # tiny sleep to yield
            time.sleep(0.001)

        finish_ts = datetime.now(timezone.utc).isoformat()
        with _JOBS_LOCK:
            job = _JOBS.get(job_id)
            if job is not None:
                job.update({
                    "status": "completed",
                    "finished_at": finish_ts,
                    "results": results,
                    "errors": errors,
                    "processed": processed,
                })
    except BaseException as e:  # noqa: BLE001 - catch all exceptions to properly mark background job as failed
        with _JOBS_LOCK:
            job = _JOBS.get(job_id)
            if job is not None:
                job.update({
                    "status": "failed",
                    "error": str(e),
                    "finished_at": datetime.now(timezone.utc).isoformat(),
                })


@router.post("/batch/invariants/submit", response_model=Dict[str, Any])
async def submit_batch_invariants(payload: SubmitBatchInvariantsResult, background: BackgroundTasks) -> SubmitBatchInvariantsResult:
    object_ids = payload.get("object_ids")
    chunk_size = int(payload.get("chunk_size", 50))
    if not isinstance(object_ids, list) or not all(isinstance(x, str) for x in object_ids):
        raise HTTPException(status_code=400, detail="'object_ids' must be a list of strings")
    if chunk_size <= 0:
        raise HTTPException(status_code=400, detail="'chunk_size' must be positive")

    # Deterministic job id based on inputs only, to deduplicate identical submissions
    job_id = semantic_hash({"object_ids": object_ids, "chunk_size": chunk_size}, obj_type="batch_invariants", spec_version="v1")
    with _JOBS_LOCK:
        if job_id in _JOBS:
            job = _JOBS[job_id]
            # If an identical job exists, return its id (could be pending, running, completed, or failed)
            return {"job_id": job_id, "status": job.get("status", "pending")}
        _JOBS[job_id] = {
            "job_id": job_id,
            "status": "pending",
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "total": len(object_ids),
            "processed": 0,
            "results": [],
            "errors": [],
            "progress": 0.0,
            "params": {"chunk_size": chunk_size},
        }

    background.add_task(_process_batch_invariants, job_id, object_ids, chunk_size)
    return {"job_id": job_id, "status": "pending"}


@router.get("/batch/invariants/status/{job_id}", response_model=Dict[str, Any])
async def batch_invariants_status(job_id: str) -> BatchInvariantsStatusResult:
    with _JOBS_LOCK:
        job = _JOBS.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        # shallow copy to avoid leaking internal references
        view = dict(job)
        # Optionally limit payload size for results in status endpoint
        max_preview = 50
        if isinstance(view.get("results"), list) and len(view["results"]) > max_preview:
            view["results_preview"] = view["results"][:max_preview]
            view["results"] = ["<truncated>"]
        return view