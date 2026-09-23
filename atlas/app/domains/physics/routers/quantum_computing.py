"""
🧮 Router de Computación Cuántica - AXIOM v4.1

Este módulo proporciona endpoints comprehensivos para computación cuántica, incluyendo
algoritmos fundamentales como estados de Bell, búsqueda de Grover, transformada
de Fourier cuántica y optimización variacional. Soporta múltiples frameworks
como Qiskit y Cirq para simulación y comparación con computación clásica.

Características principales:
- Creación y análisis de estados de Bell con entrelazamiento máximo
- Implementación del algoritmo de búsqueda de Grover con ventaja cuadrática
- Transformada de Fourier Cuántica para análisis de frecuencia
- Solucionador Variacional Cuántico (VQE) para optimización molecular
- Comparación de rendimiento cuántico vs clásico en diferentes problemas
- Estados de Bell rápidos con resultados simplificados
- Análisis de entrelazamiento y correlaciones cuánticas
- Simulación de algoritmos en frameworks Qiskit y Cirq

Endpoints disponibles:
- GET /: Página principal con información general
- GET /info: Información detallada de capacidades
- GET /examples: Ejemplos prácticos de algoritmos
- POST /bell-state: Creación de estados de Bell
- POST /grover-search: Algoritmo de búsqueda de Grover
- POST /quantum-fourier-transform: Transformada de Fourier Cuántica
- POST /vqe: Solucionador Variacional Cuántico
- POST /quantum-classical-comparison: Comparación cuántico-clásico
- GET /quick-bell/{framework}: Estado de Bell rápido

Consideraciones de seguridad:
- Validación estricta de parámetros para prevenir errores de simulación
- Manejo seguro de errores sin exposición de información sensible
- Limitación de recursos para evitar consumo excesivo de CPU/memoria
- Validación de frameworks soportados (Qiskit, Cirq)

Dependencias:
- QuantumComputingService: Servicio principal de computación cuántica
- BaseResponse: Modelo de respuesta estándar
- Qiskit: Framework de computación cuántica de IBM
- Cirq: Framework de computación cuántica de Google

Consideraciones éticas y técnicas:
- Ejemplos educativos; no usar para producción sin revisión experta
- Respetar licencias y cuotas de proveedores de servicios cuánticos
- Limitar tamaño de problemas para evitar consumo excesivo
- Resultados de simulación idealizados; considerar ruido en hardware real

Ejemplo de uso:
    POST /api/quantum-computing/bell-state
    {
        "framework": "qiskit"
    }

Autor: AXIOM Development Team
Versión: 4.1
Última actualización: 2024
"""

from fastapi import APIRouter, HTTPException
from ..quantum.quantum_computing_service import QuantumComputingService
from app.domains.models import BaseResponse
from app.models.advanced_models import QuantumComputingRequest
import logging
import datetime
from app.exceptions.domain.physics import QuantumError

# Configuración de logging
logger = logging.getLogger(__name__)

router = APIRouter()
service = QuantumComputingService()

@router.get("/", response_model=BaseResponse)
async def get_quantum_computing_home():
    """
    🏠 Página principal de computación cuántica con información general

    Proporciona una visión general completa de las capacidades de computación cuántica
    disponibles en AXIOM, incluyendo algoritmos soportados, frameworks y ejemplos de uso.

    Returns:
        BaseResponse: Información general del servicio de computación cuántica

    Raises:
        HTTPException: Si hay error interno obteniendo la información

    Example:
        GET /
        Response: {"success": true, "message": "Bienvenido a la computación cuántica", "data": {...}}
    """
    start_time = datetime.datetime.now()

    try:
        logger.info("🏠 Consultando página principal de computación cuántica")

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        response_data = {
            "description": "Algoritmos cuánticos, estados entrelazados, optimización variacional y comparación con computación clásica",
            "available_algorithms": [
                "Estados de Bell (entrelazamiento máximo)",
                "Búsqueda de Grover (búsqueda cuadrática)",
                "Transformada de Fourier Cuántica (QFT)",
                "Solucionador Variacional Cuántico (VQE)",
                "Comparación cuántico vs clásico"
            ],
            "frameworks_supported": ["Qiskit", "Cirq"],
            "examples": {
                "bell_state": "POST /api/quantum-computing/bell-state con framework qiskit o cirq",
                "grover_search": "POST /api/quantum-computing/grover-search con estado objetivo",
                "quantum_fourier": "POST /api/quantum-computing/quantum-fourier-transform con número de qubits",
                "vqe": "POST /api/quantum-computing/vqe para optimización molecular",
                "comparison": "POST /api/quantum-computing/quantum-classical-comparison con tamaño del problema"
            },
            "metadata": {
                "execution_time_seconds": execution_time,
                "timestamp": datetime.datetime.now().isoformat(),
                "service_version": "4.1"
            }
        }

        logger.info("✅ Página principal cargada exitosamente (tiempo: %.4fs)", execution_time)

        return BaseResponse(
            success=True,
            message="Bienvenido a la computación cuántica de Mathematics AI",
            data=response_data
        )

    except QuantumError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error cargando página principal: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno cargando página principal: {str(e)}"
        ) from e

