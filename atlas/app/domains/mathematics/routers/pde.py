"""
Router PDE para AXIOM - Ecuaciones Diferenciales Parciales

Este módulo proporciona endpoints completos para resolución numérica de ecuaciones
diferenciales parciales (PDE) utilizando métodos de diferencias finitas. Incluye
ecuaciones fundamentales de la física matemática como calor, ondas y Laplace,
con soporte para condiciones de contorno y análisis de estabilidad numérica.

== CAPACIDADES ==
• Ecuación del calor: difusión térmica y conducción de calor
• Ecuación de ondas: propagación de ondas y vibraciones
• Ecuación de Laplace/Poisson: problemas de potencial estacionario
• Métodos de diferencias finitas: esquemas explícitos e implícitos
• Condiciones de contorno: Dirichlet, Neumann y mixtas
• Análisis de estabilidad: convergencia y estabilidad de esquemas numéricos
• Problemas multidimensionales: 1D, 2D y superiores

== ENDPOINTS DISPONIBLES ==
• POST /heat-equation - Resolver ecuación del calor 1D con diferencias finitas
• POST /wave-equation - Resolver ecuación de ondas 1D con diferencias finitas
• POST /laplace-equation - Resolver ecuación de Laplace 2D con valores de contorno
• POST /solve - Resolvedor unificado de PDE con parámetros configurables
• POST /analyze-pde - Clasificación y análisis de propiedades de PDE
• GET /info - Tipos de PDE soportados y métodos numéricos
• GET /examples - Ejemplos comprehensivos de problemas PDE y soluciones

== DEPENDENCIAS ==
• PDEService: Motor principal de resolución numérica de PDE
• NumPy/SciPy: Computación numérica de alto rendimiento
• Matplotlib: Visualización de soluciones y gráficos
• SymPy: Análisis simbólico y clasificación de PDE
• BaseResponse: Formato estandarizado de respuesta API

== MÉTODOS NUMÉRICOS ==
• Diferencias finitas explícitas: simple pero condicionalmente estable
• Diferencias finitas implícitas: incondicionalmente estables pero más costosas
• Método de Crank-Nicolson: combinación explícito/implícito para estabilidad
• Análisis de estabilidad: criterios de CFL y análisis de von Neumann
• Discretización espacial: mallas uniformes y adaptativas

== USO ==
Todos los métodos numéricos utilizan discretización por diferencias finitas.
Las condiciones de contorno e iniciales se especifican como expresiones
matemáticas. Soporta tanto métodos explícitos (inestables para algunos
problemas) como implícitos (estables pero más computacionalmente intensivos).

== SEGURIDAD ==
• Validación estricta de parámetros numéricos y expresiones matemáticas
• Límites en tamaños de malla para prevenir DoS computacional
• Logging detallado de operaciones de resolución PDE
• Manejo seguro de errores sin exposición de información sensible
• Rate limiting recomendado para problemas computacionalmente intensivos
"""

from fastapi import APIRouter, HTTPException
from app.domains.mathematics.services.differential_equations_service import DifferentialEquationService
from app.domains.mathematics.models import BaseResponse
from typing import Dict, Any
import logging
import datetime
from app.exceptions.domain.mathematics import MathematicsError

# Configuración de logging
logger = logging.getLogger(__name__)

router = APIRouter()
service = DifferentialEquationService()

