from __future__ import annotations

from typing import Dict, Any
import numpy as np
import networkx as nx

from app.mathlab.core.object_models import MathematicalObject


def laplacian_spectrum_embedding(obj: MathematicalObject, k: int = 16) -> Dict[str, Any]:
    """Embedding basado en el espectro del Laplaciano normalizado (top-k eigenvalores).
    - Si el grafo es dirigido, se usa su versión no dirigida para el cálculo.
    - Si n < k, se rellena con ceros hasta longitud k.
    """
    payload = obj.payload_json
    directed = bool(payload.get("directed", False))
    G = nx.DiGraph() if directed else nx.Graph()
    nodes = payload.get("nodes")
    if nodes is not None:
        G.add_nodes_from(nodes)
    for u, v in payload.get("edges", []):
        G.add_edge(u, v)

    if directed:
        G = G.to_undirected()

    n = G.number_of_nodes()
    if n == 0:
        vec = [0.0] * k
        return {
            "embedding_type": "graph/laplacian_spectrum",
            "vector": vec,
            "dim": k,
            "metadata": {"n": 0, "k": k, "directed_input": True if directed else False},
        }

    try:
        L = nx.normalized_laplacian_matrix(G).toarray()
        eigvals = np.linalg.eigvalsh(L)
        eigvals_sorted = np.sort(eigvals)
        m = min(k, len(eigvals_sorted))
        vec = eigvals_sorted[:m].astype(float).tolist()
        if m < k:
            vec = vec + [0.0] * (k - m)
    except Exception:
        # En caso de error numérico, devolver vector nulo
        vec = [0.0] * k

    return {
        "embedding_type": "graph/laplacian_spectrum",
        "vector": vec,
        "dim": k,
        "metadata": {"n": n, "k": k, "directed_input": True if directed else False},
    }


def degree_histogram_embedding(obj: MathematicalObject, max_degree: int = 50) -> Dict[str, Any]:
    """Embedding basado en histograma de grados, normalizado."""
    payload = obj.payload_json
    directed = bool(payload.get("directed", False))
    G = nx.DiGraph() if directed else nx.Graph()
    nodes = payload.get("nodes")
    if nodes is not None:
        G.add_nodes_from(nodes)
    for u, v in payload.get("edges", []):
        G.add_edge(u, v)

    degrees = [d for _, d in G.degree()]
    if not degrees:
        vec = [0.0] * (max_degree + 1)
    else:
        hist, _ = np.histogram(degrees, bins=range(max_degree + 2), density=True)
        vec = hist.tolist()

    return {
        "embedding_type": "graph/degree_histogram",
        "vector": vec,
        "dim": len(vec),
        "metadata": {"max_degree": max_degree, "directed": directed},
    }