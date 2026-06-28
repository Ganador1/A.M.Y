"""
Curiosity Module — Intrinsic motivation that drives exploration.

Based on:
- ICM (Pathak et al. 2017): Curiosity = prediction error
- RND (Burda et al. 2019): Random Network Distillation
- Active Inference epistemic value: Curiosity = expected information gain

When A.M.Y has no clear next step, curiosity drives her to
explore and reduce uncertainty. This prevents her from getting
stuck in local optima.
"""
import structlog

log = structlog.get_logger()


class CuriosityModule:
    """
    Generates curiosity signals that compete for attention in the Global Workspace.
    
    The curiosity signal is higher when:
    - The world model has high uncertainty in relevant areas
    - A topic hasn't been explored recently
    - The prediction error is high (something unexpected happened)
    - There's a promising lead that hasn't been followed
    """

    def __init__(self, config: dict):
        self.config = config
        self._explored_topics: dict[str, float] = {}  # topic → recency score
        self._novelty_decay = config.get("novelty_decay", 0.95)
        self._epistemic_weight = config.get("epistemic_weight", 0.4)
        # Once a topic's decayed recency drops below this it is fully novel
        # again; we evict it so the dict stays bounded and stale near-zero
        # entries don't drag avg_recency (and thus the novelty signal) toward 0.
        self._novelty_floor = config.get("novelty_floor", 0.05)
        self._max_explored_topics = config.get("max_explored_topics", 500)

    async def get_signal(self, world_model, goal_stack) -> dict:
        """
        Compute the current curiosity signal.
        
        Returns a dict with:
        - level: 0-1 how curious A.M.Y is right now
        - direction: what she's curious about
        - reason: why she's curious about it
        """
        # Get uncertainty map from world model
        uncertainties = await world_model.get_uncertainty_map()

        # Decay explored topics (things explored long ago become novel again),
        # evicting any that have decayed below the novelty floor so the dict
        # stays bounded and fully-decayed entries don't skew the average.
        self._decay_and_evict()

        # Compute curiosity components
        model_uncertainty = self._compute_model_uncertainty(uncertainties)
        exploration_novelty = self._compute_novelty()
        prediction_surprise = world_model.average_surprise

        # Combined curiosity signal. epistemic_weight controls the split between
        # the model-uncertainty (epistemic) term and the remaining
        # novelty+surprise terms, instead of hardcoded 0.4/0.3/0.3.
        ew = self._epistemic_weight
        rest = (1.0 - ew) / 2.0
        curiosity_level = (
            ew * model_uncertainty
            + rest * exploration_novelty
            + rest * prediction_surprise
        )

        # Identify what to be curious about
        direction = "general exploration"
        reason = "Default curiosity"

        if uncertainties:
            most_uncertain = uncertainties[0]
            direction = most_uncertain.get("content", "unknown topic")
            reason = f"High uncertainty (confidence: {most_uncertain.get('confidence', 0):.2f})"
        elif prediction_surprise > 0.7:
            direction = "unexpected observation"
            reason = f"Surprise level: {prediction_surprise:.2f}"

        return {
            "level": min(1.0, curiosity_level),
            "direction": direction,
            "reason": reason,
            "model_uncertainty": model_uncertainty,
            "exploration_novelty": exploration_novelty,
            "prediction_surprise": prediction_surprise,
        }

    async def update(self, thought: dict, action_result: dict):
        """
        Update curiosity after a cognitive cycle.
        Things we just explored become less novel.
        """
        topic = thought.get("content", "")[:50]
        if topic:
            self._explored_topics[topic] = 1.0  # Mark as freshly explored

        # If the action was research, mark the query as explored
        if action_result.get("type") == "research":
            query = action_result.get("query", "")
            if query:
                self._explored_topics[query] = 1.0

    def _decay_and_evict(self):
        """Decay every topic's recency and drop those below the novelty floor.

        A topic decayed below the floor is effectively novel again, so keeping
        it (a) grows the dict without bound over a long run and (b) pulls
        avg_recency toward 0, pinning the novelty signal near 1.0. If the dict
        is still oversized after eviction, drop the least-recent entries."""
        decayed = {
            t: r * self._novelty_decay
            for t, r in self._explored_topics.items()
            if r * self._novelty_decay >= self._novelty_floor
        }
        if len(decayed) > self._max_explored_topics:
            # Keep the most-recent (highest recency) topics.
            kept = sorted(decayed.items(), key=lambda kv: kv[1], reverse=True)[: self._max_explored_topics]
            decayed = dict(kept)
        self._explored_topics = decayed

    def _compute_model_uncertainty(self, uncertainties: list[dict]) -> float:
        """How uncertain is the world model overall?"""
        if not uncertainties:
            return 0.8  # High uncertainty when we know nothing
        avg_conf = sum(u.get("confidence", 0.5) for u in uncertainties) / len(uncertainties)
        return 1.0 - avg_conf

    def _compute_novelty(self) -> float:
        """How much unexplored territory is there?"""
        if not self._explored_topics:
            return 1.0  # Everything is novel
        # Average novelty = 1 - average recency
        avg_recency = sum(self._explored_topics.values()) / len(self._explored_topics)
        return 1.0 - avg_recency