@router.get("/info", response_model=BaseResponse)
async def get_quantum_computing_info():
    """
    📋 Información detallada sobre las capacidades de computación cuántica

    Proporciona información técnica detallada sobre algoritmos, frameworks,
    limitaciones y capacidades del servicio de computación cuántica.

    Returns:
        BaseResponse: Información técnica detallada del servicio

    Raises:
        HTTPException: Si hay error obteniendo la información del servicio

    Example:
        GET /info
        Response: {"success": true, "message": "Información de algoritmos", "data": {...}}
    """
    start_time = datetime.datetime.now()

    try:
        logger.info("📋 Consultando información detallada del servicio de computación cuántica")

        result = service.get_service_info()

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        # Enriquecer respuesta con metadatos
        enriched_result = {
            **result,
            "metadata": {
                "execution_time_seconds": execution_time,
                "timestamp": datetime.datetime.now().isoformat(),
                "query_type": "service_info"
            }
        }

        logger.info("✅ Información del servicio obtenida exitosamente (tiempo: %.4fs)", execution_time)

        return BaseResponse(
            success=True,
            message="Información de algoritmos de computación cuántica",
            data=enriched_result
        )

    except QuantumError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error obteniendo información del servicio: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno obteniendo información del servicio: {str(e)}"
        ) from e

@router.get("/examples", response_model=BaseResponse)
async def get_quantum_computing_examples():
    """
    📚 Ejemplos prácticos de algoritmos de computación cuántica

    Proporciona una colección comprehensiva de ejemplos prácticos para todos los
    algoritmos cuánticos disponibles, incluyendo parámetros, descripciones y
    resultados esperados.

    Returns:
        BaseResponse: Colección completa de ejemplos de algoritmos cuánticos

    Raises:
        HTTPException: Si hay error interno generando los ejemplos

    Example:
        GET /examples
        Response: {"success": true, "message": "Ejemplos de algoritmos", "data": {...}}
    """
    start_time = datetime.datetime.now()

    try:
        logger.info("📚 Consultando ejemplos de algoritmos de computación cuántica")

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        examples_data = {
            "bell_state_examples": [
                {
                    "name": "Estado de Bell con Qiskit",
                    "parameters": {"framework": "qiskit"},
                    "description": "Creación del estado |Φ⁺⟩ = (|00⟩ + |11⟩)/√2",
                    "endpoint": "POST /api/quantum-computing/bell-state",
                    "expected_results": ["probabilidades iguales para 00 y 11", "entrelazamiento máximo"]
                },
                {
                    "name": "Estado de Bell con Cirq",
                    "parameters": {"framework": "cirq"},
                    "description": "Implementación alternativa usando Cirq",
                    "endpoint": "POST /api/quantum-computing/bell-state",
                    "expected_results": ["mismo resultado que Qiskit", "compatibilidad entre frameworks"]
                }
            ],
            "grover_search_examples": [
                {
                    "name": "Buscar estado |11⟩",
                    "parameters": {"n_qubits": 2, "target_state": "11"},
                    "description": "Búsqueda del estado |11⟩ en 2 qubits",
                    "endpoint": "POST /api/quantum-computing/grover-search",
                    "expected_results": ["amplitud amplificada para |11⟩", "probabilidad ~81%"]
                },
                {
                    "name": "Buscar estado |01⟩",
                    "parameters": {"n_qubits": 2, "target_state": "01"},
                    "description": "Búsqueda del estado |01⟩ en 2 qubits",
                    "endpoint": "POST /api/quantum-computing/grover-search",
                    "expected_results": ["amplitud amplificada para |01⟩", "reducción de otras amplitudes"]
                }
            ],
            "qft_examples": [
                {
                    "name": "QFT de 3 qubits",
                    "parameters": {"n_qubits": 3},
                    "description": "Transformada de Fourier en 3 qubits",
                    "endpoint": "POST /api/quantum-computing/quantum-fourier-transform",
                    "expected_results": ["transformada en base de Fourier", "superposición uniforme"]
                },
                {
                    "name": "QFT de 4 qubits",
                    "parameters": {"n_qubits": 4},
                    "description": "Transformada de Fourier en 4 qubits",
                    "endpoint": "POST /api/quantum-computing/quantum-fourier-transform",
                    "expected_results": ["mayor resolución de frecuencia", "más puertas cuánticas"]
                }
            ],
            "vqe_examples": [
                {
                    "name": "VQE para molécula H₂",
                    "parameters": {"n_qubits": 2},
                    "description": "Optimización de energía molecular usando VQE",
                    "endpoint": "POST /api/quantum-computing/vqe",
                    "expected_results": ["energía del estado fundamental", "comparación con cálculo clásico"]
                },
                {
                    "name": "VQE para sistema de 4 qubits",
                    "parameters": {"n_qubits": 4},
                    "description": "Optimización en sistema más grande",
                    "endpoint": "POST /api/quantum-computing/vqe",
                    "expected_results": ["convergencia del algoritmo", "energía optimizada"]
                }
            ],
            "comparison_examples": [
                {
                    "name": "Comparación factorial",
                    "parameters": {"problem_size": 4},
                    "description": "Comparación de cálculo de factorial",
                    "endpoint": "POST /api/quantum-computing/quantum-classical-comparison",
                    "expected_results": ["tiempo cuántico vs clásico", "complejidad computacional"]
                },
                {
                    "name": "Comparación búsqueda",
                    "parameters": {"problem_size": 8},
                    "description": "Comparación de algoritmos de búsqueda",
                    "endpoint": "POST /api/quantum-computing/quantum-classical-comparison",
                    "expected_results": ["ventaja cuántica O(√N) vs O(N)", "escalabilidad"]
                }
            ],
            "tips": [
                "Los estados de Bell demuestran entrelazamiento perfecto",
                "Grover proporciona ventaja cuadrática en búsqueda no estructurada",
                "QFT es fundamental para muchos algoritmos cuánticos (Shor, etc.)",
                "VQE combina computación cuántica y clásica para optimización",
                "La ventaja cuántica se vuelve significativa en problemas grandes"
            ],
            "metadata": {
                "execution_time_seconds": execution_time,
                "timestamp": datetime.datetime.now().isoformat(),
                "examples_count": 10,
                "categories_count": 5
            }
        }

        logger.info("✅ Ejemplos de algoritmos obtenidos exitosamente: %d ejemplos en %d categorías (tiempo: %.4fs)",
                   examples_data["metadata"]["examples_count"], examples_data["metadata"]["categories_count"], execution_time)

        return BaseResponse(
            success=True,
            message="Ejemplos de algoritmos de computación cuántica",
            data=examples_data
        )

    except QuantumError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error obteniendo ejemplos de algoritmos: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno obteniendo ejemplos: {str(e)}"
        ) from e