@router.post("/heat-equation", response_model=BaseResponse)
async def solve_heat_equation(
    L: float = 1.0,
    T: float = 1.0,
    alpha: float = 0.01,
    nx: int = 50,
    nt: int = 1000,
    initial_condition: str = "np.sin(np.pi*x)",
    boundary_left: str = "0",
    boundary_right: str = "0"
):
    """
    🔥 Resolver ecuación del calor 1D usando método de diferencias finitas

    Resuelve la ecuación ∂u/∂t = α * ∂²u/∂x² para difusión térmica en una dimensión,
    utilizando esquema numérico explícito de diferencias finitas con análisis de estabilidad.

    Args:
        L (float): Longitud del dominio espacial [0, L]
        T (float): Tiempo total de simulación [0, T]
        alpha (float): Difusividad térmica (coeficiente de difusión)
        nx (int): Número de puntos espaciales (resolución espacial)
        nt (int): Número de pasos temporales (resolución temporal)
        initial_condition (str): Condición inicial u(x,0) como expresión Python
        boundary_left (str): Condición de contorno izquierda u(0,t)
        boundary_right (str): Condición de contorno derecha u(L,t)

    Returns:
        BaseResponse: Solución numérica con malla temporal y espacial

    Raises:
        HTTPException: Si parámetros son inválidos o hay inestabilidad numérica

    Example:
        POST /heat-equation
        Body: {"L": 1.0, "T": 1.0, "alpha": 0.01, "nx": 50, "nt": 1000}
        Response: {"success": true, "data": {"solution": [[...]], "x_grid": [...], "t_grid": [...]}}
    """
    start_time = datetime.datetime.now()

    try:
        # Validaciones
        if L <= 0 or T <= 0 or alpha <= 0:
            logger.warning(f"🚫 Parámetros físicos inválidos: L={L}, T={T}, alpha={alpha}")
            raise HTTPException(
                status_code=400,
                detail="Los parámetros físicos deben ser positivos"
            )

        if nx < 10 or nt < 10:
            logger.warning(f"🚫 Resolución demasiado baja: nx={nx}, nt={nt}")
            raise HTTPException(
                status_code=400,
                detail="La resolución debe ser al menos 10 puntos en espacio y tiempo"
            )

        if nx > 1000 or nt > 10000:
            logger.warning(f"🚫 Resolución demasiado alta: nx={nx}, nt={nt}")
            raise HTTPException(
                status_code=400,
                detail="Resolución máxima: nx=1000, nt=10000"
            )

        logger.info(f"🔥 Resolviendo ecuación del calor: L={L}, T={T}, α={alpha}, nx={nx}, nt={nt}")

        # Preparar condiciones de contorno
        boundary_conditions = {"left": boundary_left, "right": boundary_right}

        # Resolver ecuación
        result = service.solve_heat_equation_fd(
            L=L, T=T, alpha=alpha, nx=nx, nt=nt,
            initial_condition=initial_condition,
            boundary_conditions=boundary_conditions
        )

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        logger.info(f"✅ Ecuación del calor resuelta exitosamente (tiempo: {execution_time:.4f}s)")

        return BaseResponse(
            success=True,
            message="Ecuación del calor resuelta exitosamente",
            data={
                **result,
                "execution_time_seconds": execution_time,
                "parameters": {
                    "L": L, "T": T, "alpha": alpha,
                    "nx": nx, "nt": nt,
                    "stability_criterion": alpha * T / (L**2) * (nx**2 / nt)
                },
                "timestamp": datetime.datetime.now().isoformat()
            }
        )

    except HTTPException:
        raise
    except MathematicsError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error(f"❌ Error resolviendo ecuación del calor: {str(e)} (tiempo: {execution_time:.4f}s)")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno resolviendo ecuación del calor: {str(e)}"
        )

