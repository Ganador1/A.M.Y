"""
🧮 CÁLCULO VARIACIONAL - AXIOM META 4.1
======================================

**Módulo de Cálculo Variacional Avanzado para AXIOM v4.1**

Este router proporciona capacidades avanzadas de cálculo variacional para resolver
problemas de optimización en física matemática, mecánica clásica, teoría de campos
y optimización general. Implementa métodos numéricos y analíticos para ecuaciones
de Euler-Lagrange, derivadas variacionales y principios variacionales clásicos.

## 🎯 FUNCIONALIDADES PRINCIPALES

### 📐 Ecuaciones de Euler-Lagrange
- **Derivación automática** de ecuaciones EL desde densidades Lagrangianas
- **Sistemas multivariables** con coordenadas generalizadas
- **Condiciones de contorno** variables (fijas, libres, periódicas)
- **Lagrangianos dependientes del tiempo** para sistemas dinámicos

### 🔬 Derivadas Variacionales
- **Cálculo funcional** δF/δx para funcionales arbitrarios
- **Gradientes funcionales** en espacios de Hilbert
- **Primeras y segundas variaciones** para estabilidad
- **Derivadas direccionales** en espacios funcionales

### 🏁 Problema de la Braquistócrona
- **Curva de descenso más rápido** bajo gravedad uniforme
- **Solución analítica** mediante cálculo variacional
- **Comparación con otros caminos** (recta, parábola, etc.)
- **Tiempo de recorrido mínimo** entre puntos fijos

### 🧼 Superficies Mínimas
- **Problema de la película de jabón** (Plateau)
- **Área superficial mínima** con contorno fijo
- **Ecuaciones de Euler-Lagrange** para coordenadas
- **Métodos numéricos** para geometrías complejas

### ⚡ Principio de Menor Acción
- **Acción de Hamilton** S = ∫ L(q,q̇,t) dt
- **Trayectorias estacionarias** de la acción
- **Ecuaciones de movimiento** desde variaciones
- **Conservación de la energía** y cantidades

### 🔗 Problemas Isoperimétricos
- **Optimización con restricciones** de longitud/arena fija
- **Multiplicadores de Lagrange** para vínculos
- **Curvas de longitud fija** con área máxima
- **Superficies de área fija** con volumen máximo

## 🔧 ARQUITECTURA TÉCNICA

### Framework y Dependencias
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI       │    │ Variational      │    │   SymPy         │
│   Router        │◄──►│   Calculus       │◄──►│   (Symbolic)    │
│                 │    │   Service        │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   NumPy/SciPy   │    │   Matplotlib     │    │   SciPy         │
│   (Numerical)   │    │   (Visualization)│    │   (ODE/BVP)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Algoritmos Implementados
1. **Euler-Lagrange**: Derivación simbólica de ecuaciones
2. **Método de Ritz**: Aproximación con funciones base
3. **Diferencias finitas**: Solución numérica de BVP
4. **Mínimos cuadrados**: Ajuste de parámetros variacionales
5. **Método de Newton**: Optimización no lineal

## 📊 ESTRUCTURAS DE DATOS

### Funcional Variacional
```python
F[y] = ∫ₐᵇ L(x, y(x), y'(x), ..., y^(n)(x)) dx
```

### Ecuación de Euler-Lagrange
```python
d/dx(∂L/∂y') - ∂L/∂y = 0
```

### Principio de Menor Acción
```python
δS = δ∫ L(q,q̇,t) dt = 0
```

## 🚀 USO EN FÍSICA Y MATEMÁTICAS

### Mecánica Clásica
```python
# Lagrangiano para partícula en potencial
L = T - V = (1/2)m*v² - V(x,t)

# Ecuación EL: m*d²x/dt² = -dV/dx
```

### Teoría de Campos
```python
# Lagrangiano escalar φ⁴
L = (1/2)(∂φ/∂t)² - (1/2)(∇φ)² - V(φ)

# Ecuaciones EL para campo escalar
```

### Optimización Geométrica
```python
# Longitud de curva: L[y] = ∫ √(1 + (y')²) dx
# Geodésicas en superficies curvas
```

## 📈 MÉTRICAS Y VALIDACIÓN

### Precisión de Soluciones
- **Error de discretización**: Control de malla
- **Convergencia**: Criterios de parada
- **Estabilidad numérica**: Condicionamiento
- **Conservación**: Propiedades invariantes

### Validación Física
- **Conservación de energía**: dE/dt = 0
- **Cantidad de movimiento**: dp/dt = 0
- **Simetrías**: Teoremas de Noether
- **Escalas**: Análisis dimensional

## 🔄 INTEGRACIÓN CON SISTEMAS

### Servicios Complementarios
- **TransformService**: Transformadas de Laplace para ODEs
- **ODESolver**: Resolución de ecuaciones diferenciales
- **SymbolicEngine**: Manipulación algebraica avanzada
- **VisualizationService**: Gráficos de trayectorias

### APIs Externas
- **WolframAlpha**: Verificación de resultados analíticos
- **MATHEMATICA**: Comparación con soluciones conocidas
- **SageMath**: Computación simbólica alternativa

## 🧪 TESTING Y VALIDACIÓN

### Casos de Prueba Clásicos
- **Péndulo simple**: Solución analítica conocida
- **Oscilador armónico**: Frecuencia natural
- **Caída libre**: Trayectoria parabólica
- **Geodésicas**: En esfera y cilindro

### Benchmarks de Rendimiento
- **Tiempo de convergencia**: Iteraciones vs precisión
- **Escalabilidad**: Tamaño del problema
- **Estabilidad**: Condiciones iniciales
- **Precisión**: Error relativo absoluto

## 📚 REFERENCIAS ACADÉMICAS

### Textos Fundamentales
- **Lanczos**: "The Variational Principles of Mechanics"
- **Goldstein**: "Classical Mechanics" (Capítulo 2)
- **Gelfand**: "Calculus of Variations"
- **Fox**: "An Introduction to the Calculus of Variations"

### Artículos Clásicos
- **Euler (1744)**: Método de variaciones
- **Lagrange (1755)**: Principio de menor acción
- **Hamilton (1834)**: Formalismo Hamiltoniano
- **Noether (1918)**: Teoremas de simetría

---

**AXIOM v4.1 - Sistema de Investigación Científica Autónoma**
"""

