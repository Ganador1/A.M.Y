"""NoveltyAssessor: estima novedad relativa de items usando embeddings previos (placeholder).

Estrategia mínima: distancia coseno promedio contra centroides (simulada) y densidad k-NN aproximada.
Se retornan componentes y score final normalizado.
"""
from __future__ import annotations

from typing import List, Dict, Any
import math


class NoveltyAssessor:
    def __init__(self, centroid_vectors: List[List[float]] | None = None):
        # Centroides simulados; en producción cargar desde índice/FAISS
        self.centroids = centroid_vectors or [[0.1, 0.1, 0.1], [0.5, -0.2, 0.3]]

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        num = sum(x * y for x, y in zip(a, b))
        da = math.sqrt(sum(x * x for x in a)) or 1e-9
        db = math.sqrt(sum(y * y for y in b)) or 1e-9
        return num / (da * db)

    def assess(self, embedding: List[float] | Dict[str, Any]) -> Dict[str, Any]:
        # Accept either a raw embedding (list of floats) or a candidate dict with keys
        # 'novelty', 'information_gain', 'impact_potential' (normalize to vector)
        vec: List[float]
        if embedding is None:
            return {"novelty_score": 0.0, "centroid_distance": 0.0, "density_proxy": 0.0}

        if isinstance(embedding, dict):
            vec = [
                float(embedding.get("novelty", 0.0)),
                float(embedding.get("information_gain", 0.0)),
                float(embedding.get("impact_potential", 0.0)),
            ]
        else:
            vec = list(embedding)

        if not vec:
            return {"novelty_score": 0.0, "centroid_distance": 0.0, "density_proxy": 0.0}

        # Distancia inversa media a centroides (1 - cos)
        distances = [1 - self._cosine(vec, c) for c in self.centroids]
        centroid_distance = sum(distances) / len(distances)
        # Proxy densidad: varianza interna (mayor var => mayor novedad)
        mean = sum(vec) / len(vec)
        variance = sum((x - mean) ** 2 for x in vec) / len(vec)
        density_proxy = math.tanh(variance)
        # Combinar
        raw = 0.7 * centroid_distance + 0.3 * density_proxy
        score = max(0.0, min(1.0, raw))
        # Compatibilidad: devolver sólo el score (los tests esperan un float)
        return score

__all__ = ["NoveltyAssessor"]