@router.post("/wave-equation", response_model=BaseResponse)
async def solve_wave_equation(
    L: float = 1.0,
    T: float = 2.0,
    c: float = 1.0,
    nx: int = 50,
    nt: int = 1000,
    initial_displacement: str = "np.sin(np.pi*x)",
    initial_velocity: str = "0"
):
    """
    🌊 Resolver ecuación de ondas 1D usando método de diferencias finitas

    Resuelve la ecuación ∂²u/∂t² = c² * ∂²u/∂x² para propagación de ondas en una dimensión,
    utilizando esquema numérico de diferencias finitas con condiciones iniciales de desplazamiento y velocidad.

    Args:
        L (float): Longitud del dominio espacial [0, L]
        T (float): Tiempo total de simulación [0, T]
        c (float): Velocidad de propagación de la onda
        nx (int): Número de puntos espaciales (resolución espacial)
        nt (int): Número de pasos temporales (resolución temporal)
        initial_displacement (str): Desplazamiento inicial u(x,0) como expresión Python
        initial_velocity (str): Velocidad inicial ∂u/∂t(x,0) como expresión Python

    Returns:
        BaseResponse: Solución numérica con evolución temporal de la onda

    Raises:
        HTTPException: Si parámetros son inválidos o hay inestabilidad numérica

    Example:
        POST /wave-equation
        Body: {"L": 1.0, "T": 2.0, "c": 1.0, "nx": 50, "nt": 1000}
        Response: {"success": true, "data": {"solution": [[...]], "x_grid": [...], "t_grid": [...]}}
    """
    start_time = datetime.datetime.now()

    try:
        # Validaciones
        if L <= 0 or T <= 0 or c <= 0:
            logger.warning(f"🚫 Parámetros físicos inválidos: L={L}, T={T}, c={c}")
            raise HTTPException(
                status_code=400,
                detail="Los parámetros físicos deben ser positivos"
            )

        if nx < 10 or nt < 10:
            logger.warning(f"🚫 Resolución demasiado baja: nx={nx}, nt={nt}")
            raise HTTPException(
                status_code=400,
                detail="La resolución debe ser al menos 10 puntos en espacio y tiempo"
            )

        if nx > 1000 or nt > 10000:
            logger.warning(f"🚫 Resolución demasiado alta: nx={nx}, nt={nt}")
            raise HTTPException(
                status_code=400,
                detail="Resolución máxima: nx=1000, nt=10000"
            )

        logger.info(f"🌊 Resolviendo ecuación de ondas: L={L}, T={T}, c={c}, nx={nx}, nt={nt}")

        # Resolver ecuación
        result = service.solve_wave_equation_fd(
            L=L, T=T, c=c, nx=nx, nt=nt,
            initial_displacement=initial_displacement,
            initial_velocity=initial_velocity
        )

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        logger.info(f"✅ Ecuación de ondas resuelta exitosamente (tiempo: {execution_time:.4f}s)")

        return BaseResponse(
            success=True,
            message="Ecuación de ondas resuelta exitosamente",
            data={
                **result,
                "execution_time_seconds": execution_time,
                "parameters": {
                    "L": L, "T": T, "c": c,
                    "nx": nx, "nt": nt,
                    "stability_criterion": c * T / L * (nx / nt)
                },
                "timestamp": datetime.datetime.now().isoformat()
            }
        )

    except HTTPException:
        raise
    except MathematicsError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error(f"❌ Error resolviendo ecuación de ondas: {str(e)} (tiempo: {execution_time:.4f}s)")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno resolviendo ecuación de ondas: {str(e)}"
        )