from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime
import time
import logging

from app.domains.mathematics.services.calculus_service import CalculusService
from app.domains.mathematics.models import BaseRequest, BaseResponse
from pydantic import Field
import time
from app.exceptions.domain.mathematics import MathematicsError

# Configuración de logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/variational", tags=["variational-calculus"])
service = CalculusService()

# Modelos Pydantic para la API de cálculo variacional

class VariationalRequest(BaseModel):
    """
    📥 SOLICITUD BASE PARA PROBLEMAS VARIACIONALES
    =============================================

    Modelo base para solicitudes que involucran cálculo variacional,
    incluyendo expresiones simbólicas y parámetros de configuración.
    """
    expression: str = Field(
        ...,
        description="Expresión simbólica del Lagrangiano o funcional",
        examples=["(1/2)*m*x_diff**2 - V(x)", "sqrt(1 + y_diff**2)"]
    )
    variable: str = Field(
        default="x",
        description="Variable independiente principal",
        examples=["x", "t", "theta"]
    )
    dependent_variable: Optional[str] = Field(
        default=None,
        description="Variable dependiente (para funcionales)",
        examples=["y", "q", "phi"]
    )
    parameters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Parámetros adicionales del problema",
        examples=[{"m": 1.0, "g": 9.81, "k": 10.0}]
    )

class EulerLagrangeRequest(VariationalRequest):
    """
    🧮 SOLICITUD PARA ECUACIONES DE EULER-LAGRANGE
    =============================================

    Parámetros específicos para la derivación de ecuaciones de Euler-Lagrange
    desde una densidad Lagrangiana.
    """
    time_variable: str = Field(
        default="t",
        description="Variable temporal (para problemas dinámicos)",
        examples=["t", "tau", "s"]
    )
    order: int = Field(
        default=2,
        description="Orden de las derivadas en la ecuación EL",
        ge=1,
        le=4,
        examples=[2, 1, 3]
    )
    boundary_conditions: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Condiciones de contorno para el problema",
        examples=[{"x(0)": 0, "x(L)": 1, "x'(0)": 0, "x'(L)": 0}]
    )

