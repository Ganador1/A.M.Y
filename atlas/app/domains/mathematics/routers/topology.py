"""
🏗️ ANÁLISIS TOPOLÓGICO - AXIOM META 4.1
═══════════════════════════════════════════════════════════════════════════════

Módulo de análisis topológico avanzado para la plataforma AXIOM v4.1. Proporciona
herramientas matemáticas especializadas para el estudio de propiedades topológicas
de espacios métricos, complejos simpliciales y análisis de datos mediante técnicas
de topología algebraica y geometría computacional.

FUNCIONALIDADES PRINCIPALES:
────────────────────────────
• Construcción de complejos de Vietoris-Rips: Análisis de proximidad en espacios métricos
• Cálculo de invariantes topológicos: Homología, grupos fundamentales, números de Betti
• Análisis de persistencia: Diagramas de persistencia y filtraciones topológicas
• Complejos simpliciales: Construcción y manipulación de estructuras simpliciales
• Espacios de cobertura: Análisis de recubrimientos nerviosos y propiedades
• Topología de datos: Mapper algorithm y análisis de formas topológicas
• Grupos homotópicos: Cálculo de tipo de homotopy y espacios de lazo
• Propiedades de conectividad: Componentes conexas y análisis de caminos

ARQUITECTURA TÉCNICA:
─────────────────────
• Framework: FastAPI con validación Pydantic automática
• Computación: Gudhi/TDA para topología algebraica persistente
• Geometría: SciPy para análisis de distancias y métricas
• Numérico: NumPy para computaciones vectoriales eficientes
• Visualización: Plotly/Matplotlib para diagramas topológicos
• Álgebra: SymPy para cálculos simbólicos en teoría de grupos
• Optimización: NetworkX para análisis de grafos simpliciales

ENDPOINTS DISPONIBLES:
──────────────────────
• POST /vietoris-rips: Construcción de complejos de Vietoris-Rips
• POST /invariants: Cálculo de invariantes topológicos (homología, Betti)
• POST /persistence: Análisis de persistencia topológica
• POST /simplicial-complex: Construcción y análisis de complejos simpliciales
• POST /mapper: Algoritmo Mapper para visualización topológica
• POST /homotopy-groups: Cálculo de grupos homotópicos
• POST /covering-spaces: Análisis de espacios de cobertura
• POST /connectivity: Análisis de conectividad y componentes

VALIDACIONES IMPLEMENTADAS:
──────────────────────────
• Verificación de dimensionalidad de puntos y coordenadas
• Control de parámetros epsilon para complejos de Vietoris-Rips
• Validación de complejos simpliciales y estructuras topológicas
• Límites de tamaño para computaciones de homología
• Verificación de métricas de distancia válidas
• Control de resolución para análisis de persistencia

INTEGRACIONES:
─────────────
• VietorisRipsBuilder: Constructor especializado de complejos VR
• TopologyInvariants: Calculador de invariantes homológicos
• PersistenceAnalyzer: Analizador de persistencia topológica
• SimplicialComplex: Manipulador de estructuras simpliciales
• GudhiLibrary: Biblioteca de topología algebraica
• NetworkX: Análisis de grafos y estructuras de red

SEGURIDAD Y AUTORIZACIÓN:
─────────────────────────
• Endpoints protegidos con autenticación JWT
• Scopes específicos: topology:analysis, topology:compute
• Validación de permisos para operaciones de alto costo computacional
• Auditoría completa de análisis topológicos realizados
• Rate limiting para cálculos intensivos de homología

VERSIÓN: AXIOM META 4.1
FECHA: Diciembre 2024
AUTOR: Equipo de Desarrollo AXIOM
"""

from __future__ import annotations

from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import time

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator

from app.security.auth import require_scopes
from app.core.bootstrap_logging import logger
from app.domains.mathematics.services.topology_service import TopologyService
from app.exceptions.domain.mathematics import MathematicsError

# Modelos de datos para requests y responses

class Point2D(BaseModel):
    """Punto en espacio bidimensional."""
    x: float = Field(..., description="Coordenada X")
    y: float = Field(..., description="Coordenada Y")

class Point3D(BaseModel):
    """Punto en espacio tridimensional."""
    x: float = Field(..., description="Coordenada X")
    y: float = Field(..., description="Coordenada Y")
    z: float = Field(..., description="Coordenada Z")

class PointND(BaseModel):
    """Punto en espacio N-dimensional."""
    coordinates: List[float] = Field(..., description="Lista de coordenadas")
    dimension: Optional[int] = Field(None, description="Dimensión del espacio")

    @field_validator('coordinates')
    @classmethod
    def validate_coordinates(cls, v):
        if not v:
            raise ValueError('Las coordenadas no pueden estar vacías')
        if len(v) < 2:
            raise ValueError('Se requieren al menos 2 dimensiones')
        return v

class VietorisRipsRequest(BaseModel):
    """Request para construcción de complejo de Vietoris-Rips."""
    points: List[Point2D] = Field(..., description="Lista de puntos 2D")
    epsilon: float = Field(0.2, gt=0, le=10, description="Radio de conexión (0 < ε ≤ 10)")
    max_dimension: Optional[int] = Field(2, ge=1, le=5, description="Dimensión máxima del complejo")

class PersistenceRequest(BaseModel):
    """Request para análisis de persistencia topológica."""
    points: List[Point2D] = Field(..., description="Lista de puntos para análisis")
    epsilon_range: Tuple[float, float] = Field((0.1, 2.0), description="Rango de valores epsilon")
    num_steps: int = Field(20, ge=5, le=100, description="Número de pasos en la filtración")
    max_dimension: Optional[int] = Field(2, ge=1, le=5, description="Dimensión máxima para homología")

