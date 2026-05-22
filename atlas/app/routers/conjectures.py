from __future__ import annotations
import asyncio

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.mathlab.persistence.conjecture_persistence import ConjecturePersistenceService
from app.exceptions.domain.biology import BiologyError
from app.types.conjectures_types import (
    RankPersistResult,
    RankPersistBatchResult,
    TopConjecturesResult,
)


router = APIRouter(prefix="/api/conjectures", tags=["conjectures"])
_persistence = ConjecturePersistenceService()


class UpdateImportanceRequest(BaseModel):
    conjecture_id: str = Field(...)
    importance: float = Field(..., ge=0.0, le=1.0)


class BatchUpdateImportanceRequest(BaseModel):
    updates: List[UpdateImportanceRequest] = Field(..., description="Lista de actualizaciones (id, importance)")


@router.post("/rank-persist")
async def rank_persist(req: UpdateImportanceRequest) -> RankPersistResult:
    ok = _persistence.update_importance_score(req.conjecture_id, req.importance)
    return {"success": bool(ok)}


@router.post("/rank-persist-batch")
async def rank_persist_batch(req: BatchUpdateImportanceRequest) -> RankPersistBatchResult:
    success = 0
    failed: List[str] = []
    for upd in req.updates:
        try:
            if _persistence.update_importance_score(upd.conjecture_id, upd.importance):
                success += 1
            else:
                failed.append(upd.conjecture_id)
        except BiologyError:
            failed.append(upd.conjecture_id)
    return {"success": True, "updated": success, "failed": failed}


@router.get("/top")
async def top_conjectures(limit: int = 10) -> TopConjecturesResult:
    items = _persistence.get_top_ranked_conjectures(limit=limit)
    out = []
    for c in items:
        out.append({
            "id": c.id,
            "title": c.title,
            "statement": c.statement,
            "importance_score": c.importance_score,
            "confidence": c.confidence,
            "status": c.status,
        })
    return {"count": len(out), "items": out}


@router.get("/top-topological")
async def top_topological_conjectures(
    limit: int = Query(10, ge=1, le=100),
    conjecture_type: str | None = Query(None)
) -> Dict[str, Any]:
    ct = None
    from app.mathlab.persistence.conjecture_persistence import ConjectureType as CT
    if conjecture_type:
        try:
            ct = CT[conjecture_type] if conjecture_type in CT.__members__ else None
        except BiologyError:
            ct = None
    items = _persistence.get_top_conjectures_by_object_type(
        object_type="point_cloud",
        conjecture_type=ct,
        limit=limit
    )
    out = []
    for c in items:
        out.append({
            "id": c.id,
            "title": c.title,
            "statement": c.statement,
            "importance_score": c.importance_score,
            "confidence": c.confidence,
            "status": c.status,
            "conjecture_type": c.conjecture_type,
            "primary_object_id": c.primary_object_id,
        })
    return {"count": len(out), "items": out}


@router.get("/top-topological-report")
async def top_topological_conjectures_report(
    limit: int = Query(5, ge=1, le=20),
    include_images: bool = Query(True)
) -> Dict[str, Any]:
    """
    Devuelve top-N conjeturas asociadas a objetos `point_cloud` con datos del objeto y
    opcionalmente imágenes básicas (si disponibles vía recomputación ligera no intrusiva).
    """
    items = _persistence.get_top_conjectures_by_object_type("point_cloud", limit=limit)
    out: List[Dict[str, Any]] = []
    for c in items:
        obj: Optional[dict] = None
        mo = _persistence.get_object_by_id(c.primary_object_id) if c.primary_object_id else None
        if mo:
            obj = {
                "id": mo.id,
                "object_type": mo.object_type,
                "properties": mo.properties or {},
                "invariants": mo.invariants or {},
            }
        entry: Dict[str, Any] = {
            "id": c.id,
            "title": c.title,
            "statement": c.statement,
            "importance_score": c.importance_score,
            "confidence": c.confidence,
            "conjecture_type": c.conjecture_type,
            "primary_object": obj,
        }
        if include_images and mo and mo.object_type == "point_cloud":
            # Recomputar imágenes ligeras a partir del canonical_form (lista de puntos [[x,y],...])
            try:
                import json
                import io
                import base64
                import numpy as np
                import matplotlib
                matplotlib.use("Agg")
                import matplotlib.pyplot as plt

                pts = json.loads(mo.canonical_form)
                if isinstance(pts, list) and pts:
                    arr = np.array(pts, dtype=float)
                    if arr.ndim == 2 and arr.shape[1] == 2:
                        # Diagrama de persistencia (placeholder simple usando dispersión birth~death estimada)
                        # Nota: el cálculo real de pares birth-death debe venir de servicio de persistencia.
                        # Aquí mostramos una proyección dummy para visualización ligera.
                        xs = arr[:, 0]
                        ys = arr[:, 1]
                        fig, ax = plt.subplots(figsize=(4, 3), dpi=120)
                        ax.scatter(xs, ys, s=8, alpha=0.6)
                        ax.set_title("Point Cloud (preview)")
                        ax.set_xlabel("x")
                        ax.set_ylabel("y")
                        buf = io.BytesIO(); plt.tight_layout(); fig.savefig(buf, format="png"); plt.close(fig); buf.seek(0)
                        entry.setdefault("images", {})["point_cloud_preview_base64"] = base64.b64encode(buf.read()).decode("ascii")
            except BiologyError:
                pass
        out.append(entry)
    return {"count": len(out), "items": out, "images_embedded": bool(include_images)}


