from __future__ import annotations

from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.mathlab.objects.elliptic_curve_enhanced import EllipticCurve
from app.mathlab.invariants.elliptic_invariants import EllipticInvariants
from app.domains.mathematics.services.sagemath_service import SageMathService
from app.mathlab.persistence.conjecture_persistence import ConjecturePersistenceService
from app.exceptions.domain.mathematics import MathematicsError


router = APIRouter(prefix="/api/elliptic", tags=["elliptic"])
_persistence = ConjecturePersistenceService()


class EllipticRequest(BaseModel):
    A: int = Field(..., description="Coeficiente A en y^2 = x^3 + Ax + B")
    B: int = Field(..., description="Coeficiente B en y^2 = x^3 + Ax + B")


@router.post("/invariants")
async def elliptic_invariants(req: EllipticRequest) -> Dict[str, Any]:
    try:
        curve = EllipticCurve(a=req.A, b=req.B)
        inv = EllipticInvariants()
        obj = type("MO", (), {"type": "elliptic_curve", "payload_json": {"A": req.A, "B": req.B}})()
        res = inv.compute(obj)  # Dict con j, Δ, torsion_est, rank_est, conductor_est, etc.
        return {"curve": {"A": req.A, "B": req.B}, "invariants": res}
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/advanced-invariants")
async def elliptic_advanced_invariants(req: EllipticRequest) -> Dict[str, Any]:
    svc = SageMathService(timeout_seconds=120)
    res = await svc.analyze_elliptic_curve(req.A, req.B)
    return {"curve": {"A": req.A, "B": req.B}, "sage": res}


class EllipticPersistRequest(BaseModel):
    name: str = Field(default="elliptic_curve")
    A: int
    B: int


@router.post("/invariants-persist")
async def elliptic_invariants_persist(req: EllipticPersistRequest) -> Dict[str, Any]:
    # compute invariants first
    obj = type("MO", (), {"type": "elliptic_curve", "payload_json": {"A": req.A, "B": req.B}})()
    inv = EllipticInvariants().compute(obj)
    canonical = f"y^2=x^3+{req.A}*x+{req.B}"
    oid = _persistence.store_mathematical_object(
        object_type="elliptic_curve",
        name=req.name,
        canonical_form=canonical,
        hash_value=f"ec_{hash((req.A, req.B))}",
        properties={"A": req.A, "B": req.B},
        invariants=inv,
    )
    return {"object_id": oid, "invariants": inv}