class BrachistochroneRequest(BaseModel):
    """
    🏁 SOLICITUD PARA PROBLEMA DE LA BRAQUISTÓCRONA
    ==============================================

    Parámetros para resolver el problema clásico de la curva de descenso
    más rápido bajo gravedad uniforme.
    """
    start_point: List[float] = Field(
        ...,
        description="Punto inicial [x1, y1]",
        examples=[[0.0, 0.0], [1.0, 2.0]]
    )
    end_point: List[float] = Field(
        ...,
        description="Punto final [x2, y2]",
        examples=[[2.0, 1.0], [3.0, 0.5]]
    )
    gravity: float = Field(
        default=9.81,
        description="Aceleración de la gravedad (m/s²)",
        gt=0,
        examples=[9.81, 9.8, 10.0]
    )
    num_points: int = Field(
        default=100,
        description="Número de puntos para discretización",
        ge=10,
        le=1000,
        examples=[100, 200, 500]
    )

class MinimalSurfaceRequest(BaseModel):
    """
    🧼 SOLICITUD PARA SUPERFICIES MÍNIMAS
    ====================================

    Parámetros para el cálculo de superficies mínimas con contorno fijo,
    resolviendo el problema de Plateau.
    """
    boundary_points: List[List[float]] = Field(
        ...,
        description="Puntos del contorno [[x1,y1,z1], [x2,y2,z2], ...]",
        examples=[[[0,0,0], [1,0,0], [0.5,1,0]], [[0,0,0], [1,0,0], [1,1,0], [0,1,0]]]
    )
    num_points: int = Field(
        default=50,
        description="Resolución de la malla de triangulación",
        ge=10,
        le=200,
        examples=[50, 100, 150]
    )
    method: str = Field(
        default="numerical",
        description="Método de resolución",
        examples=["numerical", "analytical", "parametric"]
    )

class LeastActionRequest(BaseModel):
    """
    ⚡ SOLICITUD PARA PRINCIPIO DE MENOR ACCIÓN
    ==========================================

    Parámetros para aplicar el principio de Hamilton de menor acción
    y encontrar trayectorias estacionarias.
    """
    lagrangian: str = Field(
        ...,
        description="Expresión del Lagrangiano L(q, q̇, t)",
        examples=["(1/2)*m*q_diff**2 - (1/2)*k*q**2", "m*sqrt(1 + q_diff**2)"]
    )
    initial_conditions: Dict[str, float] = Field(
        ...,
        description="Condiciones iniciales {q(t0), q'(t0)}",
        examples=[{"q": 0.0, "q_dot": 1.0}, {"x": 1.0, "v": 0.0}]
    )
    final_conditions: Dict[str, float] = Field(
        ...,
        description="Condiciones finales {q(tf), q'(tf)}",
        examples=[{"q": 2.0, "q_dot": 0.0}, {"x": 0.0, "v": -1.0}]
    )
    time_interval: List[float] = Field(
        ...,
        description="Intervalo temporal [t0, tf]",
        examples=[[0.0, 1.0], [0.0, 2.0]]
    )
    num_points: int = Field(
        default=100,
        description="Puntos para discretización temporal",
        ge=10,
        le=1000,
        examples=[100, 200, 500]
    )

class VariationalResponse(BaseModel):
    """
    📤 RESPUESTA ESTANDARIZADA PARA CÁLCULO VARIACIONAL
    ==================================================

    Respuesta estandarizada para todas las operaciones de cálculo variacional,
    siguiendo el patrón de respuesta consistente de AXIOM v4.1.
    """
    success: bool = Field(
        ...,
        description="Indica si la operación fue exitosa",
        examples=[True, False]
    )
    message: str = Field(
        ...,
        description="Mensaje descriptivo del resultado",
        examples=["Ecuación EL derivada exitosamente", "Error en cálculo variacional"]
    )
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Datos del resultado variacional"
    )
    execution_time_seconds: float = Field(
        ...,
        description="Tiempo de ejecución en segundos",
        examples=[0.145, 2.234, 0.089]
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp de la respuesta"
    )
    method_used: Optional[str] = Field(
        default=None,
        description="Método de resolución utilizado",
        examples=["analytical", "numerical", "symbolic"]
    )
    convergence_info: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Información de convergencia (para métodos numéricos)"
    )
    error_code: Optional[str] = Field(
        default=None,
        description="Código de error en caso de fallo",
        examples=["INVALID_LAGRANGIAN", "CONVERGENCE_FAILED"]
    )

