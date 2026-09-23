from __future__ import annotations

from typing import Dict, Any
import numpy as np
import networkx as nx
import networkx.algorithms.approximation as approx
import networkx.algorithms.coloring as coloring
# Removed unused import: import networkx.algorithms.clique as clique

from app.mathlab.core.invariants_interface import InvariantsComputer
from app.mathlab.core.object_models import MathematicalObject


class GraphInvariants(InvariantsComputer):
    """Invariantes básicos y avanzados para grafos usando NetworkX."""

    def compute(self, obj: MathematicalObject) -> Dict[str, Any]:
        payload = obj.payload_json
        # Esperamos formato: { "nodes": [id...], "edges": [[u,v], ...], "directed": bool }
        directed = bool(payload.get("directed", False))
        G = nx.DiGraph() if directed else nx.Graph()
        nodes = payload.get("nodes")
        if nodes is None:
            # Permitir implícito por edges
            pass
        else:
            G.add_nodes_from(nodes)
        for u, v in payload.get("edges", []):
            G.add_edge(u, v)

        inv: Dict[str, Any] = {}
        inv["n"] = G.number_of_nodes()
        inv["m"] = G.number_of_edges()
        inv["density"] = nx.density(G)

        # Conectividad y componentes
        if not directed:
            inv["is_connected"] = bool(nx.is_connected(G)) if G.number_of_nodes() > 0 else False
            inv["components"] = int(nx.number_connected_components(G)) if G.number_of_nodes() > 0 else 0
            try:
                inv["avg_clustering"] = float(nx.average_clustering(G)) if G.number_of_nodes() > 1 else 0.0
            except Exception:
                inv["avg_clustering"] = None
        else:
            inv["is_weakly_connected"] = bool(nx.is_weakly_connected(G)) if G.number_of_nodes() > 0 else False
            inv["is_strongly_connected"] = bool(nx.is_strongly_connected(G)) if G.number_of_nodes() > 0 else False

        # Espectro Laplaciano (no dirigido)
        if not directed and G.number_of_nodes() > 0:
            try:
                L = nx.normalized_laplacian_matrix(G).toarray()
                eigvals = np.linalg.eigvalsh(L)
                k = min(10, len(eigvals))
                topk = np.sort(eigvals)[:k].tolist()
                inv["laplacian_spectrum_topk"] = topk
            except Exception:
                inv["laplacian_spectrum_topk"] = None

        # Stats de grados
        degrees = [d for _, d in G.degree()]
        if degrees:
            inv["deg_mean"] = float(np.mean(degrees))
            inv["deg_var"] = float(np.var(degrees))
        else:
            inv["deg_mean"] = 0.0
            inv["deg_var"] = 0.0

        # Invariantes avanzados (solo para no dirigidos, por simplicidad)
        if not directed and G.number_of_nodes() > 0:
            # Número cromático (aproximación, ya que exacto es NP-hard)
            try:
                graph_coloring = coloring.greedy_color(G)
                inv["chromatic_number_approx"] = max(graph_coloring.values()) + 1 if graph_coloring else 0
            except Exception as e:
                print(f"Error in chromatic approx: {str(e)}")
                inv["chromatic_number_approx"] = None
            
            # Número de clique máximo (aproximación)
            try:
                inv["clique_number_approx"] = len(approx.clique.max_clique(G))
            except Exception as e:
                print(f"Error in clique approx: {str(e)}")
                inv["clique_number_approx"] = None
            
            # Número de independencia máximo (aproximación)
            try:
                inv["independence_number_approx"] = len(approx.maximum_independent_set(G))
            except Exception:
                inv["independence_number_approx"] = None
            
            # Diámetro
            try:
                inv["diameter"] = nx.diameter(G) if nx.is_connected(G) else None
            except Exception:
                inv["diameter"] = None
            
            # Radio
            try:
                inv["radius"] = nx.radius(G) if nx.is_connected(G) else None
            except Exception:
                inv["radius"] = None

        return inv