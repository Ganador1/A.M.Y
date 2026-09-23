from __future__ import annotations

import networkx as nx
import numpy as np
from typing import Dict, Any, List, Tuple

from app.mathlab.core.object_models import MathematicalObject
from app.mathlab.core.object_registry import REGISTRY
from app.mathlab.generation.graph_generator import enumerate_non_isomorphic_graphs
from app.mathlab.invariants.graph_invariants import GraphInvariants


def test_graph_invariants():
    """Test para verificar el cálculo de invariantes avanzados en grafos."""
    # Crear un grafo completo K4
    G = nx.complete_graph(4)
    edges = [[u, v] for u, v in G.edges()]
    payload = {"type": "graph", "directed": False, "nodes": list(range(4)), "edges": edges}
    
    # Registrar el grafo
    obj = REGISTRY.register("graph", {k: v for k, v in payload.items() if k != "type"})
    
    # Calcular invariantes
    invariants = GraphInvariants().compute(obj)
    
    print("Invariants:", invariants)
    
    # Verificar invariantes básicos
    assert invariants["n"] == 4
    assert invariants["m"] == 6
    assert invariants["density"] == 1.0
    assert invariants["is_connected"] == True
    
    # Verificar invariantes avanzados
    assert invariants["chromatic_number_approx"] == 4
    assert invariants["clique_number_approx"] == 4
    assert invariants["independence_number_approx"] == 1
    assert invariants["diameter"] == 1
    assert invariants["radius"] == 1
    
    print("✅ Test de invariantes de grafos completado con éxito")


def test_non_isomorphic_enumeration():
    """Test para verificar la enumeración no isomorfa de grafos."""
    # Enumerar todos los grafos no isomorfos con 3 nodos
    graphs = enumerate_non_isomorphic_graphs(3)
    
    # Deberían haber exactamente 4 grafos no isomorfos con 3 nodos:
    # 1. Grafo vacío (sin aristas)
    # 2. Grafo con una arista
    # 3. Grafo con dos aristas (camino)
    # 4. Grafo completo K3 (triángulo)
    assert len(graphs) == 4
    
    # Verificar que tenemos el número correcto de aristas en cada caso
    edge_counts = sorted([len(g["edges"]) for g in graphs])
    assert edge_counts == [0, 1, 2, 3]
    
    print(f"✅ Enumeración no isomorfa generó {len(graphs)} grafos con 3 nodos")


if __name__ == "__main__":
    test_graph_invariants()
    test_non_isomorphic_enumeration()
    print("✅ Todos los tests completados con éxito")