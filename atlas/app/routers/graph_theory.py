
"""
Router de Teoría de Grafos - Algoritmos y Análisis de Redes Complejas

Módulo FastAPI para algoritmos integrales de teoría de grafos y análisis de redes.
Proporciona endpoints REST API para algoritmos de grafos, problemas de flujo de red,
detección de comunidades y visualización de grafos para análisis de redes complejas.

Capacidades principales:
- Búsqueda de caminos: caminos más cortos, árboles de expansión mínima, todos los pares de caminos más cortos
- Flujos de red: flujo máximo, corte mínimo, redes de flujo
- Detección de comunidades: algoritmos de clustering, optimización de modularidad
- Medidas de centralidad: grado, intermediación, cercanía, centralidad de eigenvector
- Recorrido de grafos: BFS, DFS, ordenamiento topológico
- Análisis de redes: conectividad, componentes, ciclos
- Visualización de grafos: gráficos interactivos, layouts de red

Catálogo de Endpoints:
- POST /shortest-path: Algoritmos de camino más corto Dijkstra/Bellman-Ford
- POST /maximum-flow: Cálculo de flujo máximo Ford-Fulkerson
- POST /community-detection: Detección de comunidades basada en Louvain/modularidad
- POST /centrality: Medidas de centralidad de nodos y ranking de importancia
- POST /visualize: Visualización interactiva de grafos y renderizado

Dependencias:
- GraphTheoryService: Algoritmos centrales de grafos y análisis de redes
- NetworkX: Biblioteca integral de grafos para Python
- NumPy/SciPy: Computaciones numéricas para grafos grandes
- Matplotlib/Plotly: Visualización de grafos y gráficos interactivos
- GraphTheoryRequest: Modelos estandarizados de problemas de grafos

Uso del Servicio:
    Todos los endpoints aceptan estructuras de grafos definidas por nodos y aristas.
    Las aristas pueden incluir pesos/capacidades para algoritmos ponderados.
    Los endpoints de visualización generan gráficos interactivos para análisis.
    Soporta tanto grafos dirigidos como no dirigidos para diferentes aplicaciones.
"""

from fastapi import APIRouter
from app.models.models import GraphTheoryRequest
from app.services.graph_theory import (
    find_shortest_path,
    calculate_maximum_flow,
    detect_communities,
    calculate_centrality,
    visualize_graph
)

router = APIRouter()

@router.post("/shortest-path")
def post_shortest_path(request: GraphTheoryRequest):
    """
    Find the shortest path between two nodes in a graph.
    """
    if not request.source or not request.target:
        return {"error": "Source and target nodes are required for shortest path calculation."}
    
    path = find_shortest_path(request.nodes, request.edges, request.source, request.target)
    return {"shortest_path": path}

@router.post("/maximum-flow")
def post_maximum_flow(request: GraphTheoryRequest):
    """
    Calculate the maximum flow between two nodes in a graph.
    """
    if not request.source or not request.target:
        return {"error": "Source and target nodes are required for maximum flow calculation."}
    
    # Edges for maximum flow should have capacity, e.g., [("A", "B", 10)]
    edges_with_capacity = [(u, v, 1) for u, v in request.edges]  # Default capacity to 1 if not provided
    
    return calculate_maximum_flow(request.nodes, edges_with_capacity, request.source, request.target)

@router.post("/community-detection")
def post_community_detection(request: GraphTheoryRequest):
    """
    Detect communities in a graph.
    """
    communities = detect_communities(request.nodes, request.edges)
    return {"communities": communities}

@router.post("/centrality")
def post_centrality(request: GraphTheoryRequest):
    """
    Calculate the degree centrality for each node in a graph.
    """
    centrality = calculate_centrality(request.nodes, request.edges)
    return {"centrality": centrality}

@router.post("/visualize")
def post_visualize_graph(request: GraphTheoryRequest):
    """
    Generate an interactive visualization of the graph.
    """
    file_path = visualize_graph(request.nodes, request.edges, request.operation, request.source, request.target)
    return {"visualization_path": file_path}
