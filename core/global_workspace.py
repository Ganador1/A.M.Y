"""
Global Workspace — The attention bus.

Based on Global Workspace Theory (Baars 1988, Dehaene et al. 1998).

Multiple cognitive modules produce "candidates" for attention.
They compete. The winner gets "broadcast" to ALL modules.
This is how A.M.Y achieves integrated cognition — all parts
of her mind stay synchronized through the broadcast.
"""
import structlog

log = structlog.get_logger()


class GlobalWorkspace:
    """
    The spotlight of consciousness.
    
    Candidates compete for the workspace based on:
    - Priority (urgency/importance)
    - Relevance to current goal
    - Novelty (how surprising)
    - Coalition strength (multiple modules supporting the same content)
    """

    def __init__(self):
        self._broadcast_history: list[dict] = []
        self._subscribers: list = []  # Modules listening to broadcasts

    async def compete_and_broadcast(self, candidates: list[dict]) -> dict:
        """
        Run the competition and broadcast the winner.
        
        Each candidate has:
        - content: what it's about
        - source: which module produced it
        - priority: numeric weight (0-1)
        - type: goal_directed, curiosity_driven, memory_driven, etc.
        """
        if not candidates:
            return {
                "content": "No active focus — entering contemplation mode",
                "source": "workspace",
                "priority": 0.0,
                "type": "idle",
            }

        # Score each candidate
        scored = []
        for c in candidates:
            score = self._compute_score(c)
            scored.append((score, c))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        winner = scored[0][1]
        winner["workspace_score"] = scored[0][0]

        # Broadcast to all subscribers
        await self._broadcast(winner)

        # Record history
        self._broadcast_history.append(winner)
        if len(self._broadcast_history) > 200:
            self._broadcast_history = self._broadcast_history[-100:]

        log.debug(
            "workspace.winner",
            source=winner["source"],
            score=scored[0][0],
            candidates_count=len(candidates),
        )
        return winner

    def _compute_score(self, candidate: dict) -> float:
        """
        Score a candidate for the workspace competition.
        
        Factors:
        - Base priority from the module
        - Novelty bonus (haven't focused on this recently)
        - Coalition bonus (if multiple modules point to same topic)
        """
        base_priority = candidate.get("priority", 0.5)

        # Novelty bonus — penalize if we recently focused on the same source
        novelty_bonus = 0.0
        recent_sources = [h["source"] for h in self._broadcast_history[-10:]]
        if candidate["source"] not in recent_sources:
            novelty_bonus = 0.15  # Encourage switching focus

        # Type bonus — goal-directed gets a small boost
        type_bonus = 0.0
        if candidate.get("type") == "goal_directed":
            type_bonus = 0.1
        elif candidate.get("type") == "curiosity_driven":
            type_bonus = 0.05

        return base_priority + novelty_bonus + type_bonus

    async def _broadcast(self, winner: dict):
        """Notify all subscribed modules about the current focus."""
        for subscriber in self._subscribers:
            try:
                await subscriber.on_broadcast(winner)
            except Exception as e:
                log.warning("workspace.broadcast_error", subscriber=str(subscriber), error=str(e))

    def subscribe(self, module):
        """Register a module to receive broadcasts."""
        self._subscribers.append(module)

    def get_recent_focus_history(self, n: int = 10) -> list[dict]:
        """Get the last N items that won the workspace competition."""
        return self._broadcast_history[-n:]