@router.post("/bell-state", response_model=BaseResponse)
async def create_bell_state(framework: str = "qiskit"):
    """
    🔗 Crea y simula un estado de Bell de forma intuitiva

    Crea un estado de Bell con entrelazamiento máximo entre dos qubits,
    demostrando los principios fundamentales de la computación cuántica.

    Args:
        framework: Framework de computación cuántica ("qiskit" o "cirq")

    Returns:
        BaseResponse: Estado de Bell con análisis detallado del entrelazamiento

    Raises:
        HTTPException: Si hay error en la creación o framework no soportado

    Example:
        POST /bell-state?framework=qiskit
        Response: {"success": true, "message": "Estado de Bell creado", "data": {...}}
    """
    start_time = datetime.datetime.now()

    try:
        # Validación de entrada
        if framework.lower() not in ["qiskit", "cirq"]:
            logger.warning("🚫 Framework no soportado para estado de Bell: %s", framework)
            raise HTTPException(
                status_code=400,
                detail="Framework debe ser 'qiskit' o 'cirq'"
            )

        logger.info("🔗 Creando estado de Bell usando framework: %s", framework)

        # Crear estado de Bell
        if framework.lower() == "qiskit":
            result = service.create_bell_state_qiskit()
        else:
            result = service.create_bell_state_cirq()

        if "error" in result:
            logger.error("❌ Error en creación de estado de Bell: %s", result["error"])
            raise HTTPException(status_code=400, detail=result["error"])

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        # Agregar explicaciones detalladas
        result["explanations"] = {
            "bell_state_definition": "Estado |Φ⁺⟩ = (|00⟩ + |11⟩)/√2",
            "entanglement": "Entrelazamiento máximo entre dos qubits",
            "measurement_correlation": "Mediciones siempre dan resultados correlacionados",
            "no_local_hidden_variables": "Viola las desigualdades de Bell",
            "quantum_superposition": "Superposición coherente de estados clásicos"
        }

        result["metadata"] = {
            "framework": framework,
            "execution_time_seconds": execution_time,
            "timestamp": datetime.datetime.now().isoformat(),
            "algorithm_type": "bell_state"
        }

        logger.info("✅ Estado de Bell creado exitosamente usando %s (tiempo: %.4fs)", framework, execution_time)

        return BaseResponse(
            success=True,
            message=f"Estado de Bell creado exitosamente usando {framework}",
            data=result
        )

    except HTTPException:
        raise
    except QuantumError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error creando estado de Bell: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=400,
            detail=f"Error creando estado de Bell: {str(e)}. Verifica el framework especificado."
        ) from e

