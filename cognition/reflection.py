"""
Reflection Module — Metacognition and memory consolidation.

Based on:
- Generative Agents (Park et al. 2023): Periodic reflection that
  extracts high-level insights from episodic memories
- SOAR's chunking: Compile deliberative reasoning into automatic skills
- NELL's self-correction: Review and prune low-confidence beliefs

Reflection is like stepping back and thinking about your thinking.
It happens periodically (every N cycles) or when triggered by
significant events.
"""
import structlog

log = structlog.get_logger()


class ReflectionModule:
    """
    Periodic self-reflection and memory consolidation.

    What happens during reflection:
    1. Review recent episodic memories
    2. Use LLM to extract high-level insights and concrete sub-goals
    3. Update semantic memory with new knowledge
    4. Prune contradicted or low-confidence beliefs
    5. Push new actionable sub-goals to the goal stack
    6. Consolidate successful strategies into skills
    """

    def __init__(self, episodic_memory, semantic_memory):
        self.episodic_memory = episodic_memory
        self.semantic_memory = semantic_memory
        self._reflection_count = 0
        # Lazy-set by heartbeat after init
        self.reasoning_engine = None
        self.goal_stack = None

    async def reflect(self, world_model, goal_stack):
        """
        Main reflection cycle. Called periodically by the heartbeat.
        """
        self._reflection_count += 1
        log.info("reflection.starting", count=self._reflection_count)

        # 1. Gather recent experiences
        recent = await self.episodic_memory.get_recent(n=60)

        if not recent:
            log.info("reflection.nothing_to_reflect")
            return

        # 2. Extract patterns via LLM (if reasoning engine available)
        if self.reasoning_engine is not None:
            patterns = await self._extract_patterns_llm(recent, goal_stack)
        else:
            patterns = self._extract_patterns_heuristic(recent)

        # 3. Update semantic memory with insights
        for insight in patterns.get("insights", []):
            await self.semantic_memory.add_fact(
                subject=insight.get("topic", "reflection"),
                predicate="insight",
                obj=insight.get("content", ""),
                confidence=insight.get("confidence", 0.6),
                source=f"reflection_{self._reflection_count}",
            )

        # 4. Prune bad beliefs
        await world_model.prune_low_confidence()

        # 5. Push concrete NEW sub-goals (replacing vague gaps)
        new_subgoals = patterns.get("new_subgoals", [])
        pushed = 0
        for sg in new_subgoals:
            if sg and len(sg) > 10:
                await goal_stack.push_subgoal(
                    parent=goal_stack.mission_id or "",
                    description=sg,
                    priority=0.7,
                )
                pushed += 1

        # Also push knowledge gaps as sub-goals
        for gap in patterns.get("knowledge_gaps", [])[:3]:
            if gap:
                await goal_stack.push_subgoal(
                    parent=goal_stack.mission_id or "",
                    description=f"Investigate gap: {gap}",
                    priority=0.5,
                )
                pushed += 1

        # 6. Check for skills to consolidate
        for strategy in patterns.get("successful_strategies", [])[:2]:
            log.info("reflection.potential_skill", strategy=str(strategy)[:80])

        log.info(
            "reflection.complete",
            reflection=self._reflection_count,
            insights=len(patterns.get("insights", [])),
            new_subgoals=pushed,
        )

    async def consolidate_before_shutdown(self):
        """Emergency consolidation before the system shuts down."""
        log.info("reflection.emergency_consolidation")
        recent = await self.episodic_memory.get_recent(n=100)
        if recent:
            await self.episodic_memory.record(
                event_type="shutdown_consolidation",
                content=f"Consolidated {len(recent)} recent memories before shutdown",
                metadata={"reflection_count": self._reflection_count},
            )

    async def _extract_patterns_llm(self, memories: list[dict], goal_stack) -> dict:
        """
        Use GLM-5.1 to perform genuine metacognitive analysis.
        Produces concrete next sub-goals based on what was done and what's missing.
        """
        import json

        # Build a compact summary of what happened
        cycles = [m for m in memories if m["event_type"] == "cognitive_cycle"]
        searches = [m for m in memories if m["event_type"] == "research"]
        errors = [m for m in memories if m["event_type"] == "error"]

        # Recent thought summaries
        thought_lines = "\n".join(
            f"- [{m['event_type']}] {m['content'][:120]}"
            for m in memories[-20:]
        )
        # All queries done
        query_lines = "\n".join(
            f"- {m['content'][:100]}" for m in searches[-20:]
        )
        # Current mission
        mission = ""
        if goal_stack and goal_stack.mission_id:
            mission_goal = goal_stack.goals.get(goal_stack.mission_id)
            if mission_goal:
                mission = mission_goal.description

        prompt_messages = [
            {
                "role": "system",
                "content": (
                    "You are A.M.Y's metacognitive reflection module. "
                    "Analyze recent cognitive activity and produce a strategic plan. "
                    "Be brutally honest about patterns, loops, and missing steps. "
                    "Always return valid JSON."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"## Mission\n{mission}\n\n"
                    f"## Recent Activity ({len(memories)} events)\n{thought_lines}\n\n"
                    f"## Searches Performed ({len(searches)} total)\n{query_lines}\n\n"
                    f"## Errors: {len(errors)}\n\n"
                    "Reflect on this and return JSON:\n"
                    "{\n"
                    '  "diagnosis": "honest assessment of what went well and what failed",\n'
                    '  "loop_detected": true/false,\n'
                    '  "loop_description": "describe the loop if any",\n'
                    '  "insights": [\n'
                    '    {"topic": "...", "content": "key insight", "confidence": 0.8}\n'
                    '  ],\n'
                    '  "knowledge_gaps": ["specific gap 1", "specific gap 2"],\n'
                    '  "new_subgoals": [\n'
                    '    "Concrete, specific, actionable sub-goal 1",\n'
                    '    "Concrete sub-goal 2 with specific target"\n'
                    '  ],\n'
                    '  "recommended_next_action": "research|decompose_goal|experiment|think_more"\n'
                    "}\n\n"
                    "Make new_subgoals VERY specific — not 'investigate X' but "
                    "'Find phase III clinical trial results for DNX-2401 vs standard GBM treatment'."
                ),
            },
        ]

        try:
            from core.ollama_client import _load_env
            _load_env()
            response = await self.reasoning_engine.client.chat(
                model=self.reasoning_engine.reasoner_model,
                messages=prompt_messages,
                temperature=0.4,
                max_tokens=2048,
                format_json=True,
                num_ctx=self.reasoning_engine.reasoner_ctx,
            )
            from cognition.reasoning import _extract_content, _clean_json
            raw = _extract_content(response)
            raw = _clean_json(raw)
            result = json.loads(raw)

            loop = result.get("loop_detected", False)
            diag = result.get("diagnosis", "")
            log.info(
                "reflection.llm_complete",
                loop_detected=loop,
                loop_desc=result.get("loop_description", "")[:80],
                diagnosis=diag[:120],
                new_subgoals=len(result.get("new_subgoals", [])),
            )
            return result

        except Exception as e:
            log.warning("reflection.llm_failed", error=str(e))
            return self._extract_patterns_heuristic(memories)

    def _extract_patterns_heuristic(self, memories: list[dict]) -> dict:
        """Fallback: simple keyword-based pattern extraction."""
        by_type: dict[str, list] = {}
        for mem in memories:
            by_type.setdefault(mem.get("event_type", "unknown"), []).append(mem)

        insights = []
        knowledge_gaps = []
        successful_strategies = []
        new_subgoals = []

        research_memories = by_type.get("research", [])
        if research_memories:
            topics = [m.get("metadata", {}).get("query", "") for m in research_memories]
            topic_counts: dict[str, int] = {}
            for t in topics:
                for word in t.lower().split():
                    if len(word) > 4:
                        topic_counts[word] = topic_counts.get(word, 0) + 1
            frequent = sorted(topic_counts.items(), key=lambda x: -x[1])
            if frequent:
                top_terms = [w for w, c in frequent[:5] if c >= 2]
                if top_terms:
                    insights.append({
                        "topic": "research_focus",
                        "content": f"Recurring themes: {', '.join(top_terms)}",
                        "confidence": 0.7,
                    })
                    new_subgoals.append(
                        f"Synthesize findings on: {', '.join(top_terms[:3])}"
                    )

        error_memories = by_type.get("error", [])
        if error_memories:
            insights.append({
                "topic": "system_health",
                "content": f"{len(error_memories)} errors in recent cycles",
                "confidence": 0.9,
            })

        # If many research cycles with no experiments → push experiment goal
        if len(research_memories) > 10:
            new_subgoals.append(
                "Design and run a computational experiment to test the leading hypothesis"
            )

        return {
            "insights": insights,
            "knowledge_gaps": knowledge_gaps,
            "successful_strategies": successful_strategies,
            "new_subgoals": new_subgoals,
        }