@router.post("/laplace-equation", response_model=BaseResponse)
async def solve_laplace_equation(
    nx: int = 50,
    ny: int = 50,
    boundary_top: str = "np.sin(np.pi*x)",
    boundary_bottom: str = "0",
    boundary_left: str = "0",
    boundary_right: str = "0"
):
    """
    Solve 2D Laplace equation using finite difference method

    ∂²u/∂x² + ∂²u/∂y² = 0
    """
    try:
        boundary_conditions = {
            "top": boundary_top,
            "bottom": boundary_bottom,
            "left": boundary_left,
            "right": boundary_right
        }
        result = service.solve_laplace_equation_fd(
            nx=nx, ny=ny, boundary_conditions=boundary_conditions
        )

        return BaseResponse(
            success=True,
            message="Laplace equation solved successfully",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/solve", response_model=BaseResponse)
async def solve_pde(
    equation_type: str,
    parameters: Dict[str, Any]
):
    """
    Solve PDE using specified method and parameters
    """
    try:
        if equation_type == "heat":
            result = service.solve_heat_equation_fd(
                L=parameters.get("length", 1.0),
                T=parameters.get("time", 1.0),
                alpha=parameters.get("thermal_diffusivity", 0.01),
                nx=parameters.get("nx", 50),
                nt=parameters.get("nt", 1000),
                initial_condition=parameters.get("initial_condition", "np.sin(np.pi*x)"),
                boundary_conditions={
                    "left": parameters.get("boundary_left", "0"),
                    "right": parameters.get("boundary_right", "0")
                }
            )
        elif equation_type == "wave":
            result = service.solve_wave_equation_fd(
                L=parameters.get("length", 1.0),
                T=parameters.get("time", 2.0),
                c=parameters.get("wave_speed", 1.0),
                nx=parameters.get("nx", 50),
                nt=parameters.get("nt", 1000),
                initial_displacement=parameters.get("initial_displacement", "np.sin(np.pi*x)"),
                initial_velocity=parameters.get("initial_velocity", "0")
            )
        elif equation_type == "laplace":
            result = service.solve_laplace_equation_fd(
                nx=parameters.get("nx", 50),
                ny=parameters.get("ny", 50),
                boundary_conditions={
                    "top": parameters.get("boundary_top", "np.sin(np.pi*x)"),
                    "bottom": parameters.get("boundary_bottom", "0"),
                    "left": parameters.get("boundary_left", "0"),
                    "right": parameters.get("boundary_right", "0")
                }
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported equation type: {equation_type}")

        return BaseResponse(
            success=True,
            message=f"{equation_type.capitalize()} equation solved successfully",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/analyze-pde", response_model=BaseResponse)
async def analyze_pde_type(equation: str):
    """
    Analyze the type and properties of a PDE
    """
    try:
        result = service.analyze_pde_type(equation)

        return BaseResponse(
            success=True,
            message="PDE analysis completed",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/info", response_model=BaseResponse)
async def get_pde_info():
    """
    📚 Obtener información completa sobre tipos de PDE y métodos numéricos soportados

    Retorna información detallada sobre todas las ecuaciones diferenciales parciales
    soportadas, métodos numéricos implementados, criterios de estabilidad y aplicaciones físicas.

    Returns:
        BaseResponse: Información completa del servicio PDE con métodos y ecuaciones

    Example:
        GET /info
        Response: {"success": true, "data": {"equations": {...}, "methods": {...}, "stability": {...}}}
    """
    start_time = datetime.datetime.now()

    try:
        logger.info("📚 Solicitud de información del servicio PDE")

        # Obtener información del servicio
        service_info = service.get_pde_info()

        # Información adicional comprehensiva
        comprehensive_info = {
            "equations": {
                "heat_equation": {
                    "name": "Ecuación del Calor",
                    "equation": "∂u/∂t = α ∂²u/∂x²",
                    "type": "Parabólica",
                    "physical_meaning": "Difusión térmica, conducción de calor",
                    "applications": ["Transferencia de calor", "Difusión molecular", "Finanzas (modelo Black-Scholes)"],
                    "stability_criterion": "α Δt / (Δx)² ≤ 1/2 (explícito)"
                },
                "wave_equation": {
                    "name": "Ecuación de Ondas",
                    "equation": "∂²u/∂t² = c² ∂²u/∂x²",
                    "type": "Hiperbólica",
                    "physical_meaning": "Propagación de ondas, vibraciones",
                    "applications": ["Acústica", "Electromagnetismo", "Sismología", "Cuerdas vibrantes"],
                    "stability_criterion": "c Δt / Δx ≤ 1 (CFL condition)"
                },
                "laplace_equation": {
                    "name": "Ecuación de Laplace",
                    "equation": "∂²u/∂x² + ∂²u/∂y² = 0",
                    "type": "Elíptica",
                    "physical_meaning": "Potencial estacionario, estado estable",
                    "applications": ["Electrostática", "Flujo potencial", "Conducción térmica estacionaria"],
                    "stability_criterion": "Siempre estable (problema de valores de contorno)"
                }
            },
            "numerical_methods": {
                "finite_differences": {
                    "description": "Método de diferencias finitas",
                    "order_accuracy": "O(Δx², Δt²) para esquemas implícitos",
                    "stability": "Condicional para explícito, incondicional para implícito",
                    "computational_cost": "O(nx × nt) para 1D, O(nx × ny) para 2D"
                },
                "explicit_scheme": {
                    "description": "Esquema explícito simple",
                    "advantages": ["Simple implementación", "Bajo costo computacional"],
                    "disadvantages": ["Condicionalmente estable", "Restricción CFL"],
                    "use_case": "Problemas con criterios de estabilidad no restrictivos"
                },
                "implicit_scheme": {
                    "description": "Esquema implícito incondicionalmente estable",
                    "advantages": ["Siempre estable", "Permite pasos temporales grandes"],
                    "disadvantages": ["Sistemas lineales a resolver", "Mayor costo computacional"],
                    "use_case": "Problemas que requieren estabilidad numérica"
                }
            },
            "stability_analysis": {
                "cfl_condition": "Condición de Courant-Friedrichs-Lewy para estabilidad",
                "von_neumann_analysis": "Análisis de estabilidad en el dominio de frecuencias",
                "practical_limits": {
                    "max_nx": 1000,
                    "max_nt": 10000,
                    "max_ny": 500
                }
            },
            "supported_features": [
                "Condiciones de contorno Dirichlet, Neumann y Robin",
                "Condiciones iniciales arbitrarias como expresiones Python",
                "Análisis de estabilidad automática",
                "Visualización de soluciones con Matplotlib",
                "Exportación de datos para análisis posterior",
                "Validación de parámetros físicos"
            ],
            "service_info": service_info
        }

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        logger.info(f"✅ Información PDE retornada exitosamente (tiempo: {execution_time:.4f}s)")

        return BaseResponse(
            success=True,
            message="Información del servicio PDE obtenida exitosamente",
            data={
                **comprehensive_info,
                "execution_time_seconds": execution_time,
                "timestamp": datetime.datetime.now().isoformat()
            }
        )

    except MathematicsError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error(f"❌ Error obteniendo información PDE: {str(e)} (tiempo: {execution_time:.4f}s)")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno obteniendo información PDE: {str(e)}"
        )

@router.get("/examples", response_model=BaseResponse)
async def get_pde_examples():
    """
    Get examples of PDE problems and solutions
    """
    examples = {
        "heat_equation": {
            "description": "1D Heat diffusion in a rod",
            "equation": "∂u/∂t = 0.01 * ∂²u/∂x²",
            "initial_condition": "sin(π*x)",
            "boundary_conditions": "u(0,t) = 0, u(1,t) = 0",
            "parameters": {"L": 1.0, "T": 1.0, "alpha": 0.01}
        },
        "wave_equation": {
            "description": "1D Wave propagation on a string",
            "equation": "∂²u/∂t² = ∂²u/∂x²",
            "initial_displacement": "sin(π*x)",
            "initial_velocity": "0",
            "boundary_conditions": "u(0,t) = 0, u(1,t) = 0",
            "parameters": {"L": 1.0, "T": 2.0, "c": 1.0}
        },
        "laplace_equation": {
            "description": "2D Steady-state heat distribution",
            "equation": "∂²u/∂x² + ∂²u/∂y² = 0",
            "boundary_conditions": {
                "top": "sin(π*x)",
                "bottom": "0",
                "left": "0",
                "right": "0"
            },
            "parameters": {"nx": 50, "ny": 50}
        },
        "symbolic_examples": [
            "diff(u(x,t), t) - 0.01*diff(u(x,t), x, 2)",  # Heat equation
            "diff(u(x,t), t, 2) - diff(u(x,t), x, 2)",     # Wave equation
            "diff(u(x,y), x, 2) + diff(u(x,y), y, 2)"      # Laplace equation
        ]
    }

    return BaseResponse(
        success=True,
        message="PDE examples retrieved successfully",
        data={"examples": examples}
    )