@router.post("/grover-search", response_model=BaseResponse)
async def grover_search(
    n_qubits: int = 2,
    target_state: str = "11"
):
    """
    🔍 Implementa el algoritmo de búsqueda de Grover de forma intuitiva

    Ejecuta el algoritmo de búsqueda cuántica de Grover que proporciona
    ventaja cuadrática sobre los algoritmos clásicos de búsqueda.

    Args:
        n_qubits: Número de qubits (actualmente soporta solo 2)
        target_state: Estado objetivo a buscar (cadena de 2 bits, ej: "11")

    Returns:
        BaseResponse: Resultado de la búsqueda con análisis de amplificación de amplitud

    Raises:
        HTTPException: Si hay error en la búsqueda o parámetros inválidos

    Example:
        POST /grover-search?n_qubits=2&target_state=11
        Response: {"success": true, "message": "Búsqueda de Grover completada", "data": {...}}
    """
    start_time = datetime.datetime.now()

    try:
        # Validación de entrada
        if n_qubits != 2:
            logger.warning("🚫 Número de qubits no soportado para Grover: %d", n_qubits)
            raise HTTPException(
                status_code=400,
                detail="Actualmente solo se soporta búsqueda de Grover con 2 qubits"
            )
        if len(target_state) != 2 or not all(c in '01' for c in target_state):
            logger.warning("🚫 Estado objetivo inválido: %s", target_state)
            raise HTTPException(
                status_code=400,
                detail="El estado objetivo debe ser una cadena de 2 bits (ej: '11', '01')"
            )

        logger.info("🔍 Iniciando búsqueda de Grover: %d qubits, estado objetivo |%s⟩", n_qubits, target_state)

        # Ejecutar algoritmo de Grover
        result = service.create_grover_search_qiskit(n_qubits, target_state)
        if "error" in result:
            logger.error("❌ Error en algoritmo de Grover: %s", result["error"])
            raise HTTPException(status_code=400, detail=result["error"])

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        # Agregar explicaciones
        result["explanations"] = {
            "grover_algorithm": "Algoritmo de búsqueda cuántica con ventaja cuadrática",
            "amplitude_amplification": "Amplificación de la amplitud del estado objetivo",
            "oracle": f"Oráculo marca el estado |{target_state}⟩",
            "diffusion_operator": "Operador de difusión amplifica la amplitud marcada",
            "optimal_iterations": "Número óptimo de iteraciones: π√N/4",
            "probability_amplification": f"Probabilidad del estado objetivo: ~{0.81 if target_state else 'baja'}"
        }

        result["metadata"] = {
            "n_qubits": n_qubits,
            "target_state": target_state,
            "execution_time_seconds": execution_time,
            "timestamp": datetime.datetime.now().isoformat(),
            "algorithm_type": "grover_search"
        }

        logger.info("✅ Búsqueda de Grover completada: estado |%s⟩ encontrado (tiempo: %.4fs)", target_state, execution_time)

        return BaseResponse(
            success=True,
            message=f"Búsqueda de Grover completada - buscando estado |{target_state}⟩",
            data=result
        )

    except HTTPException:
        raise
    except QuantumError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error en búsqueda de Grover: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=400,
            detail=f"Error en búsqueda de Grover: {str(e)}. Verifica los parámetros."
        ) from e

@router.post("/quantum-fourier-transform", response_model=BaseResponse)
async def quantum_fourier_transform(n_qubits: int = 3):
    """
    🌊 Implementa la Transformada de Fourier Cuántica (QFT)

    Ejecuta la Transformada de Fourier Cuántica, componente fundamental
    de muchos algoritmos cuánticos como Shor y estimación de fase.

    Args:
        n_qubits: Número de qubits para la transformada (1-10)

    Returns:
        BaseResponse: Transformada de Fourier con análisis de frecuencias

    Raises:
        HTTPException: Si hay error en la QFT o número de qubits inválido

    Example:
        POST /quantum-fourier-transform?n_qubits=3
        Response: {"success": true, "message": "QFT completada para 3 qubits", "data": {...}}
    """
    start_time = datetime.datetime.now()

    try:
        # Validación de entrada
        if n_qubits < 1 or n_qubits > 10:
            logger.warning("🚫 Número de qubits fuera de rango para QFT: %d", n_qubits)
            raise HTTPException(
                status_code=400,
                detail="El número de qubits debe estar entre 1 y 10"
            )

        logger.info("🌊 Ejecutando Transformada de Fourier Cuántica para %d qubits", n_qubits)

        # Ejecutar QFT
        result = service.create_quantum_fourier_transform_qiskit(n_qubits)
        if "error" in result:
            logger.error("❌ Error en QFT: %s", result["error"])
            raise HTTPException(status_code=400, detail=result["error"])

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        # Agregar explicaciones
        result["explanations"] = {
            "qft_definition": "Transformada de Fourier en la base computacional",
            "phase_estimation": "Fundamental para estimación de fase cuántica",
            "shor_algorithm": "Componente clave del algoritmo de factorización de Shor",
            "frequency_domain": "Convierte del dominio del tiempo al dominio de frecuencia",
            "inverse_qft": "La QFT inversa recupera el estado original",
            "computational_complexity": f"Complejidad: O(n²) para {n_qubits} qubits"
        }

        result["metadata"] = {
            "n_qubits": n_qubits,
            "execution_time_seconds": execution_time,
            "timestamp": datetime.datetime.now().isoformat(),
            "algorithm_type": "quantum_fourier_transform"
        }

        logger.info("✅ QFT completada para %d qubits (tiempo: %.4fs)", n_qubits, execution_time)

        return BaseResponse(
            success=True,
            message=f"Transformada de Fourier Cuántica completada para {n_qubits} qubits",
            data=result
        )

    except HTTPException:
        raise
    except QuantumError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error en QFT: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=400,
            detail=f"Error en QFT: {str(e)}. Verifica el número de qubits."
        ) from e