class FunctionalLibraryResponse(BaseModel):
    """
    📚 RESPUESTA DE BIBLIOTECA DE FUNCIONALES
    =======================================

    Lista de funcionales variacionales disponibles para referencia
    y uso en problemas de optimización.
    """
    functionals: List[Dict[str, Any]] = Field(
        ...,
        description="Lista de funcionales disponibles"
    )
    categories: List[str] = Field(
        ...,
        description="Categorías de funcionales",
        examples=[["mechanics", "geometry", "physics", "optimization"]]
    )
    count: int = Field(
        ...,
        description="Número total de funcionales",
        examples=[25, 50, 100]
    )
    execution_time_seconds: float = Field(
        ...,
        description="Tiempo de ejecución en segundos",
        examples=[0.012, 0.034]
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp de la respuesta"
    )

@router.post("/euler-lagrange", response_model=VariationalResponse)
async def compute_euler_lagrange_equation(
    request: EulerLagrangeRequest
):
    """
    🧮 DERIVACIÓN DE ECUACIONES DE EULER-LAGRANGE
    ===========================================

    Deriva la ecuación de Euler-Lagrange para un Lagrangiano dado:

    d/dt(∂L/∂(dq/dt)) - ∂L/∂q = 0

    **Parámetros:**
    - `request`: Parámetros de la solicitud incluyendo Lagrangiano y variables

    **Retorna:**
    - Ecuación EL derivada en forma simbólica y numérica
    - Información de convergencia para métodos numéricos
    - Tiempo de ejecución y metadatos

    **Ejemplos de uso:**
    - Mecánica clásica: Lagrangiano de partícula en potencial
    - Óptica: Principio de Fermat (tiempo mínimo)
    - Geodesics: Caminos más cortos en variedades
    """
    start_time = time.time()

    try:
        logger.info(f"🔬 Derivando ecuación EL para Lagrangiano: {request.expression}")

        # Usar el servicio para derivar la ecuación EL
        result = service.euler_lagrange_equation(
            request.expression,
            request.variable,
            request.time_variable
        )

        if 'error' in result:
            logger.error(f"❌ Error en derivación EL: {result['error']}")
            raise HTTPException(status_code=400, detail=result['error'])

        execution_time = time.time() - start_time
        logger.info(f"✅ Ecuación EL derivada exitosamente en {execution_time:.3f}s")

        return VariationalResponse(
            success=True,
            message="🧮 Ecuación de Euler-Lagrange derivada exitosamente",
            data=result,
            execution_time_seconds=execution_time,
            method_used="symbolic",
            timestamp=datetime.now()
        )

    except HTTPException:
        raise
    except MathematicsError as e:
        execution_time = time.time() - start_time
        error_msg = f"Error inesperado en derivación EL: {str(e)}"
        logger.error(f"💥 {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@router.post("/variational-derivative", response_model=VariationalResponse)
async def compute_variational_derivative(
    request: VariationalRequest
):
    """
    📐 DERIVADA VARIACIONAL DE FUNCIONALES
    ====================================

    Computa la derivada variacional δF/δx de un funcional F,
    fundamental para el cálculo de variaciones.

    **Parámetros:**
    - `request`: Parámetros incluyendo funcional y variables

    **Retorna:**
    - Derivada variacional en forma simbólica
    - Expansión funcional y términos de Euler-Lagrange
    - Información de convergencia y validación

    **Aplicaciones:**
    - Problemas de contorno en ecuaciones diferenciales
    - Optimización de funcionales en espacios de funciones
    - Principios variacionales en física
    """
    start_time = time.time()

    try:
        logger.info(f"📐 Computando derivada variacional para: {request.expression}")

        result = service.variational_derivative(
            request.expression,
            request.variable,
            request.dependent_variable or 'y'
        )

        if 'error' in result:
            logger.error(f"❌ Error en derivada variacional: {result['error']}")
            raise HTTPException(status_code=400, detail=result['error'])

        execution_time = time.time() - start_time
        logger.info(f"✅ Derivada variacional computada en {execution_time:.3f}s")

        return VariationalResponse(
            success=True,
            message="📐 Derivada variacional computada exitosamente",
            data=result,
            execution_time_seconds=execution_time,
            method_used="symbolic",
            timestamp=datetime.now()
        )

    except HTTPException:
        raise
    except MathematicsError as e:
        execution_time = time.time() - start_time
        error_msg = f"Error inesperado en derivada variacional: {str(e)}"
        logger.error(f"💥 {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@router.post("/brachistochrone", response_model=VariationalResponse)
async def solve_brachistochrone_problem(
    request: BrachistochroneRequest
):
    """
    🏁 PROBLEMA DE LA BRAQUISTÓCRONA
    ================================

    Resuelve el problema clásico de la curva de descenso más rápido
    bajo gravedad uniforme entre dos puntos dados.

    **Parámetros:**
    - `request`: Puntos inicial/final y parámetros físicos

    **Retorna:**
    - Curva brachistochrone óptima (cicloide)
    - Tiempo de recorrido mínimo
    - Perfil de velocidad a lo largo de la trayectoria
    - Visualización de la solución

    **Fundamento matemático:**
    - Principio de menor tiempo (variacional)
    - Ecuación paramétrica de la cicloide
    - Solución analítica exacta disponible
    """
    start_time = time.time()

    try:
        # Validar que los puntos tengan exactamente 2 coordenadas
        if len(request.start_point) != 2 or len(request.end_point) != 2:
            raise HTTPException(
                status_code=400,
                detail="Los puntos deben tener exactamente 2 coordenadas [x, y]"
            )

        logger.info(f"🏁 Resolviendo brachistochrone: {request.start_point} → {request.end_point}")

        result = service.solve_brachistochrone(
            request.start_point[0], request.start_point[1],
            request.end_point[0], request.end_point[1],
            request.gravity
        )

        if 'error' in result:
            logger.error(f"❌ Error en brachistochrone: {result['error']}")
            raise HTTPException(status_code=400, detail=result['error'])

        execution_time = time.time() - start_time
        logger.info(f"✅ Brachistochrone resuelto en {execution_time:.3f}s")

        return VariationalResponse(
            success=True,
            message="🏁 Problema de la brachistochrone resuelto exitosamente",
            data=result,
            execution_time_seconds=execution_time,
            method_used="analytical",
            timestamp=datetime.now()
        )

    except HTTPException:
        raise
    except MathematicsError as e:
        execution_time = time.time() - start_time
        error_msg = f"Error inesperado en brachistochrone: {str(e)}"
        logger.error(f"💥 {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@router.post("/minimal-surface", response_model=VariationalResponse)
async def compute_minimal_surface(
    request: MinimalSurfaceRequest
):
    """
    🧼 SUPERFICIES MÍNIMAS (PROBLEMA DE PLATEAU)
    ===========================================

    Computa la superficie de área mínima con contorno fijo,
    resolviendo el problema de Plateau mediante métodos variacionales.

    **Parámetros:**
    - `request`: Puntos del contorno y parámetros de resolución

    **Retorna:**
    - Superficie mínima paramétrica
    - Área total de la superficie
    - Información de convergencia del algoritmo
    - Visualización 3D de la superficie

    **Métodos disponibles:**
    - Numérico: Algoritmos de optimización variacional
    - Analítico: Soluciones exactas para geometrías simples
    - Paramétrico: Representación paramétrica de la superficie
    """
    start_time = time.time()

    try:
        # Validar que haya al menos 3 puntos para formar un contorno
        if len(request.boundary_points) < 3:
            raise HTTPException(
                status_code=400,
                detail="Se requieren al menos 3 puntos para definir un contorno válido"
            )

        logger.info(f"🧼 Computando superficie mínima con {len(request.boundary_points)} puntos de contorno")

        result = service.minimal_surface_area(
            request.boundary_points,
            request.num_points
        )

        if 'error' in result:
            logger.error(f"❌ Error en superficie mínima: {result['error']}")
            raise HTTPException(status_code=400, detail=result['error'])

        execution_time = time.time() - start_time
        logger.info(f"✅ Superficie mínima computada en {execution_time:.3f}s")

        return VariationalResponse(
            success=True,
            message="🧼 Superficie mínima computada exitosamente",
            data=result,
            execution_time_seconds=execution_time,
            method_used=request.method,
            timestamp=datetime.now()
        )

    except HTTPException:
        raise
    except MathematicsError as e:
        execution_time = time.time() - start_time
        error_msg = f"Error inesperado en superficie mínima: {str(e)}"
        logger.error(f"💥 {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@router.post("/least-action", response_model=VariationalResponse)
async def apply_least_action_principle(
    request: LeastActionRequest
):
    """
    ⚡ PRINCIPIO DE MENOR ACCIÓN
    ===========================

    Aplica el principio de Hamilton de menor acción para encontrar
    la trayectoria estacionaria que conecta condiciones iniciales
    y finales en el tiempo especificado.

    **Parámetros:**
    - `request`: Lagrangiano, condiciones iniciales/finales y intervalo temporal

    **Retorna:**
    - Trayectoria de acción estacionaria
    - Valor de la acción a lo largo del camino
    - Información de convergencia del algoritmo
    - Comparación con otras trayectorias posibles

    **Aplicaciones físicas:**
    - Mecánica clásica: Ecuaciones de movimiento
    - Óptica geométrica: Principio de Fermat
    - Relatividad: Geodésicas en espacios curvos
    """
    start_time = time.time()

    try:
        # Validar intervalo temporal
        if len(request.time_interval) != 2:
            raise HTTPException(
                status_code=400,
                detail="El intervalo temporal debe tener exactamente 2 valores [t0, tf]"
            )

        if request.time_interval[0] >= request.time_interval[1]:
            raise HTTPException(
                status_code=400,
                detail="El tiempo inicial debe ser menor que el tiempo final"
            )

        logger.info(f"⚡ Aplicando principio de menor acción: {request.time_interval[0]} → {request.time_interval[1]}")

        result = service.principle_of_least_action(
            request.lagrangian,
            request.initial_conditions,
            request.final_conditions,
            request.time_interval
        )

        if 'error' in result:
            logger.error(f"❌ Error en principio de menor acción: {result['error']}")
            raise HTTPException(status_code=400, detail=result['error'])

        execution_time = time.time() - start_time
        logger.info(f"✅ Principio de menor acción aplicado en {execution_time:.3f}s")

        return VariationalResponse(
            success=True,
            message="⚡ Principio de menor acción aplicado exitosamente",
            data=result,
            execution_time_seconds=execution_time,
            method_used="numerical",
            timestamp=datetime.now()
        )

    except HTTPException:
        raise
    except MathematicsError as e:
        execution_time = time.time() - start_time
        error_msg = f"Error inesperado en principio de menor acción: {str(e)}"
        logger.error(f"💥 {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/functionals", response_model=FunctionalLibraryResponse)
async def get_available_functionals():
    """
    📚 BIBLIOTECA DE FUNCIONALES VARIACIONALES
    ========================================

    Retorna la biblioteca completa de funcionales variacionales
    disponibles para problemas de optimización y física.

    **Retorna:**
    - Lista completa de funcionales por categoría
    - Descripciones detalladas y expresiones matemáticas
    - Ejemplos de aplicación y referencias bibliográficas
    - Información de implementación y complejidad

    **Categorías disponibles:**
    - Mecánica: Lagrangianos de sistemas físicos
    - Geometría: Funcionales de curvatura y área
    - Física: Principios variacionales fundamentales
    - Optimización: Funcionales de costo y objetivo
    """
    start_time = time.time()

    try:
        logger.info("📚 Consultando biblioteca de funcionales variacionales")

        result = service.get_functionals_list()

        execution_time = time.time() - start_time
        logger.info(f"✅ Biblioteca de funcionales consultada en {execution_time:.3f}s")

        # Estructurar la respuesta según el modelo FunctionalLibraryResponse
        functionals_data = result.get('functionals', [])
        categories = result.get('categories', [])

        return FunctionalLibraryResponse(
            functionals=functionals_data,
            categories=categories,
            count=len(functionals_data),
            execution_time_seconds=execution_time,
            timestamp=datetime.now()
        )

    except MathematicsError as e:
        execution_time = time.time() - start_time
        error_msg = f"Error al consultar biblioteca de funcionales: {str(e)}"
        logger.error(f"💥 {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
