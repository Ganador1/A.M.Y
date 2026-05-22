"""
Mathematics Domain - Consolidated API Router

Router consolidado para el dominio Mathematics de AXIOM.
Proporciona una interfaz unificada y optimizada para todos los servicios matemáticos
con balanceador de carga, cache inteligente y monitoreo de rendimiento.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
import asyncio
import time
from datetime import datetime

from ..models import BaseRequest, BaseResponse
from ..services.service_manager import mathematics_service_manager
from app.exceptions.domain.mathematics import MathematicsError


# Crear router principal
router = APIRouter(
    prefix="/mathematics",
    tags=["Mathematics", "Consolidated API", "Mathematical Services"],
    responses={404: {"description": "Not found"}}
)


@router.get("/", response_model=None)
async def get_mathematics_overview():
    """
    Obtener vista general del dominio Mathematics
    """
    try:
        overview = {
            "domain": "Mathematics",
            "description": "Dominio consolidado de servicios matemáticos avanzados",
            "version": "2.0.0",
            "features": [
                "Computación simbólica avanzada",
                "Álgebra computacional",
                "Computación numérica de alto rendimiento",
                "Análisis topológico de datos",
                "Computación cuántica matemática",
                "Machine learning matemático",
                "Motor de descubrimiento con IA",
                "Optimización matemática"
            ],
            "services": [
                "arithmetic", "topology", "sympy", "sagemath", "julia",
                "symengine", "discovery", "advanced_topology", "quantum", "ml"
            ],
            "capabilities": [
                "Symbolic computation", "Numerical analysis", "Algebraic geometry",
                "Topological data analysis", "Quantum algorithms", "Machine learning",
                "Mathematical discovery", "Optimization", "Cryptography", "Graph theory"
            ]
        }
        
        return BaseResponse(
            success=True,
            message="Mathematics domain overview retrieved successfully",
            data=overview
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=None)
async def get_system_status():
    """
    Obtener estado del sistema de servicios matemáticos
    """
    try:
        status = await mathematics_service_manager.get_service_status()
        
        return BaseResponse(
            success=True,
            message="System status retrieved successfully",
            data=status
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/capabilities", response_model=None)
async def get_all_capabilities():
    """
    Obtener capacidades de todos los servicios matemáticos
    """
    try:
        capabilities = await mathematics_service_manager.get_service_capabilities()
        
        return BaseResponse(
            success=True,
            message="All capabilities retrieved successfully",
            data=capabilities
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/capabilities/{service_name}", response_model=None)
async def get_service_capabilities(service_name: str):
    """
    Obtener capacidades de un servicio específico
    """
    try:
        capabilities = await mathematics_service_manager.get_service_capabilities(service_name)
        
        if "error" in capabilities:
            raise HTTPException(status_code=404, detail=capabilities["error"])
        
        return BaseResponse(
            success=True,
            message=f"Capabilities for {service_name} retrieved successfully",
            data=capabilities
        )
    except HTTPException:
        raise
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute/{service_name}/{operation}", response_model=None)
async def execute_operation(
    service_name: str,
    operation: str,
    request: BaseRequest,
    use_cache: bool = Query(True, description="Usar cache si está disponible")
):
    """
    Ejecutar operación en un servicio específico
    
    Parámetros:
    - service_name: Nombre del servicio (arithmetic, sympy, sagemath, etc.)
    - operation: Operación a ejecutar
    - use_cache: Usar cache para mejorar rendimiento
    """
    try:
        if not request.data:
            raise HTTPException(status_code=400, detail="Request data is required")
        
        result = await mathematics_service_manager.execute_operation(
            service_name=service_name,
            operation=operation,
            parameters=request.data,
            use_cache=use_cache
        )
        
        return BaseResponse(
            success=result.get("success", False),
            message=f"Operation {operation} executed on {service_name}",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-execute", response_model=None)
async def batch_execute(request: BaseRequest):
    """
    Ejecutar múltiples operaciones en paralelo
    
    Parámetros:
    - operations: Lista de operaciones a ejecutar
    """
    try:
        if not request.data or "operations" not in request.data:
            raise HTTPException(status_code=400, detail="Operations list is required")
        
        operations = request.data["operations"]
        if not isinstance(operations, list):
            raise HTTPException(status_code=400, detail="Operations must be a list")
        
        # Ejecutar operaciones en paralelo
        tasks = []
        for op in operations:
            if "service_name" in op and "operation" in op:
                task = mathematics_service_manager.execute_operation(
                    service_name=op["service_name"],
                    operation=op["operation"],
                    parameters=op.get("parameters", {}),
                    use_cache=op.get("use_cache", True)
                )
                tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Procesar resultados
        batch_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                batch_results.append({
                    "index": i,
                    "success": False,
                    "error": str(result)
                })
            else:
                batch_results.append({
                    "index": i,
                    "success": result.get("success", False),
                    "result": result
                })
        
        return BaseResponse(
            success=True,
            message=f"Batch execution completed for {len(operations)} operations",
            data={
                "total_operations": len(operations),
                "successful_operations": sum(1 for r in batch_results if r["success"]),
                "failed_operations": sum(1 for r in batch_results if not r["success"]),
                "results": batch_results
            }
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize", response_model=None)
async def optimize_system(background_tasks: BackgroundTasks):
    """
    Optimizar rendimiento del sistema
    """
    try:
        # Ejecutar optimización en background
        background_tasks.add_task(mathematics_service_manager.optimize_performance)
        
        return BaseResponse(
            success=True,
            message="System optimization started in background",
            data={"status": "optimization_started"}
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=None)
async def health_check():
    """
    Verificación de salud del sistema
    """
    try:
        health = await mathematics_service_manager.health_check()
        
        return BaseResponse(
            success=True,
            message="Health check completed",
            data=health
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics", response_model=BaseResponse)
async def get_statistics():
    """
    Obtener estadísticas del sistema
    """
    try:
        stats = mathematics_service_manager.get_statistics()
        
        return BaseResponse(
            success=True,
            message="Statistics retrieved successfully",
            data=stats
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/clear", response_model=BaseResponse)
async def clear_cache():
    """
    Limpiar cache del sistema
    """
    try:
        mathematics_service_manager.cache.clear()
        
        return BaseResponse(
            success=True,
            message="Cache cleared successfully",
            data={"cache_size": 0}
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache/info", response_model=BaseResponse)
async def get_cache_info():
    """
    Obtener información del cache
    """
    try:
        cache_info = {
            "cache_size": len(mathematics_service_manager.cache),
            "cache_ttl": mathematics_service_manager.cache_ttl,
            "cache_keys": list(mathematics_service_manager.cache.keys())[:10]  # Primeros 10
        }
        
        return BaseResponse(
            success=True,
            message="Cache information retrieved successfully",
            data=cache_info
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services", response_model=BaseResponse)
async def list_services():
    """
    Listar todos los servicios disponibles
    """
    try:
        services = []
        for name, info in mathematics_service_manager.service_info.items():
            services.append({
                "name": name,
                "version": info.version,
                "status": info.status.value,
                "capabilities": info.capabilities,
                "performance_score": info.performance_score,
                "error_count": info.error_count
            })
        
        return BaseResponse(
            success=True,
            message="Services listed successfully",
            data={"services": services}
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/services/{service_name}/restart", response_model=BaseResponse)
async def restart_service(service_name: str):
    """
    Reiniciar un servicio específico
    """
    try:
        if service_name not in mathematics_service_manager.services:
            raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
        
        # Reiniciar servicio (simulado)
        mathematics_service_manager.service_info[service_name].error_count = 0
        mathematics_service_manager.service_info[service_name].status = mathematics_service_manager.ServiceStatus.ACTIVE
        
        return BaseResponse(
            success=True,
            message=f"Service {service_name} restarted successfully",
            data={"service": service_name, "status": "restarted"}
        )
    except HTTPException:
        raise
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoints de documentación y ayuda
@router.get("/help", response_model=BaseResponse)
async def get_help():
    """
    Obtener ayuda y documentación de la API
    """
    try:
        help_info = {
            "api_version": "2.0.0",
            "endpoints": {
                "GET /": "Vista general del dominio",
                "GET /status": "Estado del sistema",
                "GET /capabilities": "Capacidades de todos los servicios",
                "GET /capabilities/{service}": "Capacidades de un servicio específico",
                "POST /execute/{service}/{operation}": "Ejecutar operación",
                "POST /batch-execute": "Ejecutar múltiples operaciones",
                "POST /optimize": "Optimizar sistema",
                "GET /health": "Verificación de salud",
                "GET /statistics": "Estadísticas del sistema",
                "POST /cache/clear": "Limpiar cache",
                "GET /cache/info": "Información del cache",
                "GET /services": "Listar servicios",
                "POST /services/{service}/restart": "Reiniciar servicio"
            },
            "services": {
                "arithmetic": "Operaciones aritméticas básicas",
                "sympy": "Computación simbólica avanzada",
                "sagemath": "Álgebra computacional",
                "julia": "Computación numérica de alto rendimiento",
                "symengine": "Computación simbólica optimizada",
                "discovery": "Motor de descubrimiento matemático",
                "advanced_topology": "Análisis topológico avanzado",
                "quantum": "Computación cuántica matemática",
                "ml": "Machine learning matemático"
            },
            "examples": {
                "symbolic_computation": {
                    "service": "sympy",
                    "operation": "simplify",
                    "parameters": {"expression": "x^2 + 2*x + 1"}
                },
                "numerical_analysis": {
                    "service": "julia",
                    "operation": "root_finding",
                    "parameters": {"function": "x^2 - 2", "initial_guess": 1.0}
                },
                "topological_analysis": {
                    "service": "advanced_topology",
                    "operation": "vietoris_rips",
                    "parameters": {"points": [[0, 0], [1, 1], [2, 0]]}
                }
            }
        }
        
        return BaseResponse(
            success=True,
            message="Help information retrieved successfully",
            data=help_info
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))






