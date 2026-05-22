from __future__ import annotations

from typing import List, Dict, Any, Tuple
import numpy as np


def epsilon_graph_invariants(points: List[Tuple[float, float]], epsilon: float = 0.2) -> Dict[str, Any]:
    if not points:
        return {"n_points": 0, "avg_degree": 0.0, "density": 0.0, "clustering_coeff": 0.0, "diameter_est": 0}
    P = np.array(points, dtype=float)
    n = P.shape[0]
    if n == 1:
        return {"n_points": 1, "avg_degree": 0.0, "density": 0.0, "clustering_coeff": 0.0, "diameter_est": 0}
    D = np.sqrt(((P[:, None, :] - P[None, :, :]) ** 2).sum(axis=2))
    adj = (D <= epsilon).astype(int)
    np.fill_diagonal(adj, 0)
    E = int(adj.sum() // 2)
    deg = adj.sum(axis=1)
    avg_deg = float(deg.mean())
    density = (2 * E) / (n * (n - 1)) if n > 1 else 0.0

    # clustering coefficient (triangles over triples) aproximado
    # C_i = 2T_i / (k_i (k_i - 1)), T_i ~ (A^3)_{ii} / 2
    try:
        A = adj
        A3 = A @ A @ A
        triangles = np.diag(A3) / 2.0
        denom = deg * (deg - 1)
        with np.errstate(invalid='ignore', divide='ignore'):
            Ci = np.where(denom > 0, (2 * triangles) / denom, 0.0)
        clustering = float(np.nan_to_num(Ci).mean())
    except Exception:
        clustering = 0.0

    # diámetro estimado via BFS sobre grafo no dirigido (sampleado si n grande)
    def bfs_far(i: int) -> int:
        from collections import deque
        vis = np.zeros(n, dtype=bool)
        dist = np.full(n, -1, dtype=int)
        q = deque([i])
        vis[i] = True
        dist[i] = 0
        while q:
            u = q.popleft()
            for v in np.where(adj[u] == 1)[0]:
                if not vis[v]:
                    vis[v] = True
                    dist[v] = dist[u] + 1
                    q.append(v)
        return int(dist.max())

    sample_idx = list(range(min(n, 20)))  # limitar coste
    diam_est = max(bfs_far(i) for i in sample_idx) if n > 1 else 0

    return {
        "n_points": int(n),
        "edges": int(E),
        "avg_degree": float(avg_deg),
        "density": float(density),
        "clustering_coeff": float(clustering),
        "diameter_est": int(diam_est),
    }


__all__ = ["epsilon_graph_invariants"]


