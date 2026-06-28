"""
Semantic Memory — The knowledge graph.

Like the neocortex: stores facts and relationships.
Inspired by NELL (Never-Ending Language Learning) from CMU.

Each fact has:
- Subject, predicate, object (triple)
- Confidence score
- Source (where it was learned)
- Timestamp
"""
import asyncio
import json
import os
import time
from pathlib import Path

import structlog

log = structlog.get_logger()


class SemanticMemory:
    """
    A growing knowledge graph of facts about the domain.
    Persisted as JSON for inspection and portability.
    """

    def __init__(self, config: dict):
        self.graph_path = Path(config.get("knowledge_graph_path", "./data/knowledge_graph.json"))
        self.graph_path.parent.mkdir(parents=True, exist_ok=True)
        self.confidence_threshold = config.get("belief_confidence_threshold", 0.3)
        # Debounce disk writes: previously _save() ran on EVERY add_fact and
        # rewrote the whole graph (json.dump of the full dict), i.e. O(n) per
        # write / O(n²) per run, synchronously on the event loop. We now mark
        # the graph dirty and flush at most once per interval (plus an explicit
        # flush() on shutdown), off the event loop, atomically.
        self.save_interval_seconds = config.get("knowledge_graph_save_interval", 5.0)
        self.max_sources_per_fact = config.get("max_sources_per_fact", 25)
        self.facts: dict[str, dict] = {}
        self._dirty = False
        self._last_save = 0.0
        self._load()

    def _load(self):
        """Load existing knowledge graph from disk.

        On a corrupt/truncated file we back it up and start fresh rather than
        silently discarding the user's whole knowledge graph with no trace."""
        if not self.graph_path.exists():
            return
        try:
            with open(self.graph_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.facts = data.get("facts", {})
            log.info("semantic_memory.loaded", count=len(self.facts))
        except (json.JSONDecodeError, KeyError, OSError) as exc:
            # Preserve the corrupt file for forensics instead of zeroing memory.
            try:
                backup = self.graph_path.with_suffix(self.graph_path.suffix + f".corrupt.{int(time.time())}")
                os.replace(self.graph_path, backup)
                log.error("semantic_memory.load_corrupt_backed_up", error=str(exc), backup=str(backup))
            except OSError:
                log.error("semantic_memory.load_corrupt", error=str(exc))
            self.facts = {}

    def _write_to_disk(self):
        """Atomically persist the graph (tmp file + os.replace) so a crash
        mid-write cannot leave a truncated file that _load would then wipe."""
        tmp = self.graph_path.with_suffix(self.graph_path.suffix + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"facts": self.facts, "updated_at": time.time()}, f, indent=2)
        os.replace(tmp, self.graph_path)

    async def _maybe_save(self):
        """Flush to disk if dirty and the debounce interval has elapsed."""
        self._dirty = True
        now = time.time()
        if now - self._last_save < self.save_interval_seconds:
            return
        self._last_save = now
        self._dirty = False
        await asyncio.to_thread(self._write_to_disk)

    async def flush(self):
        """Force an immediate save if there are unsaved changes (call on shutdown)."""
        if not self._dirty:
            return
        self._last_save = time.time()
        self._dirty = False
        await asyncio.to_thread(self._write_to_disk)

    async def add_fact(
        self,
        subject: str,
        predicate: str,
        obj: str,
        confidence: float = 0.5,
        source: str = "",
    ):
        """Add or update a fact in the knowledge graph."""
        key = f"{subject}|{predicate}|{obj}"

        if key in self.facts:
            existing = self.facts[key]
            # Evidence-weighted update: weight the accumulated belief by how many
            # times it has been seen, so a single weak re-observation can't
            # collapse a heavily-confirmed fact (plain averaging did: a fact
            # seen 36× at 0.95 dropped to 0.625 on one 0.3 observation).
            # Use .get/.setdefault because _load ingests external JSON that may
            # follow the documented singular-'source' schema (no 'sources' list).
            times_seen = existing.get("times_seen", 1)
            old_conf = existing.get("confidence", 0.5)
            new_conf = (old_conf * times_seen + confidence) / (times_seen + 1)
            existing["confidence"] = new_conf
            existing["times_seen"] = times_seen + 1
            existing["last_updated"] = time.time()
            sources = existing.setdefault("sources", [existing.get("source", "")])
            # Dedup + cap so a fact re-seen thousands of times from the same
            # place doesn't accumulate thousands of identical source strings.
            if source not in sources:
                sources.append(source)
                if len(sources) > self.max_sources_per_fact:
                    del sources[0]
        else:
            self.facts[key] = {
                "subject": subject,
                "predicate": predicate,
                "object": obj,
                "confidence": confidence,
                "source": source,
                "sources": [source],
                "created_at": time.time(),
                "last_updated": time.time(),
                "times_seen": 1,
            }

        await self._maybe_save()

    async def query(self, subject: str = "", predicate: str = "", obj: str = "") -> list[dict]:
        """Query facts matching the given pattern."""
        results = []
        for key, fact in self.facts.items():
            match = True
            if subject and subject.lower() not in fact["subject"].lower():
                match = False
            if predicate and predicate.lower() not in fact["predicate"].lower():
                match = False
            if obj and obj.lower() not in fact["object"].lower():
                match = False
            if match:
                results.append(fact)
        return sorted(results, key=lambda x: -x["confidence"])

    async def get_high_confidence(self, min_confidence: float = 0.7) -> list[dict]:
        """Get all facts above a confidence threshold."""
        return [f for f in self.facts.values() if f["confidence"] >= min_confidence]

    async def get_uncertain(self, max_confidence: float = 0.5) -> list[dict]:
        """Get facts that we're unsure about — candidates for investigation."""
        return [f for f in self.facts.values() if f["confidence"] <= max_confidence]

    async def remove_fact(self, key: str):
        """Remove a fact (used during pruning)."""
        if key in self.facts:
            del self.facts[key]
            await self._maybe_save()

    async def count(self) -> int:
        return len(self.facts)

    async def summarize(self) -> str:
        """Get a text summary of the knowledge graph."""
        if not self.facts:
            return "No knowledge yet."

        high = await self.get_high_confidence()
        uncertain = await self.get_uncertain()

        summary = f"Total facts: {len(self.facts)}\n"
        summary += f"High confidence: {len(high)}\n"
        summary += f"Uncertain: {len(uncertain)}\n\n"

        if high:
            summary += "Top confirmed facts:\n"
            for f in high[:10]:
                summary += f"  - {f['subject']} {f['predicate']} {f['object']} ({f['confidence']:.2f})\n"

        return summary
