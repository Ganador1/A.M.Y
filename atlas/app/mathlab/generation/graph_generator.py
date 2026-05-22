from __future__ import annotations

from typing import Dict, Any, List
import random
import networkx as nx
import pynauty

from app.mathlab.core.object_registry import REGISTRY


def er_graph(n: int, p: float, directed: bool = False) -> Dict[str, Any]:
    """Genera un grafo Erdős–Rényi G(n,p) y devuelve payload JSON normalizado."""
    G = nx.DiGraph() if directed else nx.Graph()
    G.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < p:
                if directed:
                    G.add_edge(i, j)
                else:
                    G.add_edge(i, j)
    nodes = list(G.nodes())
    edges = [[u, v] for u, v in G.edges()]
    return {"type": "graph", "directed": directed, "nodes": nodes, "edges": edges}


def register_er_graph(n: int, p: float, directed: bool = False) -> str:
    payload = er_graph(n, p, directed)
    obj = REGISTRY.register("graph", {k: v for k, v in payload.items() if k != "type"})
    return obj.id


def enumerate_non_isomorphic_graphs(n: int, directed: bool = False) -> List[Dict[str, Any]]:
    """
    Enumera todos los grafos no isomorfos de n nodos usando pynauty.
    
    Args:
        n: Número de nodos (n ≤ 5 recomendado por complejidad exponencial O(2^(n*(n-1)/2)))
        directed: Si los grafos deben ser dirigidos
        
    Returns:
        Lista de payloads JSON de grafos no isomorfos
    """
    if n > 5:
        raise ValueError("La enumeración completa es computacionalmente costosa para n > 5 (se recomienda n <= 5 para evitar parálisis del sistema)")
    
    # Usar pynauty para generar grafos no isomorfos
    graphs = []
    
    # Para grafos no dirigidos
    if not directed:
        # Generar todos los grafos de n nodos y filtrar isomorfismos
        from itertools import combinations, product
        
        # Todos los posibles conjuntos de aristas
        possible_edges = list(combinations(range(n), 2))
        num_possible_edges = len(possible_edges)
        
        # Generar todos los grafos posibles (2^(num_possible_edges))
        for edge_mask in product([0, 1], repeat=num_possible_edges):
            # Crear el grafo con las aristas seleccionadas
            edges = []
            for i, has_edge in enumerate(edge_mask):
                if has_edge:
                    edges.append(list(possible_edges[i]))
            
            # Crear payload del grafo
            payload = {
                "type": "graph",
                "directed": False,
                "nodes": list(range(n)),
                "edges": edges
            }
            graphs.append(payload)
    else:
        # Para grafos dirigidos (implementación más compleja)
        from itertools import product
        
        # Todos los posibles pares ordenados (excluyendo loops)
        possible_edges = [(i, j) for i in range(n) for j in range(n) if i != j]
        num_possible_edges = len(possible_edges)
        
        # Generar todos los grafos dirigidos posibles
        for edge_mask in product([0, 1], repeat=num_possible_edges):
            edges = []
            for i, has_edge in enumerate(edge_mask):
                if has_edge:
                    edges.append(list(possible_edges[i]))
            
            payload = {
                "type": "graph", 
                "directed": True,
                "nodes": list(range(n)),
                "edges": edges
            }
            graphs.append(payload)
    
    # Filtrar isomorfismos usando pynauty
    unique_graphs = _filter_isomorphic_graphs(graphs)
    
    return unique_graphs


def _filter_isomorphic_graphs(graphs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filtra grafos isomorfos usando pynauty."""
    unique_canonical_forms = {}
    unique_graphs = []
    
    for graph_payload in graphs:
        # Convertir a formato pynauty
        n = len(graph_payload["nodes"])
        directed = graph_payload["directed"]
        
        # Crear grafo pynauty
        adj_dict = {i: [] for i in range(n)}
        for u, v in graph_payload["edges"]:
            adj_dict[u].append(v)
            if not directed:
                adj_dict[v].append(u)
        
        # Convertir a lista de adyacencia para pynauty
        adjacency = [adj_dict[i] for i in range(n)]
        
        # Crear objeto pynauty
        g = pynauty.Graph(n, directed=directed)
        for i in range(n):
            g.connect_vertex(i, adjacency[i])
        
        # Obtener forma canónica
        canonical_form = pynauty.certificate(g)
        
        # Mantener solo un representante por clase de isomorfismo
        if canonical_form not in unique_canonical_forms:
            unique_canonical_forms[canonical_form] = graph_payload
            unique_graphs.append(graph_payload)
    
    return unique_graphs


def register_non_isomorphic_graphs(n: int, directed: bool = False) -> List[str]:
    """
    Enumera y registra todos los grafos no isomorfos de n nodos.
    
    Returns:
        Lista de IDs de objetos registrados
    """
    graphs = enumerate_non_isomorphic_graphs(n, directed)
    object_ids = []
    
    for graph_payload in graphs:
        obj = REGISTRY.register("graph", {
            "directed": graph_payload["directed"],
            "nodes": graph_payload["nodes"],
            "edges": graph_payload["edges"]
        })
        object_ids.append(obj.id)
    
    return object_ids