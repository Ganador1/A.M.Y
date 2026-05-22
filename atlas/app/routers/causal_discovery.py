"""
Causal Discovery API Router
===========================

Router FastAPI para el servicio de descubrimiento causal.

Endpoints disponibles:
- POST /discover-structure: Descubre estructura causal en datos
- POST /estimate-effect: Estima efectos causales
- POST /validate-assumptions: Valida supuestos causales
- GET /algorithms: Lista algoritmos disponibles
- GET /health: Estado del servicio
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import pandas as pd
import logging

from app.services.causal_discovery_service import CausalDiscoveryService
from app.exceptions.domain.biology import BiologyError

logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(prefix="/causal-discovery", tags=["Causal Discovery"])

# Instancia del servicio
causal_service = CausalDiscoveryService()


# Modelos Pydantic
class CausalDiscoveryRequest(BaseModel):
    """Request para descubrimiento de estructura causal."""
    data: Dict[str, List[float]] = Field(
        ...,
        description="Datos en formato {variable: [valores]}",
        example={
            "X": [1.0, 2.0, 3.0, 4.0, 5.0],
            "Y": [2.0, 4.0, 6.0, 8.0, 10.0],
            "Z": [1.0, 1.0, 2.0, 2.0, 3.0]
        }
    )
    algorithm: str = Field(
        default="pc",
        description="Algoritmo de descubrimiento causal",
        example="pc"
    )
    alpha: Optional[float] = Field(
        default=0.05,
        description="Nivel de significancia",
        ge=0.001,
        le=0.5,
        example=0.05
    )
    max_cond_vars: Optional[int] = Field(
        default=3,
        description="Máximo número de variables condicionantes",
        ge=0,
        le=10,
        example=3
    )


class CausalEffectRequest(BaseModel):
    """Request para estimación de efectos causales."""
    data: Dict[str, List[float]] = Field(
        ...,
        description="Datos en formato {variable: [valores]}",
        example={
            "treatment": [0.0, 1.0, 0.0, 1.0, 0.0],
            "outcome": [1.0, 3.0, 2.0, 4.0, 1.5],
            "confounder": [1.0, 2.0, 1.5, 2.5, 1.2]
        }
    )
    treatment: str = Field(
        ...,
        description="Variable de tratamiento",
        example="treatment"
    )
    outcome: str = Field(
        ...,
        description="Variable de resultado",
        example="outcome"
    )
    confounders: Optional[List[str]] = Field(
        default=None,
        description="Lista de variables confounders",
        example=["confounder"]
    )
    method: str = Field(
        default="backdoor",
        description="Método de estimación causal",
        example="backdoor"
    )


class AssumptionValidationRequest(BaseModel):
    """Request para validación de supuestos causales."""
    data: Dict[str, List[float]] = Field(
        ...,
        description="Datos en formato {variable: [valores]}"
    )
    causal_graph: Dict[str, Any] = Field(
        ...,
        description="Grafo causal previamente descubierto"
    )
    treatment: str = Field(
        ...,
        description="Variable de tratamiento"
    )
    outcome: str = Field(
        ...,
        description="Variable de resultado"
    )


class CausalDiscoveryResponse(BaseModel):
    """Response para descubrimiento causal."""
    success: bool = Field(description="Indica si la operación fue exitosa")
    algorithm: str = Field(description="Algoritmo utilizado")
    variables: List[str] = Field(description="Variables analizadas")
    edges: List[List[str]] = Field(description="Edges causales encontrados")
    adjacency_matrix: Optional[List[List[float]]] = Field(description="Matriz de adyacencia")
    statistics: Dict[str, Any] = Field(description="Estadísticas del grafo")
    execution_time: Optional[float] = Field(description="Tiempo de ejecución en segundos")
    error: Optional[str] = Field(description="Mensaje de error si aplica")


class CausalEffectResponse(BaseModel):
    """Response para estimación de efectos causales."""
    success: bool = Field(description="Indica si la operación fue exitosa")
    treatment: str = Field(description="Variable de tratamiento")
    outcome: str = Field(description="Variable de resultado")
    method: str = Field(description="Método utilizado")
    ate: Optional[float] = Field(description="Average Treatment Effect")
    confidence_interval: Optional[List[float]] = Field(description="Intervalo de confianza")
    p_value: Optional[float] = Field(description="P-valor de la estimación")
    statistics: Dict[str, Any] = Field(description="Estadísticas adicionales")
    error: Optional[str] = Field(description="Mensaje de error si aplica")


class AssumptionValidationResponse(BaseModel):
    """Response para validación de supuestos."""
    success: bool = Field(description="Indica si la operación fue exitosa")
    overall_validity: str = Field(description="Validez general de los supuestos")
    positivity: Dict[str, Any] = Field(description="Validación de positividad")
    overlap: Dict[str, Any] = Field(description="Validación de overlap")
    no_unmeasured_confounding: Dict[str, Any] = Field(description="Validación de confounding")
    consistency: Dict[str, Any] = Field(description="Validación de consistencia")
    error: Optional[str] = Field(description="Mensaje de error si aplica")


# Endpoints
@router.post("/discover-structure", response_model=CausalDiscoveryResponse)
async def discover_causal_structure(request: CausalDiscoveryRequest):
    """
    Descubre la estructura causal en los datos proporcionados.
    
    Utiliza algoritmos de descubrimiento causal para identificar
    relaciones causales entre variables.
    """
    try:
        import time
        start_time = time.time()
        
        # Convertir datos a DataFrame
        df = pd.DataFrame(request.data)
        
        # Validar datos
        if df.empty:
            raise HTTPException(status_code=400, detail="Los datos no pueden estar vacíos")
        
        if len(df.columns) < 2:
            raise HTTPException(status_code=400, detail="Se requieren al menos 2 variables")
        
        # Ejecutar descubrimiento causal
        result = causal_service.discover_causal_structure(
            data=df,
            algorithm=request.algorithm,
            alpha=request.alpha,
            max_cond_vars=request.max_cond_vars
        )
        
        execution_time = time.time() - start_time
        
        # Verificar si hubo error
        if 'error' in result:
            return CausalDiscoveryResponse(
                success=False,
                algorithm=request.algorithm,
                variables=list(df.columns),
                edges=[],
                statistics={},
                execution_time=execution_time,
                error=result['error']
            )
        
        return CausalDiscoveryResponse(
            success=True,
            algorithm=result['algorithm'],
            variables=result['variables'],
            edges=result['edges'],
            adjacency_matrix=result.get('adjacency_matrix'),
            statistics=result.get('statistics', {}),
            execution_time=execution_time
        )
        
    except BiologyError as e:
        logger.error(f"Error in causal structure discovery: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en descubrimiento causal: {str(e)}")


@router.post("/estimate-effect", response_model=CausalEffectResponse)
async def estimate_causal_effect(request: CausalEffectRequest):
    """
    Estima el efecto causal entre una variable de tratamiento y una de resultado.
    
    Utiliza métodos de inferencia causal para estimar efectos causales
    controlando por confounders especificados.
    """
    try:
        # Convertir datos a DataFrame
        df = pd.DataFrame(request.data)
        
        # Validar variables requeridas
        required_vars = [request.treatment, request.outcome]
        if request.confounders:
            required_vars.extend(request.confounders)
        
        missing_vars = [var for var in required_vars if var not in df.columns]
        if missing_vars:
            raise HTTPException(
                status_code=400, 
                detail=f"Variables faltantes en los datos: {missing_vars}"
            )
        
        # Ejecutar estimación de efecto causal
        result = causal_service.estimate_causal_effect(
            data=df,
            treatment=request.treatment,
            outcome=request.outcome,
            confounders=request.confounders,
            method=request.method
        )
        
        # Verificar si hubo error
        if 'error' in result:
            return CausalEffectResponse(
                success=False,
                treatment=request.treatment,
                outcome=request.outcome,
                method=request.method,
                ate=None,
                statistics={},
                error=result['error']
            )
        
        return CausalEffectResponse(
            success=True,
            treatment=result['treatment'],
            outcome=result['outcome'],
            method=result['method'],
            ate=result.get('ate'),
            confidence_interval=result.get('confidence_interval'),
            p_value=result.get('p_value'),
            statistics=result.get('statistics', {})
        )
        
    except BiologyError as e:
        logger.error(f"Error in causal effect estimation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en estimación de efecto causal: {str(e)}")


@router.post("/validate-assumptions", response_model=AssumptionValidationResponse)
async def validate_causal_assumptions(request: AssumptionValidationRequest):
    """
    Valida los supuestos causales necesarios para inferencia causal válida.
    
    Verifica supuestos como positividad, overlap, no confounding no medido
    y consistencia.
    """
    try:
        # Convertir datos a DataFrame
        df = pd.DataFrame(request.data)
        
        # Validar variables requeridas
        required_vars = [request.treatment, request.outcome]
        missing_vars = [var for var in required_vars if var not in df.columns]
        if missing_vars:
            raise HTTPException(
                status_code=400, 
                detail=f"Variables faltantes en los datos: {missing_vars}"
            )
        
        # Ejecutar validación de supuestos
        result = causal_service.validate_causal_assumptions(
            data=df,
            causal_graph=request.causal_graph,
            treatment=request.treatment,
            outcome=request.outcome
        )
        
        # Verificar si hubo error
        if 'error' in result:
            return AssumptionValidationResponse(
                success=False,
                overall_validity='unknown',
                positivity={},
                overlap={},
                no_unmeasured_confounding={},
                consistency={},
                error=result['error']
            )
        
        return AssumptionValidationResponse(
            success=True,
            overall_validity=result['overall_validity'],
            positivity=result['positivity'],
            overlap=result['overlap'],
            no_unmeasured_confounding=result['no_unmeasured_confounding'],
            consistency=result['consistency']
        )
        
    except BiologyError as e:
        logger.error(f"Error in assumption validation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en validación de supuestos: {str(e)}")


@router.get("/algorithms")
async def get_supported_algorithms():
    """
    Retorna la lista de algoritmos de descubrimiento causal soportados.
    """
    try:
        algorithms = causal_service.get_supported_algorithms()
        
        algorithm_info = {
            'pc': 'PC Algorithm - Constraint-based causal discovery',
            'ges': 'GES Algorithm - Score-based causal discovery',
            'lingam': 'LINGAM - Linear Non-Gaussian Acyclic Model',
            'hc': 'Hill Climbing - Score-based structure learning',
            'correlation': 'Correlation-based - Simple fallback method'
        }
        
        return {
            'supported_algorithms': algorithms,
            'algorithm_descriptions': {
                alg: algorithm_info.get(alg, 'Algorithm description not available')
                for alg in algorithms
            },
            'recommended_algorithm': 'pc' if 'pc' in algorithms else 'correlation'
        }
        
    except BiologyError as e:
        logger.error(f"Error getting algorithms: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo algoritmos: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Verifica el estado de salud del servicio de descubrimiento causal.
    """
    try:
        service_info = causal_service.get_service_info()
        
        return {
            'status': 'healthy',
            'service': service_info['service_name'],
            'version': service_info['version'],
            'libraries_available': service_info['libraries_available'],
            'supported_algorithms': service_info['supported_algorithms'],
            'capabilities': service_info['capabilities']
        }
        
    except BiologyError as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            'status': 'unhealthy',
            'error': str(e)
        }


