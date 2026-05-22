from __future__ import annotations

from typing import List, Dict, Any, Tuple
import numpy as np


class VietorisRipsBuilder:
    """Constructor mínimo de complejo de Vietoris–Rips en 2D.

    Retorna invariantes básicos aproximados:
    - n_points
    - components_est (H0 aproximado via umbral de conectividad)
    - cycles_est (H1 aproximado via Euler characteristic sobre grafo de vecindad)
    """

    def __init__(self, epsilon: float = 0.2):
        self.epsilon = float(epsilon)

    def build(self, points: List[Tuple[float, float]]) -> Dict[str, Any]:
        if not points or len(points) < 2:
            return {"n_points": len(points or []), "components_est": len(points or []), "cycles_est": 0}
        P = np.array(points, dtype=float)
        n = P.shape[0]
        # matriz de adyacencia por radio
        D = np.sqrt(((P[:, None, :] - P[None, :, :]) ** 2).sum(axis=2))
        adj = (D <= self.epsilon).astype(int)
        np.fill_diagonal(adj, 0)

        # componentes por DFS
        visited = np.zeros(n, dtype=bool)
        comp = 0
        for i in range(n):
            if not visited[i]:
                comp += 1
                stack = [i]
                visited[i] = True
                while stack:
                    u = stack.pop()
                    for v in range(n):
                        if adj[u, v] and not visited[v]:
                            visited[v] = True
                            stack.append(v)

        # Euler characteristic χ ≈ V - E para grafo; H1 ≈ E - V + C (heurística)
        V = n
        E = int(adj.sum() // 2)
        cycles_est = max(0, E - V + comp)

        return {"n_points": n, "components_est": int(comp), "edges": E, "cycles_est": int(cycles_est)}


__all__ = ["VietorisRipsBuilder"]


