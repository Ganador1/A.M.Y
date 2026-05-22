"""Vector Store Abstraction (Stub)

Provee una interfaz mínima para almacenar embeddings y realizar búsquedas de similitud
coseno en memoria. Sustituible posteriormente por FAISS, Chroma, Weaviate, etc.
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional, Iterable, Tuple
import math
import threading

class VectorStoreProvider:
    def add(self, vectors: List[List[float]], metadatas: Optional[List[Dict[str, Any]]] = None) -> List[str]:  # pragma: no cover - interfaz
        raise NotImplementedError
    def similarity_search(self, query_vector: List[float], k: int = 5) -> List[Dict[str, Any]]:  # pragma: no cover - interfaz
        raise NotImplementedError
    def delete(self, ids: Iterable[str]) -> int:  # pragma: no cover - interfaz
        raise NotImplementedError
    def count(self) -> int:  # pragma: no cover - interfaz
        raise NotImplementedError

class InMemoryVectorStore(VectorStoreProvider):
    def __init__(self):
        self._data: Dict[str, Tuple[List[float], Dict[str, Any]]] = {}
        self._lock = threading.Lock()
        self._id_counter = 0

    def _gen_id(self) -> str:
        self._id_counter += 1
        return f"vec_{self._id_counter}"

    def add(self, vectors: List[List[float]], metadatas: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        ids: List[str] = []
        metas = metadatas or [{} for _ in vectors]
        if len(metas) != len(vectors):
            raise ValueError("metadatas length mismatch")
        with self._lock:
            for vec, meta in zip(vectors, metas):
                vid = self._gen_id()
                self._data[vid] = (vec, meta)
                ids.append(vid)
        return ids

    def similarity_search(self, query_vector: List[float], k: int = 5) -> List[Dict[str, Any]]:
        if not self._data:
            return []
        qnorm = math.sqrt(sum(x * x for x in query_vector)) or 1e-9
        scored = []
        for vid, (vec, meta) in self._data.items():
            if len(vec) != len(query_vector):
                continue
            dot = sum(a * b for a, b in zip(vec, query_vector))
            vnorm = math.sqrt(sum(x * x for x in vec)) or 1e-9
            score = dot / (qnorm * vnorm)
            scored.append((score, vid, meta))
        scored.sort(key=lambda t: t[0], reverse=True)
        out = []
        for score, vid, meta in scored[:k]:
            out.append({"id": vid, "score": round(score, 6), "metadata": meta})
        return out

    def delete(self, ids: Iterable[str]) -> int:
        removed = 0
        with self._lock:
            for i in ids:
                if i in self._data:
                    del self._data[i]
                    removed += 1
        return removed

    def count(self) -> int:
        return len(self._data)

# Singleton simple para uso ligero
vector_store_singleton = InMemoryVectorStore()
