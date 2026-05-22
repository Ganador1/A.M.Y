"""
Advanced Topology Router for AXIOM Mathematics Domain

Router para endpoints de análisis topológico avanzado utilizando Gudhi.
Proporciona acceso a homología persistente, complejos de Vietoris-Rips,
algoritmo Mapper y análisis de formas topológicas.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional, List
import asyncio

from ..models import BaseRequest, BaseResponse
from ..services.advanced_topology_service import AdvancedTopologyService
from app.exceptions.domain.mathematics import MathematicsError

# Crear router
router = APIRouter(
    prefix="/topology",
    tags=["Advanced Topology", "Persistent Homology", "TDA"],
    responses={404: {"description": "Not found"}}
)

# Instancia del servicio
topology_service = AdvancedTopologyService()


@router.get("/capabilities", response_model=None)
async def get_topology_capabilities():
    """
    Obtener capacidades del servicio de topología avanzada
    """
    try:
        capabilities = topology_service.get_capabilities()
        return BaseResponse(
            success=True,
            message="Advanced topology capabilities retrieved successfully",
            data=capabilities
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/persistent-homology/{operation}", response_model=None)
async def persistent_homology_operation(
    operation: str,
    request: BaseRequest
):
    """
    Operaciones de homología persistente con Gudhi
    
    Operaciones disponibles:
    - vietoris_rips: Complejo de Vietoris-Rips
    - alpha_complex: Complejo Alpha
    - witness_complex: Complejo Witness
    """
    try:
        result = await topology_service.persistent_homology(
            operation=operation,
            parameters=request.data or {}
        )
        
        return BaseResponse(
            success=result["success"],
            message=f"Persistent homology operation '{operation}' completed",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mapper/{operation}", response_model=BaseResponse)
async def mapper_operation(
    operation: str,
    request: BaseRequest
):
    """
    Operaciones del algoritmo Mapper
    
    Operaciones disponibles:
    - mapper_analysis: Análisis Mapper
    """
    try:
        result = await topology_service.mapper_algorithm(
            operation=operation,
            parameters=request.data or {}
        )
        
        return BaseResponse(
            success=result["success"],
            message=f"Mapper operation '{operation}' completed",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/distance-metrics/{operation}", response_model=BaseResponse)
async def distance_metrics_operation(
    operation: str,
    request: BaseRequest
):
    """
    Operaciones de métricas de distancia topológica
    
    Operaciones disponibles:
    - bottleneck_distance: Distancia bottleneck
    - wasserstein_distance: Distancia Wasserstein
    """
    try:
        result = await topology_service.distance_metrics(
            operation=operation,
            parameters=request.data or {}
        )
        
        return BaseResponse(
            success=result["success"],
            message=f"Distance metrics operation '{operation}' completed",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/topological-features/{operation}", response_model=BaseResponse)
async def topological_features_operation(
    operation: str,
    request: BaseRequest
):
    """
    Operaciones de extracción de características topológicas
    
    Operaciones disponibles:
    - betti_numbers: Números de Betti
    - persistence_diagram: Diagrama de persistencia
    """
    try:
        result = await topology_service.topological_features(
            operation=operation,
            parameters=request.data or {}
        )
        
        return BaseResponse(
            success=result["success"],
            message=f"Topological features operation '{operation}' completed",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-shape", response_model=BaseResponse)
async def analyze_shape(request: BaseRequest):
    """
    Análisis completo de forma topológica
    
    Parámetros:
    - points: Puntos de datos para analizar
    - analysis_type: Tipo de análisis (vietoris_rips, alpha_complex, mapper)
    - parameters: Parámetros adicionales
    """
    try:
        if not request.data:
            raise HTTPException(status_code=400, detail="Request data is required")
        
        points = request.data.get("points")
        analysis_type = request.data.get("analysis_type", "vietoris_rips")
        parameters = request.data.get("parameters", {})
        
        if points is None:
            raise HTTPException(status_code=400, detail="Points data is required")
        
        # Realizar análisis topológico
        result = await topology_service.persistent_homology(
            operation=analysis_type,
            parameters={"points": points, **parameters}
        )
        
        return BaseResponse(
            success=result["success"],
            message=f"Shape analysis completed using {analysis_type}",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare-shapes", response_model=BaseResponse)
async def compare_shapes(request: BaseRequest):
    """
    Comparar formas topológicas usando métricas de distancia
    
    Parámetros:
    - shape1: Primera forma (puntos o persistencia)
    - shape2: Segunda forma (puntos o persistencia)
    - metric: Métrica a usar (bottleneck, wasserstein)
    """
    try:
        if not request.data:
            raise HTTPException(status_code=400, detail="Request data is required")
        
        shape1 = request.data.get("shape1")
        shape2 = request.data.get("shape2")
        metric = request.data.get("metric", "bottleneck")
        
        if shape1 is None or shape2 is None:
            raise HTTPException(status_code=400, detail="Both shapes are required")
        
        # Calcular distancia entre formas
        if metric == "bottleneck":
            result = await topology_service.distance_metrics(
                operation="bottleneck_distance",
                parameters={"persistence1": shape1, "persistence2": shape2}
            )
        elif metric == "wasserstein":
            result = await topology_service.distance_metrics(
                operation="wasserstein_distance",
                parameters={"persistence1": shape1, "persistence2": shape2}
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported metric: {metric}")
        
        return BaseResponse(
            success=result["success"],
            message=f"Shape comparison completed using {metric} distance",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def topology_status():
    """
    Estado del servicio de topología avanzada
    """
    return {
        "service": "Advanced Topology",
        "status": "active",
        "gudhi_available": topology_service.gudhi_available,
        "sklearn_available": topology_service.sklearn_available,
        "version": topology_service.version,
        "simulation_mode": not topology_service.gudhi_available
    }






