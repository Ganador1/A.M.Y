"""
Quantum Algorithms Router
========================

Router FastAPI para el servicio de algoritmos cuánticos híbridos.

Endpoints disponibles:
- POST /qaoa/optimize: Ejecutar optimización QAOA
- POST /vqe/ground-state: Calcular estado fundamental con VQE
- POST /quantum-advantage: Analizar ventaja cuántica
- GET /circuits: Listar circuitos disponibles
- GET /backends: Listar backends cuánticos
- GET /health: Estado del servicio
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Union
import numpy as np
import logging
from datetime import datetime

from ..quantum.quantum_algorithms_service import QuantumAlgorithmsService
from app.exceptions.domain.physics import QuantumError

logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(prefix="/quantum-algorithms", tags=["Quantum Algorithms"])

# Instancia del servicio
quantum_service = QuantumAlgorithmsService()


# Modelos Pydantic
class QAOARequest(BaseModel):
    """Request para optimización QAOA."""
    problem_type: str = Field(
        ...,
        description="Tipo de problema (max_cut, tsp, portfolio)",
        example="max_cut"
    )
    problem_data: Dict[str, Any] = Field(
        ...,
        description="Datos del problema específico",
        example={
            "graph": [[0, 1, 1], [1, 0, 1], [1, 1, 0]],
            "weights": [1.0, 1.0, 1.0]
        }
    )
    p_layers: int = Field(
        default=2,
        description="Número de capas QAOA",
        ge=1,
        le=10,
        example=2
    )
    optimizer: str = Field(
        default="COBYLA",
        description="Optimizador clásico",
        example="COBYLA"
    )
    max_iterations: int = Field(
        default=100,
        description="Máximo número de iteraciones",
        ge=10,
        le=1000,
        example=100
    )
    backend: str = Field(
        default="qasm_simulator",
        description="Backend cuántico",
        example="qasm_simulator"
    )
    shots: int = Field(
        default=1024,
        description="Número de shots",
        ge=100,
        le=10000,
        example=1024
    )

class VQERequest(BaseModel):
    """Request para cálculo VQE."""
    hamiltonian: Dict[str, Any] = Field(
        ...,
        description="Hamiltoniano del sistema",
        example={
            "pauli_strings": ["ZZ", "XX", "YY"],
            "coefficients": [1.0, 0.5, 0.5]
        }
    )
    ansatz: str = Field(
        default="EfficientSU2",
        description="Tipo de ansatz",
        example="EfficientSU2"
    )
    optimizer: str = Field(
        default="SLSQP",
        description="Optimizador clásico",
        example="SLSQP"
    )
    max_iterations: int = Field(
        default=200,
        description="Máximo número de iteraciones",
        ge=50,
        le=1000,
        example=200
    )
    backend: str = Field(
        default="statevector_simulator",
        description="Backend cuántico",
        example="statevector_simulator"
    )
    initial_point: Optional[List[float]] = Field(
        default=None,
        description="Punto inicial para optimización",
        example=None
    )

class QuantumAdvantageRequest(BaseModel):
    """Request para análisis de ventaja cuántica."""
    problem_size: int = Field(
        ...,
        description="Tamaño del problema",
        ge=2,
        le=20,
        example=10
    )
    problem_type: str = Field(
        ...,
        description="Tipo de problema",
        example="optimization"
    )
    classical_methods: List[str] = Field(
        default=["brute_force", "simulated_annealing"],
        description="Métodos clásicos a comparar",
        example=["brute_force", "simulated_annealing"]
    )
    quantum_methods: List[str] = Field(
        default=["qaoa", "vqe"],
        description="Métodos cuánticos a evaluar",
        example=["qaoa", "vqe"]
    )
    metrics: List[str] = Field(
        default=["time", "accuracy", "resources"],
        description="Métricas a evaluar",
        example=["time", "accuracy", "resources"]
    )

class QAOAResponse(BaseModel):
    """Response de optimización QAOA."""
    success: bool = Field(description="Indica si la optimización fue exitosa")
    problem_type: str = Field(description="Tipo de problema resuelto")
    optimal_parameters: List[float] = Field(description="Parámetros óptimos encontrados")
    optimal_value: float = Field(description="Valor óptimo de la función objetivo")
    optimal_solution: List[int] = Field(description="Solución óptima encontrada")
    convergence_data: Dict[str, Any] = Field(description="Datos de convergencia")
    circuit_depth: int = Field(description="Profundidad del circuito")
    execution_time: float = Field(description="Tiempo de ejecución en segundos")
    backend_used: str = Field(description="Backend utilizado")
    shots_used: int = Field(description="Número de shots utilizados")
    error: Optional[str] = Field(description="Mensaje de error si aplica")

class VQEResponse(BaseModel):
    """Response de cálculo VQE."""
    success: bool = Field(description="Indica si el cálculo fue exitoso")
    ground_state_energy: float = Field(description="Energía del estado fundamental")
    optimal_parameters: List[float] = Field(description="Parámetros óptimos del ansatz")
    eigenstate: Optional[List[complex]] = Field(description="Vector de estado propio")
    convergence_data: Dict[str, Any] = Field(description="Datos de convergencia")
    hamiltonian_info: Dict[str, Any] = Field(description="Información del Hamiltoniano")
    ansatz_info: Dict[str, Any] = Field(description="Información del ansatz")
    execution_time: float = Field(description="Tiempo de ejecución en segundos")
    backend_used: str = Field(description="Backend utilizado")
    error: Optional[str] = Field(description="Mensaje de error si aplica")

class QuantumAdvantageResponse(BaseModel):
    """Response de análisis de ventaja cuántica."""
    success: bool = Field(description="Indica si el análisis fue exitoso")
    problem_size: int = Field(description="Tamaño del problema analizado")
    classical_results: Dict[str, Any] = Field(description="Resultados de métodos clásicos")
    quantum_results: Dict[str, Any] = Field(description="Resultados de métodos cuánticos")
    advantage_analysis: Dict[str, Any] = Field(description="Análisis de ventaja cuántica")
    recommendations: List[str] = Field(description="Recomendaciones basadas en el análisis")
    scalability_projection: Dict[str, Any] = Field(description="Proyección de escalabilidad")
    error: Optional[str] = Field(description="Mensaje de error si aplica")


# Endpoints
@router.post("/qaoa/optimize", response_model=QAOAResponse)
async def optimize_with_qaoa(request: QAOARequest):
    """
    Ejecuta optimización usando QAOA (Quantum Approximate Optimization Algorithm).
    
    Resuelve problemas de optimización combinatoria usando un enfoque híbrido
    cuántico-clásico con el algoritmo QAOA.
    """
    try:
        logger.info(f"Iniciando optimización QAOA para problema: {request.problem_type}")
        
        # Ejecutar QAOA
        result = await quantum_service.run_qaoa(
            problem_type=request.problem_type,
            problem_data=request.problem_data,
            p_layers=request.p_layers,
            optimizer=request.optimizer,
            max_iterations=request.max_iterations,
            backend=request.backend,
            shots=request.shots
        )
        
        if result["success"]:
            return QAOAResponse(
                success=True,
                problem_type=request.problem_type,
                optimal_parameters=result["optimal_parameters"],
                optimal_value=result["optimal_value"],
                optimal_solution=result["optimal_solution"],
                convergence_data=result["convergence_data"],
                circuit_depth=result["circuit_depth"],
                execution_time=result["execution_time"],
                backend_used=request.backend,
                shots_used=request.shots
            )
        else:
            return QAOAResponse(
                success=False,
                problem_type=request.problem_type,
                optimal_parameters=[],
                optimal_value=0.0,
                optimal_solution=[],
                convergence_data={},
                circuit_depth=0,
                execution_time=0.0,
                backend_used=request.backend,
                shots_used=request.shots,
                error=result.get("error", "Error desconocido en QAOA")
            )
            
    except QuantumError as e:
        logger.error(f"Error en optimización QAOA: {e}")
        raise HTTPException(status_code=500, detail=f"Error en QAOA: {str(e)}")

@router.post("/vqe/ground-state", response_model=VQEResponse)
async def calculate_ground_state_vqe(request: VQERequest):
    """
    Calcula el estado fundamental usando VQE (Variational Quantum Eigensolver).
    
    Encuentra el estado fundamental de un Hamiltoniano dado usando
    un enfoque variacional híbrido cuántico-clásico.
    """
    try:
        logger.info("Iniciando cálculo VQE para estado fundamental")
        
        # Ejecutar VQE
        result = await quantum_service.run_vqe(
            hamiltonian=request.hamiltonian,
            ansatz=request.ansatz,
            optimizer=request.optimizer,
            max_iterations=request.max_iterations,
            backend=request.backend,
            initial_point=request.initial_point
        )
        
        if result["success"]:
            return VQEResponse(
                success=True,
                ground_state_energy=result["ground_state_energy"],
                optimal_parameters=result["optimal_parameters"],
                eigenstate=result.get("eigenstate"),
                convergence_data=result["convergence_data"],
                hamiltonian_info=result["hamiltonian_info"],
                ansatz_info=result["ansatz_info"],
                execution_time=result["execution_time"],
                backend_used=request.backend
            )
        else:
            return VQEResponse(
                success=False,
                ground_state_energy=0.0,
                optimal_parameters=[],
                eigenstate=None,
                convergence_data={},
                hamiltonian_info={},
                ansatz_info={},
                execution_time=0.0,
                backend_used=request.backend,
                error=result.get("error", "Error desconocido en VQE")
            )
            
    except QuantumError as e:
        logger.error(f"Error en cálculo VQE: {e}")
        raise HTTPException(status_code=500, detail=f"Error en VQE: {str(e)}")

@router.post("/quantum-advantage", response_model=QuantumAdvantageResponse)
async def analyze_quantum_advantage(request: QuantumAdvantageRequest):
    """
    Analiza la ventaja cuántica comparando métodos cuánticos vs clásicos.
    
    Evalúa el rendimiento de algoritmos cuánticos frente a métodos clásicos
    para determinar cuándo existe ventaja cuántica.
    """
    try:
        logger.info(f"Analizando ventaja cuántica para problema de tamaño {request.problem_size}")
        
        # Ejecutar análisis de ventaja cuántica
        result = await quantum_service.analyze_quantum_advantage(
            problem_size=request.problem_size,
            problem_type=request.problem_type,
            classical_methods=request.classical_methods,
            quantum_methods=request.quantum_methods,
            metrics=request.metrics
        )
        
        if result["success"]:
            return QuantumAdvantageResponse(
                success=True,
                problem_size=request.problem_size,
                classical_results=result["classical_results"],
                quantum_results=result["quantum_results"],
                advantage_analysis=result["advantage_analysis"],
                recommendations=result["recommendations"],
                scalability_projection=result["scalability_projection"]
            )
        else:
            return QuantumAdvantageResponse(
                success=False,
                problem_size=request.problem_size,
                classical_results={},
                quantum_results={},
                advantage_analysis={},
                recommendations=[],
                scalability_projection={},
                error=result.get("error", "Error en análisis de ventaja cuántica")
            )
            
    except QuantumError as e:
        logger.error(f"Error en análisis de ventaja cuántica: {e}")
        raise HTTPException(status_code=500, detail=f"Error en análisis: {str(e)}")

@router.get("/circuits")
async def get_available_circuits():
    """Lista los tipos de circuitos cuánticos disponibles."""
    try:
        circuits = await quantum_service.get_available_circuits()
        return {
            "success": True,
            "circuits": circuits,
            "total": len(circuits)
        }
    except QuantumError as e:
        logger.error(f"Error obteniendo circuitos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/backends")
async def get_quantum_backends():
    """Lista los backends cuánticos disponibles."""
    try:
        backends = await quantum_service.get_available_backends()
        return {
            "success": True,
            "backends": backends,
            "total": len(backends)
        }
    except QuantumError as e:
        logger.error(f"Error obteniendo backends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Verifica el estado del servicio de algoritmos cuánticos."""
    try:
        health = await quantum_service.health_check()
        return health
    except QuantumError as e:
        logger.error(f"Error en health check: {e}")
        return {
            "service": "quantum_algorithms",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/examples")
async def get_usage_examples():
    """Proporciona ejemplos de uso para los endpoints."""
    return {
        "qaoa_example": {
            "problem_type": "max_cut",
            "problem_data": {
                "graph": [[0, 1, 1], [1, 0, 1], [1, 1, 0]],
                "weights": [1.0, 1.0, 1.0]
            },
            "p_layers": 2,
            "optimizer": "COBYLA",
            "max_iterations": 100
        },
        "vqe_example": {
            "hamiltonian": {
                "pauli_strings": ["ZZ", "XX", "YY"],
                "coefficients": [1.0, 0.5, 0.5]
            },
            "ansatz": "EfficientSU2",
            "optimizer": "SLSQP",
            "max_iterations": 200
        },
        "quantum_advantage_example": {
            "problem_size": 10,
            "problem_type": "optimization",
            "classical_methods": ["brute_force", "simulated_annealing"],
            "quantum_methods": ["qaoa", "vqe"],
            "metrics": ["time", "accuracy", "resources"]
        }
    }