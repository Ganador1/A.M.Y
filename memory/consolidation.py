"""Memory consolidation — like REM sleep for A.M.Y."""


class MemoryConsolidation:
    """
    Periodically consolidate episodic memories into semantic knowledge.
    This is the equivalent of "sleeping on it" — patterns emerge
    when you review your experiences.
    """

    def __init__(self, episodic_memory, semantic_memory, procedural_memory):
        self.episodic = episodic_memory
        self.semantic = semantic_memory
        self.procedural = procedural_memory

    async def consolidate(self):
        """Run a full consolidation cycle."""
        recent = await self.episodic.get_recent(n=200)
        if not recent:
            return

        # Extract repeated patterns → semantic facts
        await self._extract_patterns(recent)

        # Identify successful action sequences → procedural skills
        await self._extract_skills(recent)

    async def _extract_patterns(self, memories: list[dict]):
        """Find recurring themes in episodic memory → add to semantic."""
        word_freq: dict[str, int] = {}
        for mem in memories:
            for word in mem.get("content", "").lower().split():
                if len(word) > 5:
                    word_freq[word] = word_freq.get(word, 0) + 1

        significant = [(w, c) for w, c in word_freq.items() if c >= 5]
        for word, count in significant:
            await self.semantic.add_fact(
                subject="recurring_theme",
                predicate="appears_frequently",
                obj=word,
                confidence=min(1.0, count / 20),
                source="consolidation",
            )

    async def _extract_skills(self, memories: list[dict]):
        """Find successful experiment patterns → add to procedural."""
        experiments = [m for m in memories if m.get("event_type") == "experiment"]
        for exp in experiments:
            meta = exp.get("metadata", {})
            result = meta.get("result", {})
            if isinstance(result, dict) and result.get("success"):
                code = meta.get("code", "")
                if code:
                    await self.procedural.store_skill(
                        name=f"experiment_{exp.get('id', 'unknown')}",
                        description=exp.get("content", ""),
                        code=code,
                    )
