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
import asyncio
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
        # Hydrate from disk so A.M.Y is not amnesiac across restarts and so new
        # ids continue past the highest existing id (previously _count reset to
        # 0 every run, colliding with prior records — see the cycle_0 source
        # corruption in the knowledge graph).
        self._load()

    def _load(self) -> None:
        """Rehydrate the in-memory buffer from the JSONL tail and seed the id
        counter from the highest id on disk. Tolerant of partial/corrupt lines."""
        if not self.log_path.exists():
            return
        max_id = -1
        recent: list[dict] = []
        keep = self.max_before_consolidation
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue  # skip a torn/partial line, keep going
                    eid = entry.get("id")
                    if isinstance(eid, int) and eid > max_id:
                        max_id = eid
                    recent.append(entry)
                    if len(recent) > keep:
                        recent.pop(0)  # bounded tail, never load the whole file
        except OSError as exc:
            log.warning("episodic.load_failed", error=str(exc))
            return
        self._buffer = recent
        self._count = max_id + 1
        if self._buffer:
            log.info("episodic.loaded", entries=len(self._buffer), next_id=self._count)

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

        # Persist to disk off the event loop (sync append would block the
        # single asyncio loop that runs the whole mind; the JSONL grows large).
        line = json.dumps(entry) + "\n"
        await asyncio.to_thread(self._append_line, line)

        # Trim in-memory buffer
        if len(self._buffer) > self.max_before_consolidation:
            self._buffer = self._buffer[-500:]

    def _append_line(self, line: str) -> None:
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(line)

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