@router.post("/vqe", response_model=BaseResponse)
async def variational_quantum_eigensolver(n_qubits: int = 2):
    """
    ⚛️ Simula el Solucionador Variacional Cuántico (VQE)

    Ejecuta el algoritmo VQE para encontrar el estado fundamental de un
    sistema cuántico, combinando computación cuántica y optimización clásica.

    Args:
        n_qubits: Número de qubits para el ansatz (1-6)

    Returns:
        BaseResponse: Optimización variacional con energía del estado fundamental

    Raises:
        HTTPException: Si hay error en VQE o número de qubits inválido

    Example:
        POST /vqe?n_qubits=2
        Response: {"success": true, "message": "VQE completado para 2 qubits", "data": {...}}
    """
    start_time = datetime.datetime.now()

    try:
        # Validación de entrada
        if n_qubits < 1 or n_qubits > 6:
            logger.warning("🚫 Número de qubits fuera de rango para VQE: %d", n_qubits)
            raise HTTPException(
                status_code=400,
                detail="El número de qubits debe estar entre 1 y 6 para VQE"
            )

        logger.info("⚛️ Ejecutando VQE para sistema de %d qubits", n_qubits)

        # Ejecutar VQE
        params = {"n_qubits": n_qubits}
        result = service.simulate_variational_quantum_eigensolver(params)
        if "error" in result:
            logger.error("❌ Error en VQE: %s", result["error"])
            raise HTTPException(status_code=400, detail=result["error"])

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        # Agregar explicaciones
        result["explanations"] = {
            "vqe_principle": "Optimización híbrida cuántico-clásica",
            "variational_ansatz": f"Ansatz variacional con {n_qubits} qubits",
            "energy_minimization": "Minimización de la energía del Hamiltoniano",
            "quantum_expectation": "Cálculo de valores esperados en el computador cuántico",
            "classical_optimization": "Optimización clásica de parámetros variacionales",
            "ground_state_energy": "Energía del estado fundamental molecular"
        }

        result["metadata"] = {
            "n_qubits": n_qubits,
            "execution_time_seconds": execution_time,
            "timestamp": datetime.datetime.now().isoformat(),
            "algorithm_type": "variational_quantum_eigensolver"
        }

        logger.info("✅ VQE completado para sistema de %d qubits (tiempo: %.4fs)", n_qubits, execution_time)

        return BaseResponse(
            success=True,
            message=f"VQE completado para sistema de {n_qubits} qubits",
            data=result
        )

    except HTTPException:
        raise
    except QuantumError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error en VQE: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=400,
            detail=f"Error en VQE: {str(e)}. Verifica el número de qubits."
        ) from e

@router.post("/quantum-classical-comparison", response_model=BaseResponse)
async def compare_quantum_vs_classical(problem_size: int = 4):
    """
    ⚖️ Compara el rendimiento de algoritmos cuánticos vs clásicos

    Ejecuta algoritmos equivalentes en computación cuántica y clásica
    para demostrar las ventajas cuánticas en diferentes tipos de problemas.

    Args:
        problem_size: Tamaño del problema a resolver (1-20)

    Returns:
        BaseResponse: Comparación detallada de complejidad y rendimiento

    Raises:
        HTTPException: Si hay error en la comparación o tamaño inválido

    Example:
        POST /quantum-classical-comparison?problem_size=8
        Response: {"success": true, "message": "Comparación completada", "data": {...}}
    """
    start_time = datetime.datetime.now()

    try:
        # Validación de entrada
        if problem_size < 1 or problem_size > 20:
            logger.warning("🚫 Tamaño de problema fuera de rango: %d", problem_size)
            raise HTTPException(
                status_code=400,
                detail="El tamaño del problema debe estar entre 1 y 20"
            )

        logger.info("⚖️ Comparando rendimiento cuántico vs clásico para problema de tamaño %d", problem_size)

        # Ejecutar comparación
        result = service.compare_quantum_vs_classical(problem_size)
        if "error" in result:
            logger.error("❌ Error en comparación cuántico-clásico: %s", result["error"])
            raise HTTPException(status_code=400, detail=result["error"])

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        # Agregar explicaciones
        result["explanations"] = {
            "quantum_advantage": "Ventaja cuántica en ciertos problemas computacionales",
            "grover_speedup": f"Grover: O(√{problem_size}) vs O({problem_size}) clásico",
            "shor_algorithm": "Shor: factorización exponencialmente más rápida",
            "quantum_supremacy": "Punto donde los computadores cuánticos superan a los clásicos",
            "hybrid_algorithms": "Algoritmos híbridos (VQE, QAOA) para problemas actuales"
        }

        result["metadata"] = {
            "problem_size": problem_size,
            "execution_time_seconds": execution_time,
            "timestamp": datetime.datetime.now().isoformat(),
            "comparison_type": "quantum_vs_classical"
        }

        logger.info("✅ Comparación cuántico-clásico completada para problema de tamaño %d (tiempo: %.4fs)", problem_size, execution_time)

        return BaseResponse(
            success=True,
            message=f"Comparación cuántico-clásico completada para problema de tamaño {problem_size}",
            data=result
        )

    except HTTPException:
        raise
    except QuantumError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error en comparación cuántico-clásico: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=400,
            detail=f"Error en comparación: {str(e)}. Verifica el tamaño del problema."
        ) from e