@router.get("/examples")
async def get_usage_examples():
    """
    Retorna ejemplos de uso del servicio de descubrimiento causal.
    """
    return {
        'causal_discovery_example': {
            'description': 'Ejemplo de descubrimiento de estructura causal',
            'request': {
                'data': {
                    'X': [1.0, 2.0, 3.0, 4.0, 5.0],
                    'Y': [2.0, 4.0, 6.0, 8.0, 10.0],
                    'Z': [1.0, 1.0, 2.0, 2.0, 3.0]
                },
                'algorithm': 'pc',
                'alpha': 0.05
            }
        },
        'causal_effect_example': {
            'description': 'Ejemplo de estimación de efecto causal',
            'request': {
                'data': {
                    'treatment': [0.0, 1.0, 0.0, 1.0, 0.0, 1.0],
                    'outcome': [1.0, 3.0, 2.0, 4.0, 1.5, 3.5],
                    'confounder': [1.0, 2.0, 1.5, 2.5, 1.2, 2.2]
                },
                'treatment': 'treatment',
                'outcome': 'outcome',
                'confounders': ['confounder'],
                'method': 'backdoor'
            }
        },
        'assumption_validation_example': {
            'description': 'Ejemplo de validación de supuestos causales',
            'note': 'Requiere un grafo causal previamente descubierto'
        }
    }