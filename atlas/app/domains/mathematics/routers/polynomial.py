from __future__ import annotations

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.mathlab.invariants.polynomial_invariants import compute_polynomial_invariants
from app.mathlab.persistence.conjecture_persistence import ConjecturePersistenceService
from app.exceptions.domain.mathematics import MathematicsError


router = APIRouter(prefix="/api/polynomial", tags=["polynomial"])
_persistence = ConjecturePersistenceService()


class PolynomialRequest(BaseModel):
    coeffs: List[float] = Field(..., description="Coeficientes [a_n, a_{n-1}, ..., a_0]")


@router.post("/invariants")
async def polynomial_invariants(req: PolynomialRequest) -> Dict[str, Any]:
    try:
        inv = compute_polynomial_invariants(req.coeffs)
        # Convertir objetos sympy a str para JSON seguro
        def to_jsonable(v):
            try:
                return str(v)
            except MathematicsError:
                return v
        json_inv = {k: to_jsonable(v) for k, v in inv.items()}
        return {"coeffs": req.coeffs, "invariants": json_inv}
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))


class PolynomialRegisterRequest(BaseModel):
    name: str = Field(default="polynomial")
    coeffs: List[float] = Field(..., description="Coeficientes [a_n, a_{n-1}, ..., a_0]")


@router.post("/register")
async def polynomial_register(req: PolynomialRegisterRequest) -> Dict[str, Any]:
    try:
        # Canonical form: string with coefficients
        canonical = ",".join(str(c) for c in req.coeffs)
        # Simple hash: reuse canonical as unique key through persistence layer
        object_id = _persistence.store_mathematical_object(
            object_type="polynomial",
            name=req.name,
            canonical_form=canonical,
            hash_value=f"poly_{hash(tuple(req.coeffs))}",
            properties={"coeffs": req.coeffs},
            invariants={}
        )
        return {"object_id": object_id, "name": req.name}
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))


class PolynomialBatchRequest(BaseModel):
    items: List[List[float]] = Field(..., description="Lista de polinomios (coeficientes)")


@router.post("/invariants-batch")
async def polynomial_invariants_batch(req: PolynomialBatchRequest) -> Dict[str, Any]:
    results = []
    for coeffs in req.items:
        try:
            inv = compute_polynomial_invariants(coeffs)
            results.append({"coeffs": coeffs, "invariants": {k: str(v) for k, v in inv.items()}})
        except MathematicsError as e:
            results.append({"coeffs": coeffs, "error": str(e)})
    return {"count": len(results), "items": results}


