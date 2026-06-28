"""Embedding-backed semantic index (optional, graceful-fallback).

A.M.Y's recall paths (skill retrieval, episodic/semantic lookup) match on
exact token overlap, which misses synonyms and morphology ('plotting' vs
'plot', 'web scraping' vs 'crawl'). This wraps a chromadb collection with
*manually supplied* embeddings (we embed via the injected `embed_fn`, e.g.
the Ollama client, rather than chroma's built-in model) so callers can add
documents and query by meaning.

Design constraints:
- Opt-in. The caller decides whether to construct one; if it isn't constructed,
  behavior is unchanged.
- Dependency-injected embed function → fully testable offline (pass a fake
  embedder) and no hard network dependency baked into the class.
- Fail-soft. Any embedding/chroma error returns an empty result so the caller
  can fall back to its existing keyword match; recall never breaks.
"""
import structlog

log = structlog.get_logger()


class SemanticIndex:
    def __init__(self, embed_fn, *, name: str = "amy_index", space: str = "cosine"):
        """embed_fn: async callable(text:str) -> list[float] (a single vector)."""
        self._embed_fn = embed_fn
        self._name = name
        self._space = space
        self._collection = None
        self._client = None

    def _ensure_collection(self):
        if self._collection is not None:
            return self._collection
        import chromadb  # imported lazily so the dependency is only needed when used

        self._client = chromadb.Client()  # in-process, ephemeral
        self._collection = self._client.get_or_create_collection(
            self._name, metadata={"hnsw:space": self._space}
        )
        return self._collection

    async def add(self, doc_id: str, text: str, metadata: dict | None = None) -> bool:
        """Embed and upsert one document. Returns False (no-op) on any failure."""
        try:
            vec = await self._embed_fn(text)
            if not vec:
                return False
            col = self._ensure_collection()
            kwargs = {
                "ids": [doc_id],
                "embeddings": [list(vec)],
                "documents": [text],
            }
            # chromadb rejects an empty metadata dict; only pass it when set.
            if metadata:
                kwargs["metadatas"] = [metadata]
            col.upsert(**kwargs)
            return True
        except Exception as exc:
            log.warning("semantic_index.add_failed", doc_id=doc_id, error=str(exc))
            return False

    async def query(self, text: str, n_results: int = 5) -> list[dict]:
        """Return up to n_results matches as
        [{'id','document','metadata','distance'}], best first. Empty on failure
        so the caller can fall back to keyword matching."""
        try:
            vec = await self._embed_fn(text)
            if not vec:
                return []
            col = self._ensure_collection()
            if col.count() == 0:
                return []
            res = col.query(query_embeddings=[list(vec)], n_results=min(n_results, col.count()))
            ids = (res.get("ids") or [[]])[0]
            docs = (res.get("documents") or [[]])[0]
            metas = (res.get("metadatas") or [[]])[0]
            dists = (res.get("distances") or [[]])[0]
            out = []
            for i, _id in enumerate(ids):
                out.append({
                    "id": _id,
                    "document": docs[i] if i < len(docs) else "",
                    "metadata": metas[i] if i < len(metas) else {},
                    "distance": dists[i] if i < len(dists) else None,
                })
            return out
        except Exception as exc:
            log.warning("semantic_index.query_failed", error=str(exc))
            return []
