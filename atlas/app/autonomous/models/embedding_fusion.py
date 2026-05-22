"""Embedding fusion module (placeholder).

Implements late fusion attention-like weighting across multiple embedding vectors.
Input: dict mapping modality name -> list[float]. Output: fused list[float].
This simplified version normalizes each vector and computes a weighted sum using a
softmax over tanh(W e_i) · v where W and v are random-initialized (deterministic seed optional).
"""
from __future__ import annotations

from typing import Dict, List
import math
import random
from app.core.bootstrap_logging import logger


class EmbeddingFusion:
    def __init__(self, dim: int | None = None, seed: int | None = 42):
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        self.dim = dim  # optional expected dimension
        # Random projection params
        self._w = [random.uniform(-0.1, 0.1) for _ in range(dim or 32)]
        self._v = [random.uniform(-0.1, 0.1) for _ in range(dim or 32)]

    def fuse(self, embeddings: Dict[str, List[float]]) -> List[float]:
        if not embeddings:
            return []
        scored_vectors: list[tuple[float, list[float]]] = []
        for _, vec in embeddings.items():
            if not vec:
                continue
            norm = math.sqrt(sum(x * x for x in vec)) or 1.0
            normed = [x / norm for x in vec]
            target_dim = len(self._w)
            if len(normed) < target_dim:
                normed.extend([0.0] * (target_dim - len(normed)))
            elif len(normed) > target_dim:
                normed = normed[:target_dim]
            activated = [math.tanh(w * x) for w, x in zip(self._w, normed)]
            score = sum(v * a for v, a in zip(self._v, activated))
            scored_vectors.append((score, normed))
        if not scored_vectors:
            return []
        max_score = max(s for s, _ in scored_vectors)
        exps = [math.exp(s - max_score) for s, _ in scored_vectors]
        denom = sum(exps) or 1.0
        weights = [e / denom for e in exps]
        fused = [0.0] * len(scored_vectors[0][1])
        for (w, (_, vec)) in zip(weights, scored_vectors):
            for i, val in enumerate(vec):
                fused[i] += w * val
        logger.debug("Fused %d embedding modalities", len(scored_vectors))
        return fused

__all__ = ["EmbeddingFusion"]
