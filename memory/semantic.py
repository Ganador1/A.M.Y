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
import json
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
        self.facts: dict[str, dict] = {}
        self._load()

    def _load(self):
        """Load existing knowledge graph from disk."""
        if self.graph_path.exists():
            try:
                with open(self.graph_path, "r") as f:
                    data = json.load(f)
                    self.facts = data.get("facts", {})
                    log.info("semantic_memory.loaded", count=len(self.facts))
            except (json.JSONDecodeError, KeyError):
                self.facts = {}

    def _save(self):
        """Persist knowledge graph to disk."""
        with open(self.graph_path, "w") as f:
            json.dump({"facts": self.facts, "updated_at": time.time()}, f, indent=2)

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
            # Bayesian update
            old_conf = existing["confidence"]
            new_conf = (old_conf + confidence) / 2
            existing["confidence"] = new_conf
            existing["times_seen"] = existing.get("times_seen", 1) + 1
            existing["last_updated"] = time.time()
            existing["sources"].append(source)
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

        self._save()

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
            self._save()

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
