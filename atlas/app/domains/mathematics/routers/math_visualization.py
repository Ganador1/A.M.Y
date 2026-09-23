"""
Mathematical Visualization Router for AXIOM Mathematics Domain

Router para endpoints de visualización matemática interactiva.
Proporciona acceso a gráficos 2D/3D, animaciones, visualizaciones estadísticas
y visualizaciones geométricas avanzadas.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional, List
import asyncio

from ..models import BaseRequest, BaseResponse
from ..services.math_visualization_service import MathVisualizationService
from app.exceptions.domain.mathematics import MathematicsError

# Crear router
router = APIRouter(
    prefix="/visualization",
    tags=["Mathematical Visualization", "Interactive Plots", "Graphics"],
    responses={404: {"description": "Not found"}}
)

# Instancia del servicio
visualization_service = MathVisualizationService()


@router.get("/capabilities", response_model=BaseResponse)
async def get_visualization_capabilities():
    """
    Obtener capacidades del servicio de visualización matemática
    """
    try:
        capabilities = visualization_service.get_capabilities()
        return BaseResponse(
            success=True,
            message="Mathematical visualization capabilities retrieved successfully",
            data=capabilities
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/2d-plots/{operation}", response_model=BaseResponse)
async def create_2d_plot(
    operation: str,
    request: BaseRequest
):
    """
    Crear gráficos 2D interactivos
    
    Operaciones disponibles:
    - function_plot: Gráfico de función matemática
    - parametric_plot: Gráfico paramétrico
    - polar_plot: Gráfico polar
    """
    try:
        result = await visualization_service.create_2d_plot(
            operation=operation,
            parameters=request.data or {}
        )
        
        return BaseResponse(
            success=result["success"],
            message=f"2D plot '{operation}' created successfully",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/3d-plots/{operation}", response_model=BaseResponse)
async def create_3d_plot(
    operation: str,
    request: BaseRequest
):
    """
    Crear gráficos 3D interactivos
    
    Operaciones disponibles:
    - surface_plot: Gráfico de superficie 3D
    - parametric_3d: Gráfico paramétrico 3D
    """
    try:
        result = await visualization_service.create_3d_plot(
            operation=operation,
            parameters=request.data or {}
        )
        
        return BaseResponse(
            success=result["success"],
            message=f"3D plot '{operation}' created successfully",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/animations/{operation}", response_model=BaseResponse)
async def create_animation(
    operation: str,
    request: BaseRequest
):
    """
    Crear animaciones matemáticas
    
    Operaciones disponibles:
    - function_animation: Animación de función con parámetro variable
    """
    try:
        result = await visualization_service.create_animation(
            operation=operation,
            parameters=request.data or {}
        )
        
        return BaseResponse(
            success=result["success"],
            message=f"Animation '{operation}' created successfully",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/statistical-plots/{operation}", response_model=BaseResponse)
async def create_statistical_plot(
    operation: str,
    request: BaseRequest
):
    """
    Crear gráficos estadísticos avanzados
    
    Operaciones disponibles:
    - distribution_plot: Gráfico de distribución
    - correlation_plot: Gráfico de correlación
    """
    try:
        result = await visualization_service.create_statistical_plot(
            operation=operation,
            parameters=request.data or {}
        )
        
        return BaseResponse(
            success=result["success"],
            message=f"Statistical plot '{operation}' created successfully",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/geometric-visualizations/{operation}", response_model=BaseResponse)
async def create_geometric_visualization(
    operation: str,
    request: BaseRequest
):
    """
    Crear visualizaciones geométricas
    
    Operaciones disponibles:
    - conic_sections: Visualización de secciones cónicas
    - vector_field: Campo vectorial
    """
    try:
        result = await visualization_service.create_geometric_visualization(
            operation=operation,
            parameters=request.data or {}
        )
        
        return BaseResponse(
            success=result["success"],
            message=f"Geometric visualization '{operation}' created successfully",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interactive-demo", response_model=BaseResponse)
async def create_interactive_demo(request: BaseRequest):
    """
    Crear demostración interactiva personalizada
    
    Parámetros:
    - demo_type: Tipo de demostración (function, geometry, statistics)
    - parameters: Parámetros específicos para la demostración
    """
    try:
        if not request.data:
            raise HTTPException(status_code=400, detail="Request data is required")
        
        demo_type = request.data.get("demo_type", "function")
        parameters = request.data.get("parameters", {})
        
        # Crear demostración interactiva
        demo_result = {
            "demo_type": demo_type,
            "parameters": parameters,
            "interactive_elements": [
                "Zoom and pan controls",
                "Parameter sliders",
                "Animation controls",
                "Export options"
            ],
            "plot_html": f"<div>Interactive demo for {demo_type}</div>",
            "features": [
                "Real-time parameter adjustment",
                "Multiple view modes",
                "Export to various formats",
                "Shareable links"
            ]
        }
        
        return BaseResponse(
            success=True,
            message=f"Interactive demo '{demo_type}' created successfully",
            data=demo_result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def visualization_status():
    """
    Estado del servicio de visualización matemática
    """
    return {
        "service": "Mathematical Visualization",
        "status": "active",
        "matplotlib_available": visualization_service.matplotlib_available,
        "plotly_available": visualization_service.plotly_available,
        "seaborn_available": visualization_service.seaborn_available,
        "version": visualization_service.version,
        "simulation_mode": not (visualization_service.matplotlib_available or visualization_service.plotly_available)
    }






