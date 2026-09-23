"""
Advanced Algebra Router for Mathematics AI
Provides REST API endpoints for advanced algebra operations
"""

from fastapi import APIRouter, HTTPException
from app.services.advanced_algebra import AdvancedAlgebraService
from app.models.advanced_models import MatrixRequest, BaseResponse
from typing import List
from app.exceptions.domain.mathematics import MathematicsError

router = APIRouter()
service = AdvancedAlgebraService()

@router.post("/matrix/determinant", response_model=None)
async def calculate_matrix_determinant(request: MatrixRequest):
    """Calculate matrix determinant"""
    try:
        result = service.matrix_determinant(request.matrix)
        return BaseResponse(
            success=True,
            message="Matrix determinant calculated successfully",
            data={"matrix": request.matrix, "determinant": result}
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/matrix/inverse", response_model=None)
async def calculate_matrix_inverse(request: MatrixRequest):
    """Calculate matrix inverse"""
    try:
        result = service.matrix_inverse(request.matrix)
        return BaseResponse(
            success=True,
            message="Matrix inverse calculated successfully",
            data={"matrix": request.matrix, "inverse": result}
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/matrix/eigenvalues", response_model=None)
async def calculate_matrix_eigenvalues(request: MatrixRequest):
    """Calculate matrix eigenvalues"""
    try:
        result = service.matrix_eigenvalues(request.matrix)
        return BaseResponse(
            success=True,
            message="Matrix eigenvalues calculated successfully",
            data={"matrix": request.matrix, "eigenvalues": result}
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/matrix/eigenvectors", response_model=None)
async def calculate_matrix_eigenvectors(request: MatrixRequest):
    """Calculate matrix eigenvectors"""
    try:
        result = service.matrix_eigenvectors(request.matrix)
        return BaseResponse(
            success=True,
            message="Matrix eigenvectors calculated successfully",
            data={"matrix": request.matrix, "eigenvectors": result}
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/polynomial/roots", response_model=BaseResponse)
async def calculate_polynomial_roots(coefficients: List[float]):
    """Calculate polynomial roots"""
    try:
        result = service.polynomial_roots(coefficients)
        return BaseResponse(
            success=True,
            message="Polynomial roots calculated successfully",
            data={"coefficients": coefficients, "roots": result}
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/complex/add", response_model=BaseResponse)
async def add_complex_numbers(real1: float, imag1: float, real2: float, imag2: float):
    """Add two complex numbers"""
    try:
        result = service.complex_operations(real1, imag1, real2, imag2, "add")
        return BaseResponse(
            success=True,
            message="Complex numbers added successfully",
            data={
                "complex1": {"real": real1, "imag": imag1},
                "complex2": {"real": real2, "imag": imag2},
                "result": result
            }
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/complex/multiply", response_model=BaseResponse)
async def multiply_complex_numbers(real1: float, imag1: float, real2: float, imag2: float):
    """Multiply two complex numbers"""
    try:
        result = service.complex_operations(real1, imag1, real2, imag2, "multiply")
        return BaseResponse(
            success=True,
            message="Complex numbers multiplied successfully",
            data={
                "complex1": {"real": real1, "imag": imag1},
                "complex2": {"real": real2, "imag": imag2},
                "result": result
            }
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/info")
async def get_algebra_info():
    """Get information about advanced algebra capabilities"""
    return {
        "description": "Advanced algebra service for Mathematics AI",
        "supported_operations": [
            "matrix_determinant",
            "matrix_inverse",
            "matrix_eigenvalues",
            "matrix_eigenvectors",
            "polynomial_roots",
            "complex_operations"
        ],
        "capabilities": [
            "Matrix operations (determinant, inverse, eigenvalues, eigenvectors)",
            "Polynomial root finding",
            "Complex number arithmetic",
            "Linear algebra computations"
        ]
    }