@router.get("/quick-bell/{framework}")
async def quick_bell_state(framework: str = "qiskit"):
    """
    ⚡ Creación rápida de estado de Bell con framework en la URL

    Proporciona una versión simplificada del estado de Bell para demostraciones
    rápidas y aprendizaje, con información esencial sobre entrelazamiento.

    Args:
        framework: Framework a usar ("qiskit" o "cirq")

    Returns:
        BaseResponse: Estado de Bell básico con información esencial

    Raises:
        HTTPException: Si hay error o framework no soportado

    Example:
        GET /quick-bell/qiskit
        Response: {"success": true, "message": "Estado de Bell rápido usando qiskit", "data": {...}}
    """
    start_time = datetime.datetime.now()

    try:
        # Validación de entrada
        if framework.lower() not in ["qiskit", "cirq"]:
            logger.warning("🚫 Framework no soportado para estado de Bell rápido: %s", framework)
            raise HTTPException(
                status_code=400,
                detail="Framework debe ser 'qiskit' o 'cirq'"
            )

        logger.info("⚡ Creando estado de Bell rápido usando framework: %s", framework)

        # Crear estado de Bell
        if framework.lower() == "qiskit":
            result = service.create_bell_state_qiskit()
        else:
            result = service.create_bell_state_cirq()

        if "error" in result:
            logger.error("❌ Error en estado de Bell rápido: %s", result["error"])
            raise HTTPException(status_code=400, detail=result["error"])

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        response_data = {
            "framework": framework,
            "bell_state": "|Φ⁺⟩ = (|00⟩ + |11⟩)/√2",
            "entanglement": "Máximo (concurrencia = 1.0)",
            "measurement_probabilities": {"00": 0.5, "11": 0.5},
            "quick_facts": [
                "Entrelazamiento perfecto entre 2 qubits",
                "Probabilidades iguales para estados 00 y 11",
                "Viola desigualdades de Bell",
                "Fundamental para computación cuántica"
            ],
            "metadata": {
                "execution_time_seconds": execution_time,
                "timestamp": datetime.datetime.now().isoformat(),
                "algorithm_type": "quick_bell_state"
            }
        }

        logger.info("✅ Estado de Bell rápido completado usando %s (tiempo: %.4fs)", framework, execution_time)

        return BaseResponse(
            success=True,
            message=f"Estado de Bell rápido usando {framework}",
            data=response_data
        )

    except HTTPException:
        raise
    except QuantumError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error en estado de Bell rápido: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=400,
            detail=f"Error en estado de Bell rápido: {str(e)}. Verifica el framework."
        ) from e


@router.post("/grover-search")
async def grover_quantum_search(request: QuantumComputingRequest) -> BaseResponse:
    """
    🔍 Algoritmo de Grover para Búsqueda Cuántica
    
    Implementa el algoritmo de Grover para búsqueda no estructurada
    con ventaja cuadrática sobre algoritmos clásicos.
    
    Ejemplo de payload:
    ```json
    {
        "qubits": 3,
        "database_size": 8,
        "marked_items": [3, 7],
        "max_iterations": 50,
        "shots": 8192
    }
    ```
    
    Returns:
        BaseResponse: Resultados de búsqueda con probabilidades
    """
    start_time = datetime.datetime.now()
    
    try:
        logger.info("🔍 Iniciando algoritmo de Grover - Base de datos: %d elementos", 
                   request.qubits)
        
        # Parámetros del algoritmo Grover
        database_size = request.parameters.get("database_size", 2 ** request.qubits)
        marked_items = request.parameters.get("marked_items", [database_size - 1])
        max_iterations = request.parameters.get("max_iterations", 50)
        
        # Validaciones específicas para Grover
        if database_size <= 0 or database_size & (database_size - 1) != 0:
            raise HTTPException(
                status_code=400,
                detail="Database size must be a positive power of 2"
            )
        
        if not marked_items or any(item >= database_size or item < 0 for item in marked_items):
            raise HTTPException(
                status_code=400,
                detail="Invalid marked items for database size"
            )
        
        # Ejecutar algoritmo de Grover
        result = await service.simulate_grover_search(
            database_size=database_size,
            marked_items=marked_items,
            max_iterations=max_iterations
        )
        
        if "error" in result:
            logger.error("❌ Error en algoritmo de Grover: %s", result["error"])
            raise HTTPException(status_code=400, detail=result["error"])
        
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        
        # Formatear respuesta
        response_data = {
            **result,
            "algorithm_info": {
                "description": "Algoritmo de Grover para búsqueda cuántica",
                "complexity": "O(√N) vs O(N) clásico",
                "advantage": "Ventaja cuadrática",
                "discovery_year": 1996,
                "inventor": "Lov Grover"
            },
            "performance": {
                "execution_time_seconds": execution_time,
                "quantum_speedup": result.get("quantum_speedup", "Unknown"),
                "success_rate": result.get("success_probability", 0) * 100
            },
            "metadata": {
                "timestamp": datetime.datetime.now().isoformat(),
                "framework": "qiskit"
            }
        }
        
        logger.info("✅ Algoritmo de Grover completado - Éxito: %.1f%% (tiempo: %.4fs)", 
                   result.get("success_probability", 0) * 100, execution_time)
        
        return BaseResponse(
            success=True,
            message=f"Búsqueda de Grover completada con {result.get('success_probability', 0)*100:.1f}% de éxito",
            data=response_data
        )
        
    except HTTPException:
        raise
    except QuantumError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error en algoritmo de Grover: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error en algoritmo de Grover: {str(e)}"
        ) from e


