"""
Episodic Memory — What happened and when.

Like the hippocampus: records experiences with temporal context.
Each memory is a timestamped event with content and metadata.
Used for:
- Recalling what was done before
- Avoiding repetition
- Providing context for reflection
- Detecting patterns over time
"""
import json
import time
from pathlib import Path

import structlog

log = structlog.get_logger()


class EpisodicMemory:
    """
    Sequential log of everything A.M.Y experiences.
    Persisted as JSONL (one JSON object per line) for simplicity and durability.
    """

    def __init__(self, config: dict):
        self.log_path = Path(config.get("episodic_log_path", "./data/episodic_memory.jsonl"))
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.max_before_consolidation = config.get("max_episodic_before_consolidation", 1000)
        self._buffer: list[dict] = []
        self._count = 0

    async def record(self, event_type: str, content: str, metadata: dict | None = None):
        """Record an event to episodic memory."""
        entry = {
            "timestamp": time.time(),
            "event_type": event_type,
            "content": content,
            "metadata": metadata or {},
            "id": self._count,
        }

        self._buffer.append(entry)
        self._count += 1

        # Persist to disk
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

        # Trim in-memory buffer
        if len(self._buffer) > self.max_before_consolidation:
            self._buffer = self._buffer[-500:]

    async def get_recent(self, n: int = 50) -> list[dict]:
        """Get the N most recent memories."""
        return self._buffer[-n:]

    async def get_recent_relevant(self, context: str, n: int = 5) -> dict | None:
        """
        Find the most relevant recent memory for a given context.
        Simple keyword matching for now — will use embeddings later.
        """
        if not self._buffer or not context:
            return None

        context_words = set(context.lower().split())
        scored = []

        for mem in self._buffer[-100:]:
            content_words = set(mem.get("content", "").lower().split())
            overlap = len(context_words & content_words)
            if overlap > 0:
                scored.append((overlap, mem))

        if scored:
            scored.sort(key=lambda x: -x[0])
            best = scored[0][1]
            best["relevance"] = scored[0][0] / max(len(context_words), 1)
            return best

        return None

    async def search(self, query: str, max_results: int = 10) -> list[dict]:
        """Search episodic memory for matching entries."""
        query_words = set(query.lower().split())
        results = []

        for mem in reversed(self._buffer):
            content = mem.get("content", "").lower()
            if any(w in content for w in query_words):
                results.append(mem)
                if len(results) >= max_results:
                    break

        return results

    async def count(self) -> int:
        return self._count