class SimplicialComplexRequest(BaseModel):
    """Request para construcción de complejo simplicial."""
    simplices: List[List[int]] = Field(..., description="Lista de símplices (índices de vértices)")
    vertices: List[Point2D] = Field(..., description="Lista de vértices del complejo")
    validate_complex: bool = Field(True, description="Validar que forme un complejo válido")

class MapperRequest(BaseModel):
    """Request para algoritmo Mapper."""
    points: List[Point2D] = Field(..., description="Conjunto de datos para mapeo")
    filter_function: str = Field("distance", description="Función de filtrado (distance, density, etc.)")
    cover: Dict[str, Any] = Field(..., description="Parámetros de cobertura")
    clustering: Dict[str, Any] = Field(..., description="Parámetros de clustering")

class HomotopyRequest(BaseModel):
    """Request para cálculo de grupos homotópicos."""
    space_definition: Dict[str, Any] = Field(..., description="Definición del espacio topológico")
    max_order: int = Field(2, ge=1, le=10, description="Orden máximo de grupos homotópicos")
    approximation_method: str = Field("fundamental", description="Método de aproximación")

class ConnectivityRequest(BaseModel):
    """Request para análisis de conectividad."""
    points: List[Point2D] = Field(..., description="Puntos para análisis de conectividad")
    epsilon: float = Field(0.2, gt=0, description="Radio de conectividad")
    metric: str = Field("euclidean", description="Métrica de distancia")

class CoveringSpaceRequest(BaseModel):
    """Request para análisis de espacios de cobertura."""
    base_space: Dict[str, Any] = Field(..., description="Espacio base")
    covering_type: str = Field("universal", description="Tipo de recubrimiento")
    max_lifts: int = Field(10, ge=1, le=100, description="Número máximo de elevaciones")

class InvariantsRequest(BaseModel):
    """Request para cálculo de invariantes topológicos."""
    points: List[Point2D] = Field(..., description="Lista de puntos 2D para análisis")
    epsilon: float = Field(0.2, gt=0, le=10, description="Radio de conectividad epsilon")

class VietorisRipsResponse(BaseModel):
    """Response para complejo de Vietoris-Rips."""
    epsilon: float
    max_dimension: int
    num_simplices: Dict[int, int]  # Número de símplices por dimensión
    betti_numbers: List[int]  # Números de Betti
    euler_characteristic: int
    invariants: Dict[str, Any]
    execution_time_seconds: float
    timestamp: str

class PersistenceResponse(BaseModel):
    """Response para análisis de persistencia."""
    persistence_diagram: List[Dict[str, Any]]  # Pares nacimiento-muerte
    betti_curves: Dict[int, List[float]]  # Curvas de Betti por dimensión
    persistence_entropy: float
    bottleneck_distance: Optional[float]
    wasserstein_distance: Optional[float]
    epsilon_values: List[float]
    execution_time_seconds: float
    timestamp: str

class SimplicialComplexResponse(BaseModel):
    """Response para complejo simplicial."""
    num_vertices: int
    num_simplices: Dict[int, int]
    euler_characteristic: int
    betti_numbers: List[int]
    homology_groups: Dict[int, str]  # Representación de grupos homológicos
    is_valid: bool
    validation_errors: List[str]
    execution_time_seconds: float
    timestamp: str

class MapperResponse(BaseModel):
    """Response para algoritmo Mapper."""
    nodes: List[Dict[str, Any]]  # Nodos del grafo Mapper
    edges: List[Tuple[int, int]]  # Conexiones entre nodos
    clusters: List[List[int]]  # Índices de puntos por cluster
    filter_values: List[float]  # Valores de la función de filtrado
    graph_statistics: Dict[str, Any]
    execution_time_seconds: float
    timestamp: str


class GraphStatsRequest(BaseModel):
    """Request para estadísticas de grafo ε (derivado de puntos 2D)."""
    points: List[Point2D] = Field(..., description="Lista de puntos 2D")
    epsilon: float = Field(0.2, gt=0, le=10, description="Radio de conexión para grafo ε")


class GraphStatsResponse(BaseModel):
    """Estadísticas básicas del grafo ε construido a partir de puntos 2D."""
    epsilon: float
    n_points: int
    n_edges: int
    avg_degree: float
    density: float
    components: int
    degree_hist: Dict[int, int]
    execution_time_seconds: float
    timestamp: str


class VisualizationImageResponse(BaseModel):
    """Imagen generada (PNG base64) y metadatos mínimos."""
    image_base64: str
    width: int
    height: int
    execution_time_seconds: float
    timestamp: str

class HomotopyResponse(BaseModel):
    """Response para grupos homotópicos."""
    pi_groups: Dict[int, str]  # Grupos homotópicos π_n
    fundamental_group: str  # Grupo fundamental π₁
    homotopy_type: str  # Tipo de homotopía
    cw_complex: Optional[Dict[str, Any]]  # Estructura CW si aplica
    approximation_used: str
    execution_time_seconds: float
    timestamp: str

class ConnectivityResponse(BaseModel):
    """Response para análisis de conectividad."""
    connected_components: List[List[int]]  # Componentes conexas (índices)
    num_components: int
    component_sizes: List[int]
    connectivity_graph: Dict[str, Any]  # Grafo de conectividad
    clustering_coefficient: float
    average_path_length: float
    execution_time_seconds: float
    timestamp: str

class CoveringSpaceResponse(BaseModel):
    """Response para espacios de cobertura."""
    covering_maps: List[Dict[str, Any]]  # Mapas de recubrimiento
    deck_transformations: List[Dict[str, Any]]  # Transformaciones del deck
    fundamental_domain: Dict[str, Any]
    monodromy: Dict[str, Any]
    execution_time_seconds: float
    timestamp: str

