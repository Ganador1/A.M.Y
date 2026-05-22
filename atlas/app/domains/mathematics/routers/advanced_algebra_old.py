"""
Advanced Algebra Router
API endpoints for advanced algebra operations.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.models.advanced_models import (
from app.exceptions.domain.mathematics import MathematicsError
    MatrixRequest, MatrixResult, MatrixResponse,
    ComplexNumberRequest, ComplexNumberResult, ComplexNumberResponse,
    PolynomialRequest, PolynomialResult, PolynomialResponse,
    LinearSystemRequest, LinearSystemResponse,
    BaseResponse
)
from app.services.advanced_algebra import AdvancedAlgebraService

router = APIRouter()
algebra_service = AdvancedAlgebraService()

@router.post("/matrix/determinant", response_model=BaseResponse)
async def matrix_determinant(request: MatrixRequest):
    """Calculate matrix determinant"""
    try:
        result = algebra_service.matrix_determinant(request.matrix)
        return BaseResponse(
            success=True,
            message="Matrix determinant calculated successfully",
            data={"operation": "determinant", "result": result}
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/matrix/inverse", response_model=BaseResponse)
async def matrix_inverse(request: MatrixRequest):
    """Calculate matrix inverse"""
    try:
        result = algebra_service.matrix_inverse(request.matrix)
        return BaseResponse(
            success=True,
            message="Matrix inverse calculated successfully",
            data={"operation": "inverse", "result": result}
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/matrix/eigenvalues", response_model=MatrixResponse)
async def matrix_eigenvalues(request: MatrixRequest):
    """Calculate matrix eigenvalues"""
    try:
        result = algebra_service.matrix_eigenvalues(request.matrix)
        return MatrixResponse(operation="eigenvalues", result=result)
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/matrix/eigenvectors", response_model=MatrixResponse)
async def matrix_eigenvectors(request: MatrixRequest):
    """Calculate matrix eigenvectors"""
    try:
        result = algebra_service.matrix_eigenvectors(request.matrix)
        return MatrixResponse(operation="eigenvectors", result=result)
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/complex/operations", response_model=ComplexNumberResponse)
async def complex_operations(request: ComplexNumberRequest):
    """Perform complex number operations"""
    try:
        result = algebra_service.complex_operations(
            request.real1, request.imag1,
            request.real2, request.imag2,
            request.operation
        )
        return ComplexNumberResponse(
            operation=request.operation,
            result=result,
            representation=result.get("result", "")
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/polynomial/roots", response_model=PolynomialResponse)
async def polynomial_roots(request: PolynomialRequest):
    """Find polynomial roots"""
    try:
        if not request.coefficients:
            raise HTTPException(status_code=400, detail="Coefficients are required")
        
        result = algebra_service.polynomial_roots(request.coefficients)
        return PolynomialResponse(
            operation="roots",
            result=result,
            original_polynomial=str(request.coefficients),
            degree=len(request.coefficients) - 1
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/polynomial/expand", response_model=PolynomialResponse)
async def polynomial_expand(request: PolynomialRequest):
    """Expand polynomial expression"""
    try:
        if not request.expression:
            raise HTTPException(status_code=400, detail="Expression is required")
        
        result = algebra_service.polynomial_expand(request.expression)
        return PolynomialResponse(
            operation="expand",
            result=result,
            original_polynomial=request.expression,
            degree=0  # This would need to be calculated
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/linear_system/solve", response_model=LinearSystemResponse)
async def solve_linear_system(request: LinearSystemRequest):
    """Solve linear system of equations"""
    try:
        result = algebra_service.solve_linear_system(
            request.coefficient_matrix,
            request.constants
        )
        return LinearSystemResponse(
            method="direct",
            result=result,
            system_type="unique",
            steps=["Solved using numpy.linalg.solve"]
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/linear_system/gauss_elimination", response_model=LinearSystemResponse)
async def gauss_elimination(request: LinearSystemRequest):
    """Solve using Gaussian elimination"""
    try:
        result = algebra_service.gauss_elimination(
            request.coefficient_matrix,
            request.constants
        )
        return LinearSystemResponse(
            method="gaussian_elimination",
            result=result,
            system_type="unique",
            steps=["Applied Gaussian elimination with back substitution"]
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))