@router.post("/shor-factorization")
async def shor_quantum_factorization(request: QuantumComputingRequest) -> BaseResponse:
    """
    🔢 Algoritmo de Shor para Factorización Cuántica
    
    Implementa el algoritmo de Shor para factorización de enteros
    con ventaja exponencial sobre métodos clásicos.
    
    Ejemplo de payload:
    ```json
    {
        "qubits": 6,
        "parameters": {
            "N": 15,
            "a": 7
        }
    }
    ```
    
    Returns:
        BaseResponse: Factores encontrados y análisis del algoritmo
    """
    start_time = datetime.datetime.now()
    
    try:
        # Parámetros del algoritmo de Shor
        N = request.parameters.get("N")
        a = request.parameters.get("a")
        
        if N is None:
            raise HTTPException(
                status_code=400,
                detail="Parameter 'N' (number to factor) is required"
            )
        
        logger.info("🔢 Iniciando algoritmo de Shor - Factorizando: %d", N)
        
        # Ejecutar algoritmo de Shor
        result = await service.simulate_shor_algorithm(N=N, a=a)
        
        if "error" in result:
            logger.error("❌ Error en algoritmo de Shor: %s", result["error"])
            raise HTTPException(status_code=400, detail=result["error"])
        
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        
        # Formatear respuesta
        response_data = {
            **result,
            "algorithm_info": {
                "description": "Algoritmo de Shor para factorización cuántica",
                "complexity": "O((log N)³) vs O(exp(√(log N log log N))) clásico",
                "advantage": "Ventaja exponencial",
                "discovery_year": 1994,
                "inventor": "Peter Shor",
                "cryptographic_impact": "Amenaza RSA y criptografía de clave pública"
            },
            "factorization_result": {
                "input_number": N,
                "factors_found": result.get("factors", []),
                "verification_passed": result.get("verification", False),
                "method_used": result.get("algorithm", "Shor's Algorithm")
            },
            "performance": {
                "execution_time_seconds": execution_time,
                "quantum_advantage": result.get("speedup", "Exponential for large N")
            },
            "metadata": {
                "timestamp": datetime.datetime.now().isoformat(),
                "framework": "qiskit",
                "educational_purpose": True,
                "security_note": "Implementación educativa - no usar para criptoanálisis real"
            }
        }
        
        factors = result.get("factors", [])
        logger.info("✅ Algoritmo de Shor completado - %d = %s (tiempo: %.4fs)", 
                   N, " × ".join(map(str, factors)), execution_time)
        
        return BaseResponse(
            success=True,
            message=f"Factorización completada: {N} = {' × '.join(map(str, factors))}",
            data=response_data
        )
        
    except HTTPException:
        raise
    except QuantumError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error en algoritmo de Shor: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error en algoritmo de Shor: {str(e)}"
        ) from e


@router.post("/noisy-simulation")
async def noisy_circuit_simulation(request: QuantumComputingRequest) -> BaseResponse:
    """
    🌀 Simulación de Circuitos Cuánticos con Ruido
    
    Simula circuitos cuánticos bajo condiciones realistas con
    modelos de ruido que representan imperfecciones del hardware.
    
    Ejemplo de payload:
    ```json
    {
        "qubits": 2,
        "parameters": {
            "circuit_type": "bell",
            "noise_model": "depolarizing",
            "noise_strength": 0.05,
            "shots": 8192
        }
    }
    ```
    
    Returns:
        BaseResponse: Comparación entre simulación ideal y ruidosa
    """
    start_time = datetime.datetime.now()
    
    try:
        # Parámetros de ruido
        circuit_type = request.parameters.get("circuit_type", "bell")
        noise_model = request.parameters.get("noise_model", "depolarizing")
        noise_strength = request.parameters.get("noise_strength", 0.01)
        shots = request.parameters.get("shots", 8192)
        
        logger.info("🌀 Iniciando simulación con ruido - Tipo: %s, Modelo: %s, Fuerza: %.3f", 
                   circuit_type, noise_model, noise_strength)
        
        # Validaciones
        valid_circuits = ["bell", "grover", "random"]
        if circuit_type not in valid_circuits:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid circuit type. Choose from: {valid_circuits}"
            )
        
        valid_noise_models = ["depolarizing", "amplitude_damping", "phase_damping"]
        if noise_model not in valid_noise_models:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid noise model. Choose from: {valid_noise_models}"
            )
        
        if not (0 <= noise_strength <= 1):
            raise HTTPException(
                status_code=400,
                detail="Noise strength must be between 0.0 and 1.0"
            )
        
        # Ejecutar simulación con ruido
        result = await service.simulate_noisy_circuit(
            circuit_type=circuit_type,
            noise_model=noise_model,
            noise_strength=noise_strength,
            shots=shots
        )
        
        if "error" in result:
            logger.error("❌ Error en simulación con ruido: %s", result["error"])
            raise HTTPException(status_code=400, detail=result["error"])
        
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        
        # Formatear respuesta
        response_data = {
            **result,
            "noise_modeling_info": {
                "description": "Simulación realista de errores cuánticos",
                "purpose": "Evaluar robustez de algoritmos cuánticos",
                "applications": [
                    "Diseño de códigos de corrección de errores",
                    "Optimización de algoritmos NISQ",
                    "Estimación de requisitos de hardware"
                ]
            },
            "hardware_context": {
                "typical_gate_fidelities": {
                    "single_qubit": "99.9%",
                    "two_qubit": "99.0%",
                    "readout": "98.5%"
                },
                "decoherence_times": {
                    "T1_relaxation": "50-100 μs",
                    "T2_dephasing": "20-80 μs"
                }
            },
            "performance": {
                "execution_time_seconds": execution_time,
                "fidelity_degradation": result.get("comparison_metrics", {}).get("noise_impact", "Unknown"),
                "quantum_error_rate": noise_strength * 100
            },
            "metadata": {
                "timestamp": datetime.datetime.now().isoformat(),
                "framework": "qiskit",
                "simulation_type": "noisy_quantum"
            }
        }
        
        fidelity = result.get("comparison_metrics", {}).get("fidelity", 0)
        logger.info("✅ Simulación con ruido completada - Fidelidad: %.3f (tiempo: %.4fs)", 
                   fidelity, execution_time)
        
        return BaseResponse(
            success=True,
            message=f"Simulación con ruido completada - Fidelidad: {fidelity:.3f}",
            data=response_data
        )
        
    except HTTPException:
        raise
    except QuantumError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error en simulación con ruido: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error en simulación con ruido: {str(e)}"
        ) from e