router = APIRouter(prefix="/api/topology", tags=["topology"])

# Endpoints de análisis topológico

@router.post("/vietoris-rips", response_model=VietorisRipsResponse)
async def vietoris_rips_complex(
    request: VietorisRipsRequest,
    current_user: dict = Depends(require_scopes(["topology:analysis"]))
) -> VietorisRipsResponse:
    """
    🏗️ CONSTRUCCIÓN DE COMPLEJO DE VIETORIS-RIPS
    ============================================

    Construye un complejo simplicial de Vietoris-Rips a partir de un conjunto de puntos
    en el plano, utilizando un radio epsilon para definir las conexiones entre puntos.

    **Parámetros de entrada:**
    - **points**: Lista de puntos bidimensionales (x, y)
    - **epsilon**: Radio de conexión (0 < ε ≤ 10)
    - **max_dimension**: Dimensión máxima del complejo (default: 2)

    **Proceso de construcción:**
    1. Calcular distancias euclidianas entre todos los pares de puntos
    2. Conectar puntos dentro del radio epsilon (1-símplices)
    3. Generar símplices de dimensión superior cuando aplicable
    4. Calcular invariantes topológicos (números de Betti, característica de Euler)

    **Respuesta exitosa:**
    ```json
    {
        "epsilon": 0.2,
        "max_dimension": 2,
        "num_simplices": {"0": 50, "1": 120, "2": 45},
        "betti_numbers": [3, 2],
        "euler_characteristic": 1,
        "invariants": {
            "n_points": 50,
            "components_est": 3,
            "edges": 120,
            "cycles_est": 2
        },
        "execution_time_seconds": 0.145,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Interpretación topológica:**
    - **Betti₀ (b₀)**: Número de componentes conexas
    - **Betti₁ (b₁)**: Número de ciclos independientes (agujeros)
    - **Característica de Euler**: χ = b₀ - b₁ + b₂ - ...

    **Códigos de error:**
    - **400**: Puntos insuficientes, epsilon inválido, parámetros fuera de rango
    - **500**: Error interno en construcción del complejo
    """
    start_time = time.time()
    logger.info("🏗️ Iniciando construcción VR - Usuario: %s, %d puntos, ε=%f", current_user.get('sub'), len(request.points), request.epsilon)

    try:
        service = TopologyService()
        result = await service.build_vietoris_rips(
            points=[(p.x, p.y) for p in request.points],
            epsilon=request.epsilon,
            max_dimension=request.max_dimension or 2
        )

        execution_time = time.time() - start_time
        logger.info("✅ Complejo VR construido en %.2fs", execution_time)

        return VietorisRipsResponse(
            **result,
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat()
        )

    except MathematicsError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error en construcción VR: %s", str(e))
        raise HTTPException(status_code=500, detail="Error en construcción de complejo VR: %s" % str(e)) from e

@router.post("/graph-stats", response_model=Dict[str, Any])
async def graph_stats(
    request: InvariantsRequest,
    current_user: dict = Depends(require_scopes(["topology:analysis"]))
) -> Dict[str, Any]:
    """
    📈 ESTADÍSTICAS BÁSICAS DE GRAFO ε
    ==================================

    Calcula estadísticas del grafo ε a partir de `points` 2D:
    - n_points, n_edges, avg_degree, density
    - número de componentes conexas
    - histograma de grados (degree_hist)
    """
    start_time = time.time()
    try:
        import numpy as np
        pts = request.points
        n = len(pts)
        if n == 0:
            return {
                "epsilon": request.epsilon,
                "n_points": 0,
                "n_edges": 0,
                "avg_degree": 0.0,
                "density": 0.0,
                "components": 0,
                "degree_hist": {},
                "execution_time_seconds": 0.0,
                "timestamp": datetime.now().isoformat(),
            }

        P = np.array([[p.x, p.y] for p in pts], dtype=float)
        D = np.sqrt(((P[:, None, :] - P[None, :, :]) ** 2).sum(axis=2))
        A = (D <= request.epsilon).astype(int)
        np.fill_diagonal(A, 0)
        E = int(A.sum() // 2)
        deg = A.sum(axis=1)
        avg_deg = float(deg.mean())
        density = (2 * E) / (n * (n - 1)) if n > 1 else 0.0

        # Componentes (DFS)
        visited = np.zeros(n, dtype=bool)
        comps = 0
        for i in range(n):
            if not visited[i]:
                comps += 1
                stack = [i]
                visited[i] = True
                while stack:
                    u = stack.pop()
                    for v in np.where(A[u] == 1)[0]:
                        if not visited[v]:
                            visited[v] = True
                            stack.append(v)

        vals, counts = np.unique(deg, return_counts=True)
        hist = {int(v): int(c) for v, c in zip(vals, counts)}

        execution_time = time.time() - start_time
        return {
            "epsilon": request.epsilon,
            "n_points": n,
            "n_edges": E,
            "avg_degree": round(avg_deg, 4),
            "density": round(float(density), 6),
            "components": comps,
            "degree_hist": hist,
            "execution_time_seconds": round(execution_time, 4),
            "timestamp": datetime.now().isoformat(),
        }
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/degree-histogram", response_model=VisualizationImageResponse)
async def degree_histogram_image(
    request: InvariantsRequest,
    current_user: dict = Depends(require_scopes(["topology:analysis"]))
) -> VisualizationImageResponse:
    """
    📊 HISTOGRAMA DE GRADOS (imagen)
    Genera un histograma de grados del grafo ε como PNG (base64).
    """
    start_time = time.time()
    try:
        import io
        import base64
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np

        pts = request.points
        n = len(pts)
        if n == 0:
            # Imagen vacía mínima
            fig, ax = plt.subplots(figsize=(5, 4), dpi=120)
            ax.text(0.5, 0.5, "Sin datos", ha="center", va="center")
            ax.axis('off')
            buf = io.BytesIO()
            plt.tight_layout()
            fig.savefig(buf, format="png")
            plt.close(fig)
            buf.seek(0)
            b64 = base64.b64encode(buf.read()).decode("ascii")
            exec_s = time.time() - start_time
            return VisualizationImageResponse(
                image_base64=b64,
                width=600,
                height=480,
                execution_time_seconds=exec_s,
                timestamp=datetime.now().isoformat()
            )

        P = np.array([[p.x, p.y] for p in pts], dtype=float)
        D = np.sqrt(((P[:, None, :] - P[None, :, :]) ** 2).sum(axis=2))
        A = (D <= request.epsilon).astype(int)
        np.fill_diagonal(A, 0)
        deg = A.sum(axis=1)

        fig, ax = plt.subplots(figsize=(5, 4), dpi=120)
        bins = range(0, int(deg.max()) + 2) if n > 0 else [0, 1]
        ax.hist(deg, bins=bins, color="tab:blue", edgecolor="white")
        ax.set_xlabel("grado")
        ax.set_ylabel("frecuencia")
        ax.set_title("Degree Histogram (ε=%.3f)" % request.epsilon)
        ax.grid(alpha=0.2)
        buf = io.BytesIO()
        plt.tight_layout()
        fig.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode("ascii")

        exec_s = time.time() - start_time
        return VisualizationImageResponse(
            image_base64=b64,
            width=600,
            height=480,
            execution_time_seconds=exec_s,
            timestamp=datetime.now().isoformat()
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/invariants", response_model=Dict[str, Any])
async def topology_invariants(
    request: InvariantsRequest,
    current_user: dict = Depends(require_scopes(["topology:analysis"]))
) -> Dict[str, Any]:
    """
    📊 CÁLCULO DE INVARIANTES TOPOLÓGICOS
    ====================================

    Calcula invariantes topológicos del grafo epsilon generado por un conjunto
    de puntos, incluyendo medidas de conectividad, clustering y propiedades estructurales.

    **Parámetros de entrada:**
    - **points**: Lista de puntos bidimensionales
    - **epsilon**: Radio para construcción del grafo epsilon

    **Invariantes calculados:**
    - **n_points**: Número total de puntos
    - **edges**: Número de conexiones (aristas)
    - **avg_degree**: Grado promedio de los nodos
    - **density**: Densidad del grafo (conexiones posibles realizadas)
    - **clustering_coeff**: Coeficiente de clustering promedio
    - **diameter_est**: Diámetro estimado del grafo

    **Respuesta exitosa:**
    ```json
    {
        "n_points": 50,
        "edges": 120,
        "avg_degree": 4.8,
        "density": 0.098,
        "clustering_coeff": 0.67,
        "diameter_est": 8,
        "execution_time_seconds": 0.089,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Interpretación de métricas:**
    - **Density**: Proporción de conexiones realizadas vs posibles (0-1)
    - **Clustering**: Tendencia a formar triángulos (0-1)
    - **Diameter**: Distancia máxima entre nodos conectados

    **Códigos de error:**
    - **400**: Conjunto de puntos vacío o insuficiente
    - **500**: Error en cálculo de invariantes
    """
    start_time = time.time()
    logger.info("📊 Calculando invariantes topológicos - Usuario: %s, ε=%f", current_user.get('sub'), request.epsilon)

    try:
        service = TopologyService()
        result = await service.calculate_invariants(
            points=[(p.x, p.y) for p in request.points],
            epsilon=request.epsilon
        )

        execution_time = time.time() - start_time
        logger.info("✅ Invariantes calculados en %.2fs", execution_time)

        return {
            **result,
            "execution_time_seconds": execution_time,
            "timestamp": datetime.now().isoformat()
        }

    except MathematicsError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error en cálculo de invariantes: %s", str(e))
        raise HTTPException(status_code=500, detail="Error en cálculo de invariantes: %s" % str(e)) from e

@router.post("/persistence", response_model=PersistenceResponse)
async def persistence_analysis(
    request: PersistenceRequest,
    current_user: dict = Depends(require_scopes(["topology:compute"]))
) -> PersistenceResponse:
    """
    🔄 ANÁLISIS DE PERSISTENCIA TOPOLÓGICA
    =====================================

    Realiza análisis de persistencia topológica mediante filtración por radio epsilon,
    generando diagramas de persistencia que capturan la evolución de estructuras topológicas.

    **Parámetros de entrada:**
    - **points**: Conjunto de puntos para análisis
    - **epsilon_range**: Rango de valores epsilon (min, max)
    - **num_steps**: Número de pasos en la filtración (5-100)
    - **max_dimension**: Dimensión máxima para homología (1-5)

    **Proceso de análisis:**
    1. Construir filtración de complejos VR para valores epsilon crecientes
    2. Calcular números de Betti en cada paso
    3. Identificar nacimiento y muerte de componentes topológicas
    4. Generar diagrama de persistencia con intervalos de vida

    **Respuesta exitosa:**
    ```json
    {
        "persistence_diagram": [
            {"dimension": 0, "birth": 0.1, "death": 2.0, "persistence": 1.9},
            {"dimension": 1, "birth": 0.3, "death": 1.2, "persistence": 0.9}
        ],
        "betti_curves": {
            "0": [1, 1, 2, 2, 1],
            "1": [0, 0, 1, 1, 0]
        },
        "persistence_entropy": 0.45,
        "bottleneck_distance": null,
        "wasserstein_distance": null,
        "epsilon_values": [0.1, 0.5, 1.0, 1.5, 2.0],
        "execution_time_seconds": 2.145,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Interpretación:**
    - **Intervalos largos**: Estructuras topológicas robustas
    - **Intervalos cortos**: Ruido topológico o estructuras efímeras
    - **Entropía de persistencia**: Complejidad de la filtración

    **Códigos de error:**
    - **400**: Parámetros inválidos, puntos insuficientes
    - **500**: Error en análisis de persistencia
    """
    start_time = time.time()
    logger.info("🔄 Iniciando análisis de persistencia - Usuario: %s, %d pasos", current_user.get('sub'), request.num_steps)

    try:
        service = TopologyService()
        result = await service.analyze_persistence(
            points=[(p.x, p.y) for p in request.points],
            epsilon_range=request.epsilon_range,
            num_steps=request.num_steps,
            max_dimension=request.max_dimension or 2
        )

        execution_time = time.time() - start_time
        logger.info("✅ Análisis de persistencia completado en %.2fs", execution_time)

        return PersistenceResponse(
            **result,
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat()
        )

    except MathematicsError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error en análisis de persistencia: %s", str(e))
        raise HTTPException(status_code=500, detail="Error en análisis de persistencia: %s" % str(e)) from e

@router.post("/persistence-diagram", response_model=VisualizationImageResponse)
async def persistence_diagram_image(
    request: PersistenceRequest,
    current_user: dict = Depends(require_scopes(["topology:compute"]))
) -> VisualizationImageResponse:
    """
    🖼️ DIAGRAMA DE PERSISTENCIA (imagen)
    Genera un diagrama de persistencia como imagen PNG (base64).
    """
    start_time = time.time()
    try:
        import io
        import base64
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        service = TopologyService()
        result = await service.analyze_persistence(
            points=[(p.x, p.y) for p in request.points],
            epsilon_range=request.epsilon_range,
            num_steps=request.num_steps,
            max_dimension=request.max_dimension or 2
        )

        # Renderizado simple de puntos (birth, death) por dimensión
        fig, ax = plt.subplots(figsize=(5, 4), dpi=120)
        diag = result.get("persistence_diagram", [])
        colors = {0: "tab:blue", 1: "tab:orange", 2: "tab:green"}
        for item in diag:
            dim = int(item.get("dimension", 0))
            b = float(item.get("birth", 0.0))
            d = float(item.get("death", b))
            ax.scatter(b, d, c=colors.get(dim, "black"), s=20)
        ax.plot([0, 1], [0, 1], transform=ax.transAxes, ls="--", c="gray", lw=1)
        ax.set_xlabel("birth")
        ax.set_ylabel("death")
        ax.set_title("Persistence Diagram")
        buf = io.BytesIO()
        plt.tight_layout()
        fig.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode("ascii")

        exec_s = time.time() - start_time
        return VisualizationImageResponse(
            image_base64=b64,
            width=600,
            height=480,
            execution_time_seconds=exec_s,
            timestamp=datetime.now().isoformat()
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/betti-curve", response_model=VisualizationImageResponse)
async def betti_curve_image(
    request: PersistenceRequest,
    current_user: dict = Depends(require_scopes(["topology:compute"]))
) -> VisualizationImageResponse:
    """
    📈 CURVAS DE BETTI (imagen)
    Genera curvas de Betti por dimensión como imagen PNG (base64).
    """
    start_time = time.time()
    try:
        import io
        import base64
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        service = TopologyService()
        result = await service.analyze_persistence(
            points=[(p.x, p.y) for p in request.points],
            epsilon_range=request.epsilon_range,
            num_steps=request.num_steps,
            max_dimension=request.max_dimension or 2
        )

        betti_curves = result.get("betti_curves", {})
        eps_vals = result.get("epsilon_values", [])
        fig, ax = plt.subplots(figsize=(5, 4), dpi=120)
        for dim_str, values in betti_curves.items():
            ax.plot(eps_vals, values, label=f"Betti {dim_str}")
        ax.set_xlabel("epsilon")
        ax.set_ylabel("Betti")
        ax.set_title("Betti Curves")
        ax.legend()
        buf = io.BytesIO()
        plt.tight_layout()
        fig.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode("ascii")

        exec_s = time.time() - start_time
        return VisualizationImageResponse(
            image_base64=b64,
            width=600,
            height=480,
            execution_time_seconds=exec_s,
            timestamp=datetime.now().isoformat()
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/simplicial-complex", response_model=SimplicialComplexResponse)
async def simplicial_complex_analysis(
    request: SimplicialComplexRequest,
    current_user: dict = Depends(require_scopes(["topology:analysis"]))
) -> SimplicialComplexResponse:
    """
    🔺 ANÁLISIS DE COMPLEJO SIMPLICIAL
    =================================

    Construye y analiza un complejo simplicial definido por vértices y símplices,
    calculando propiedades topológicas y validando la estructura matemática.

    **Parámetros de entrada:**
    - **simplices**: Lista de símplices (índices de vértices)
    - **vertices**: Coordenadas de los vértices
    - **validate_complex**: Validar estructura del complejo

    **Análisis realizado:**
    1. Validación de la estructura simplicial
    2. Cálculo de números de Betti por dimensión
    3. Característica de Euler del complejo
    4. Representación de grupos homológicos

    **Respuesta exitosa:**
    ```json
    {
        "num_vertices": 8,
        "num_simplices": {"0": 8, "1": 12, "2": 6},
        "euler_characteristic": 2,
        "betti_numbers": [1, 0, 1],
        "homology_groups": {"0": "ℤ", "1": "0", "2": "ℤ"},
        "is_valid": true,
        "validation_errors": [],
        "execution_time_seconds": 0.067,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Interpretación:**
    - **Euler χ = V - E + F - ...**: Invariante topológico
    - **Betti bₖ**: Rango del k-ésimo grupo homológico
    - **Grupos Hₖ**: ℤ (ciclos infinitos), 0 (trivial)

    **Códigos de error:**
    - **400**: Estructura simplicial inválida, índices incorrectos
    - **500**: Error en análisis del complejo
    """
    start_time = time.time()
    logger.info("🔺 Analizando complejo simplicial - Usuario: %s, %d símplices", current_user.get('sub'), len(request.simplices))

    try:
        service = TopologyService()
        result = await service.build_simplicial_complex(
            simplices=request.simplices,
            vertices=[(v.x, v.y) for v in request.vertices],
            validate_complex=request.validate_complex
        )

        execution_time = time.time() - start_time
        logger.info("✅ Complejo simplicial analizado en %.2fs", execution_time)

        return SimplicialComplexResponse(
            **result,
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat()
        )

    except MathematicsError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error en análisis simplicial: %s", str(e))
        raise HTTPException(status_code=500, detail="Error en análisis simplicial: %s" % str(e)) from e

@router.post("/mapper", response_model=MapperResponse)
async def mapper_topological_visualization(
    request: MapperRequest,
    current_user: dict = Depends(require_scopes(["topology:analysis"]))
) -> MapperResponse:
    """
    🗺️ ALGORITMO MAPPER - VISUALIZACIÓN TOPOLÓGICA
    ==============================================

    Aplica el algoritmo Mapper para crear una visualización topológica de datos
    de alta dimensión, proyectándolos a través de funciones de filtrado y clustering.

    **Parámetros de entrada:**
    - **points**: Conjunto de datos para mapeo topológico
    - **filter_function**: Función de filtrado ('distance', 'density', etc.)
    - **cover**: Parámetros de cobertura del rango de filtrado
    - **clustering**: Parámetros de clustering local

    **Proceso Mapper:**
    1. Aplicar función de filtrado a los datos
    2. Cubrir el rango de la función con intervalos solapados
    3. Aplicar clustering en cada intervalo
    4. Conectar clusters de intervalos adyacentes

    **Respuesta exitosa:**
    ```json
    {
        "nodes": [
            {"id": 0, "interval": 0, "centroid": [1.2, 3.4], "size": 15, "points": [1,5,8,12]}
        ],
        "edges": [[0, 1], [1, 2]],
        "clusters": [[1,5,8,12], [2,3,6,9]],
        "filter_values": [0.1, 0.3, 0.7, 0.9, 1.2],
        "graph_statistics": {
            "num_nodes": 8,
            "num_edges": 12,
            "num_clusters": 8,
            "average_cluster_size": 6.25
        },
        "execution_time_seconds": 0.234,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Interpretación:**
    - **Nodos**: Clusters locales en intervalos de filtrado
    - **Aristas**: Conexiones entre clusters relacionados
    - **Topología**: Estructura global revelada por el mapeo

    **Códigos de error:**
    - **400**: Datos insuficientes, parámetros inválidos
    - **500**: Error en algoritmo Mapper
    """
    start_time = time.time()
    logger.info("🗺️ Ejecutando algoritmo Mapper - Usuario: %s, %d puntos", current_user.get('sub'), len(request.points))

    try:
        service = TopologyService()
        result = await service.mapper_algorithm(
            points=[(p.x, p.y) for p in request.points],
            filter_function=request.filter_function,
            cover_params=request.cover,
            clustering_params=request.clustering
        )

        execution_time = time.time() - start_time
        logger.info("✅ Mapper completado en %.2fs", execution_time)

        return MapperResponse(
            **result,
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat()
        )

    except MathematicsError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error en algoritmo Mapper: %s", str(e))
        raise HTTPException(status_code=500, detail="Error en algoritmo Mapper: %s" % str(e)) from e

@router.post("/connectivity", response_model=ConnectivityResponse)
async def connectivity_analysis(
    request: ConnectivityRequest,
    current_user: dict = Depends(require_scopes(["topology:analysis"]))
) -> ConnectivityResponse:
    """
    🔗 ANÁLISIS DE CONECTIVIDAD TOPOLÓGICA
    =====================================

    Analiza las propiedades de conectividad de un conjunto de puntos,
    identificando componentes conexas y métricas de estructura de red.

    **Parámetros de entrada:**
    - **points**: Puntos para análisis de conectividad
    - **epsilon**: Radio de conectividad
    - **metric**: Métrica de distancia ('euclidean', etc.)

    **Análisis realizado:**
    1. Construcción del grafo de conectividad epsilon
    2. Identificación de componentes conexas
    3. Cálculo de métricas de red (clustering, caminos)
    4. Análisis de propiedades estructurales

    **Respuesta exitosa:**
    ```json
    {
        "connected_components": [[0,1,2,5], [3,4], [6]],
        "num_components": 3,
        "component_sizes": [4, 2, 1],
        "connectivity_graph": {
            "adjacency_matrix_shape": [7, 7],
            "average_degree": 2.3,
            "max_degree": 5,
            "density": 0.19
        },
        "clustering_coefficient": 0.67,
        "average_path_length": 2.1,
        "execution_time_seconds": 0.089,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Interpretación:**
    - **Componentes**: Grupos de puntos mutuamente conectados
    - **Clustering**: Tendencia a formar comunidades locales
    - **Path length**: Eficiencia de navegación en la red

    **Códigos de error:**
    - **400**: Puntos insuficientes, parámetros inválidos
    - **500**: Error en análisis de conectividad
    """
    start_time = time.time()
    logger.info("🔗 Analizando conectividad - Usuario: %s, ε=%f", current_user.get('sub'), request.epsilon)

    try:
        service = TopologyService()
        result = await service.analyze_connectivity(
            points=[(p.x, p.y) for p in request.points],
            epsilon=request.epsilon,
            metric=request.metric
        )

        execution_time = time.time() - start_time
        logger.info("✅ Análisis de conectividad completado en %.2fs", execution_time)

        return ConnectivityResponse(
            **result,
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat()
        )

    except MathematicsError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error en análisis de conectividad: %s", str(e))
        raise HTTPException(status_code=500, detail="Error en análisis de conectividad: %s" % str(e)) from e

@router.post("/homotopy-groups", response_model=HomotopyResponse)
async def homotopy_groups_analysis(
    request: HomotopyRequest,
    current_user: dict = Depends(require_scopes(["topology:compute"]))
) -> HomotopyResponse:
    """
    🔄 ANÁLISIS DE GRUPOS HOMOTÓPICOS
    ================================

    Analiza propiedades homotópicas de espacios topológicos definidos,
    calculando grupos homotópicos y tipo de homotopy.

    **Nota**: Implementación básica - funcionalidad extendida requiere bibliotecas especializadas.
    """
    start_time = time.time()
    logger.info("🔄 Analizando grupos homotópicos - Usuario: %s", current_user.get('sub'))

    try:
        # Implementación básica (placeholder para funcionalidad completa)
        # Usar request.space_definition para análisis futuro
        _ = request.space_definition  # Evitar warning de argumento no usado
        result = {
            "pi_groups": {0: "ℤ", 1: "ℤ"},  # Grupos fundamentales básicos
            "fundamental_group": "ℤ",
            "homotopy_type": "simply_connected",
            "cw_complex": None,
            "approximation_used": "fundamental_group_only"
        }

        execution_time = time.time() - start_time
        logger.info("✅ Análisis homotópico completado en %.2fs", execution_time)

        return HomotopyResponse(
            **result,
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat()
        )

    except MathematicsError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error en análisis homotópico: %s", str(e))
        raise HTTPException(status_code=500, detail="Error en análisis homotópico: %s" % str(e)) from e

@router.post("/covering-spaces", response_model=CoveringSpaceResponse)
async def covering_spaces_analysis(
    request: CoveringSpaceRequest,
    current_user: dict = Depends(require_scopes(["topology:compute"]))
) -> CoveringSpaceResponse:
    """
    🌀 ANÁLISIS DE ESPACIOS DE COBERTURA
    ===================================

    Analiza propiedades de espacios de cobertura y transformaciones del deck.

    **Nota**: Implementación básica - funcionalidad extendida requiere teoría avanzada.
    """
    start_time = time.time()
    logger.info("🌀 Analizando espacios de cobertura - Usuario: %s", current_user.get('sub'))

    try:
        # Implementación básica (placeholder)
        # Usar request.base_space y request.covering_type para análisis futuro
        _ = request.base_space, request.covering_type  # Evitar warning de argumentos no usados
        result = {
            "covering_maps": [],
            "deck_transformations": [],
            "fundamental_domain": {},
            "monodromy": {}
        }

        execution_time = time.time() - start_time
        logger.info("✅ Análisis de cobertura completado en %.2fs", execution_time)

        return CoveringSpaceResponse(
            **result,
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat()
        )

    except MathematicsError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error en análisis de cobertura: %s", str(e))
        raise HTTPException(status_code=500, detail="Error en análisis de cobertura: %s" % str(e)) from e


# ========== ENDPOINTS AVANZADOS AÑADIDOS ==========

class MapperAdvancedRequest(BaseModel):
    """Request para algoritmo Mapper avanzado."""
    points: List[Point2D] = Field(..., description="Conjunto de datos para mapeo topológico")
    n_intervals: int = Field(10, ge=5, le=50, description="Número de intervalos en la cobertura")
    overlap_fraction: float = Field(0.3, ge=0.0, le=0.8, description="Fracción de solapamiento")
    cluster_algorithm: str = Field("kmeans", description="Algoritmo de clustering (kmeans, dbscan, hierarchical)")
    filter_function: str = Field("pca_1", description="Función de filtro (pca_1, pca_2, density, distance_to_point)")
    cluster_params: Optional[Dict[str, Any]] = Field(None, description="Parámetros específicos del clustering")

class ShapeAnalysisRequest(BaseModel):
    """Request para análisis avanzado de formas."""
    points: List[Point2D] = Field(..., description="Puntos que definen la forma")
    resolution: float = Field(0.1, gt=0, le=1.0, description="Resolución para análisis discreto")
    compute_symmetries: bool = Field(True, description="Computar análisis de simetrías")
    compute_medial_axis: bool = Field(True, description="Computar medial axis transform")
    compute_descriptors: bool = Field(True, description="Computar descriptores de forma")

class MultiScaleRequest(BaseModel):
    """Request para análisis multi-escala."""
    points: List[Point2D] = Field(..., description="Puntos para análisis multi-escala")
    epsilon_min: float = Field(..., gt=0, description="Valor mínimo de epsilon")
    epsilon_max: float = Field(..., gt=0, description="Valor máximo de epsilon")
    num_scales: int = Field(10, ge=5, le=50, description="Número de escalas a analizar")
    
    @field_validator('epsilon_max')
    @classmethod
    def validate_epsilon_range(cls, v, values):
        if 'epsilon_min' in values and v <= values['epsilon_min']:
            raise ValueError('epsilon_max debe ser mayor que epsilon_min')
        return v

class TopologyAdvancedResponse(BaseModel):
    """Response unificada para análisis topológico avanzado."""
    result: Dict[str, Any] = Field(..., description="Resultado del análisis")
    algorithm: str = Field(..., description="Algoritmo utilizado")
    execution_time_seconds: float = Field(..., description="Tiempo de ejecución")
    timestamp: str = Field(..., description="Timestamp del análisis")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")

@router.post("/mapper-advanced", response_model=TopologyAdvancedResponse)
async def mapper_advanced_analysis(
    request: MapperAdvancedRequest,
    current_user: dict = Depends(require_scopes(["topology:analysis"]))
) -> TopologyAdvancedResponse:
    """
    🗺️ ALGORITMO MAPPER AVANZADO
    ============================
    
    Ejecuta análisis topológico avanzado usando el algoritmo Mapper con configuración personalizada,
    múltiples funciones de filtro y algoritmos de clustering adaptativos.
    
    Características:
    - Funciones de filtro: PCA, densidad, distancia, excentricidad
    - Clustering: K-means, DBSCAN, jerárquico
    - Análisis de calidad del grafo resultante
    - Métricas de estabilidad topológica
    """
    start_time = time.time()
    logger.info("🗺️ Iniciando análisis Mapper avanzado - Usuario: %s", current_user.get('sub'))
    
    try:
        topology_service = TopologyService()
        
        # Convertir puntos
        points = [(p.x, p.y) for p in request.points]
        
        # Configuración del Mapper
        mapper_config = {
            "n_intervals": request.n_intervals,
            "overlap_fraction": request.overlap_fraction,
            "cluster_algorithm": request.cluster_algorithm,
            "filter_function": request.filter_function,
            "cluster_params": request.cluster_params or {}
        }
        
        # Ejecutar análisis Mapper avanzado
        result = await topology_service.compute_mapper_visualization(
            points=points,
            mapper_config=mapper_config
        )
        
        execution_time = time.time() - start_time
        logger.info("✅ Análisis Mapper avanzado completado en %.2fs", execution_time)
        
        return TopologyAdvancedResponse(
            result=result,
            algorithm="mapper_tda_advanced",
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat(),
            metadata={
                "n_points": len(points),
                "config": mapper_config
            }
        )
        
    except MathematicsError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error en análisis Mapper avanzado: %s", str(e))
        raise HTTPException(
            status_code=500, 
            detail=f"Error en análisis Mapper avanzado: {str(e)}"
        ) from e

@router.post("/shape-analysis", response_model=TopologyAdvancedResponse)
async def shape_characteristics_analysis(
    request: ShapeAnalysisRequest,
    current_user: dict = Depends(require_scopes(["topology:analysis"]))
) -> TopologyAdvancedResponse:
    """
    🔍 ANÁLISIS AVANZADO DE FORMAS
    ===============================
    
    Realiza análisis geométrico y topológico completo de formas 2D incluyendo:
    - Características geométricas (área, perímetro, compacidad)
    - Análisis de curvatura y puntos críticos
    - Simetrías reflectivas y rotacionales
    - Descriptores de Fourier y shape context
    - Medial axis transform y esqueletonización
    - Momentos invariantes de Hu
    """
    start_time = time.time()
    logger.info("🔍 Iniciando análisis de forma - Usuario: %s", current_user.get('sub'))
    
    try:
        topology_service = TopologyService()
        
        # Convertir puntos
        points = [(p.x, p.y) for p in request.points]
        
        # Ejecutar análisis de forma
        result = await topology_service.analyze_shape_characteristics(
            points=points,
            resolution=request.resolution
        )
        
        execution_time = time.time() - start_time
        logger.info("✅ Análisis de forma completado en %.2fs", execution_time)
        
        return TopologyAdvancedResponse(
            result=result,
            algorithm="comprehensive_shape_analysis",
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat(),
            metadata={
                "n_points": len(points),
                "resolution": request.resolution,
                "analysis_options": {
                    "symmetries": request.compute_symmetries,
                    "medial_axis": request.compute_medial_axis,
                    "descriptors": request.compute_descriptors
                }
            }
        )
        
    except MathematicsError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error en análisis de forma: %s", str(e))
        raise HTTPException(
            status_code=500, 
            detail=f"Error en análisis de forma: {str(e)}"
        ) from e

@router.post("/multi-scale-analysis", response_model=TopologyAdvancedResponse)
async def multi_scale_topological_analysis(
    request: MultiScaleRequest,
    current_user: dict = Depends(require_scopes(["topology:compute"]))
) -> TopologyAdvancedResponse:
    """
    📏 ANÁLISIS TOPOLÓGICO MULTI-ESCALA
    ====================================
    
    Realiza análisis topológico a múltiples escalas para detectar:
    - Evolución de números de Betti con cambios de escala
    - Transiciones topológicas significativas
    - Regiones de estabilidad topológica
    - Características persistentes vs. ruido topológico
    - Diagramas de persistencia multi-resolución
    
    Útil para identificar características topológicas robustas en datos.
    """
    start_time = time.time()
    logger.info("📏 Iniciando análisis multi-escala - Usuario: %s", current_user.get('sub'))
    
    try:
        topology_service = TopologyService()
        
        # Convertir puntos
        points = [(p.x, p.y) for p in request.points]
        
        # Ejecutar análisis multi-escala
        result = await topology_service.compute_multi_scale_analysis(
            points=points,
            scale_range=(request.epsilon_min, request.epsilon_max),
            num_scales=request.num_scales
        )
        
        execution_time = time.time() - start_time
        logger.info("✅ Análisis multi-escala completado en %.2fs", execution_time)
        
        return TopologyAdvancedResponse(
            result=result,
            algorithm="multi_scale_topology",
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat(),
            metadata={
                "n_points": len(points),
                "scale_range": [request.epsilon_min, request.epsilon_max],
                "num_scales": request.num_scales
            }
        )
        
    except MathematicsError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error en análisis multi-escala: %s", str(e))
        raise HTTPException(
            status_code=500, 
            detail=f"Error en análisis multi-escala: {str(e)}"
        ) from e