@router.post("/qaoa/maxcut")
async def qaoa_maxcut(request: QuantumComputingRequest) -> BaseResponse:
    """
    🧠 Resolución de MaxCut con QAOA de última generación

    Acepta grafos arbitrarios (lista de aristas o matriz de adyacencia) y ejecuta
    QAOA con optimizadores avanzados, comparando contra una línea base clásica.
    """
    start_time = datetime.datetime.now()

    try:
        logger.info("🧠 Ejecutando QAOA MaxCut con parámetros: %s", request.parameters)

        result = service.run_qaoa_maxcut(request.parameters or {})

        if "error" in result:
            logger.error("❌ QAOA MaxCut falló: %s", result["error"])
            raise HTTPException(status_code=400, detail=result["error"])

        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        response_data = {
            **result,
            "metadata": {
                "timestamp": datetime.datetime.now().isoformat(),
                "execution_time_seconds": execution_time,
                "framework": result.get("framework", "qiskit")
            }
        }

        logger.info("✅ QAOA MaxCut completado - corte %.3f", result["results"].get("cut_value", 0.0))

        return BaseResponse(
            success=True,
            message="QAOA MaxCut ejecutado exitosamente",
            data=response_data
        )

    except HTTPException:
        raise
    except QuantumError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error inesperado en QAOA MaxCut: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error en QAOA MaxCut: {str(e)}"
        ) from e


@router.post("/qml/kernel-classifier")
async def quantum_kernel_classifier(request: QuantumComputingRequest) -> BaseResponse:
    """
    🧬 Clasificador cuántico basado en kernels (QSVC)

    Ejecuta un `QuantumKernel` con `QSVC` sobre el dataset proporcionado y devuelve
    métricas de entrenamiento y pruebas, además de la matriz de kernel resultante.
    """
    start_time = datetime.datetime.now()

    try:
        logger.info("🧬 Ejecutando quantum kernel classification con parámetros: %s", request.parameters)

        result = service.run_quantum_kernel_classification(request.parameters or {})

        if "error" in result:
            logger.error("❌ Quantum kernel classification falló: %s", result["error"])
            raise HTTPException(status_code=400, detail=result["error"])

        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        response_data = {
            **result,
            "metadata": {
                "timestamp": datetime.datetime.now().isoformat(),
                "execution_time_seconds": execution_time,
                "framework": result.get("framework", "qiskit")
            }
        }

        logger.info("✅ Quantum kernel classification completado - accuracy entrenamiento %.3f", result["results"].get("train_accuracy", 0.0))

        return BaseResponse(
            success=True,
            message="Quantum kernel classification ejecutado exitosamente",
            data=response_data
        )

    except HTTPException:
        raise
    except QuantumError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error inesperado en quantum kernel classification: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error en quantum kernel classification: {str(e)}"
        ) from e


@router.post("/error-mitigation/zero-noise")
async def quantum_error_mitigation(request: QuantumComputingRequest) -> BaseResponse:
    """
    🛡️ Mitigación de error cuántico mediante zero-noise extrapolation (ZNE)

    Ejecuta un circuito especificado por el usuario con modelos de ruido controlados,
    estira compuertas para distintos factores y extrapola al límite de ruido cero.
    """
    start_time = datetime.datetime.now()

    try:
        logger.info("🛡️ Ejecutando ZNE con parámetros: %s", request.parameters)

        result = service.run_error_mitigation(request.parameters or {})

        if "error" in result:
            logger.error("❌ Quantum error mitigation falló: %s", result["error"])
            raise HTTPException(status_code=400, detail=result["error"])

        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        response_data = {
            **result,
            "metadata": {
                "timestamp": datetime.datetime.now().isoformat(),
                "execution_time_seconds": execution_time,
                "framework": result.get("framework", "qiskit")
            }
        }

        logger.info(
            "✅ ZNE completado - raw %.4f -> mitigado %.4f",
            result["results"].get("raw_expectation", 0.0),
            result["results"].get("mitigated_expectation", 0.0),
        )

        return BaseResponse(
            success=True,
            message="Zero-noise extrapolation ejecutado exitosamente",
            data=response_data
        )

    except HTTPException:
        raise
    except QuantumError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error(
            "❌ Error inesperado en quantum error mitigation: %s (tiempo: %.4fs)",
            str(e),
            execution_time,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error en quantum error mitigation: {str(e)}"
        ) from e
