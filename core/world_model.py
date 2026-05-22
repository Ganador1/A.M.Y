"""
World Model — The internal generative model of reality.

Based on Active Inference / Free Energy Principle (Friston 2010).

A.M.Y maintains an internal model of "how the world works" relative
to her mission. This model generates PREDICTIONS about what she
expects to find. When reality diverges from predictions → surprise →
which triggers either:
  - Update the model (learn)
  - Act on the world (experiment)

This is the core of Active Inference: minimize the gap between
what you expect and what you observe.
"""
import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class Belief:
    """A single belief in the world model."""
    content: str
    confidence: float  # 0.0 to 1.0
    source: str
    timestamp: float = field(default_factory=time.time)
    times_confirmed: int = 0
    times_contradicted: int = 0

    @property
    def reliability(self) -> float:
        total = self.times_confirmed + self.times_contradicted
        if total == 0:
            return self.confidence
        return self.times_confirmed / total


class WorldModel:
    """
    The generative model of the world.
    
    Maintains beliefs about:
    - The domain of the mission (e.g., cancer biology, trading patterns)
    - What actions lead to what outcomes
    - What information is still unknown (uncertainty)
    
    The model is always being updated:
    - New observations → update beliefs (Bayesian update)
    - High surprise → flag for investigation
    - Low confidence beliefs → candidates for pruning or verification
    """

    def __init__(self, semantic_memory, episodic_memory):
        self.semantic_memory = semantic_memory
        self.episodic_memory = episodic_memory
        self.beliefs: dict[str, Belief] = {}
        self.predictions: list[dict] = []
        self._total_surprise: float = 0.0
        self._observation_count: int = 0

    async def compute_surprise(self, perceptions: list[dict]) -> float:
        """
        How surprising are the current perceptions given our model?
        
        Surprise = divergence between predicted and observed states.
        High surprise → the world model needs updating.
        This is the "free energy" that A.M.Y is always trying to minimize.
        """
        if not self.predictions:
            # No predictions yet — everything is maximally surprising
            return 0.5

        surprise = 0.0
        comparison_count = 0

        for perception in perceptions:
            source = perception.get("source", "")
            data = perception.get("data", {})

            # Find predictions related to this perception
            related_predictions = [
                p for p in self.predictions
                if p.get("domain") == source
            ]

            if related_predictions:
                for pred in related_predictions:
                    # Simple surprise: did reality match our prediction?
                    match = self._compare_prediction_to_reality(pred, data)
                    surprise += (1.0 - match)
                    comparison_count += 1

        if comparison_count > 0:
            surprise /= comparison_count

        self._total_surprise += surprise
        self._observation_count += 1

        return surprise

    def _compare_prediction_to_reality(self, prediction: dict, observation: dict) -> float:
        """
        Returns a match score 0-1 between a prediction and an observation.
        1.0 = perfect match, 0.0 = completely wrong.
        """
        # For now, simple keyword overlap. Will be replaced with
        # proper embedding similarity as we develop.
        pred_content = str(prediction.get("content", "")).lower()
        obs_content = str(observation).lower()

        if not pred_content or not obs_content:
            return 0.5  # Neutral — can't compare

        pred_words = set(pred_content.split())
        obs_words = set(obs_content.split())

        if not pred_words:
            return 0.5

        overlap = len(pred_words & obs_words)
        return min(1.0, overlap / max(len(pred_words), 1))

    async def update_beliefs(self, thought: dict, action_result: dict):
        """
        Bayesian update of beliefs based on new evidence.
        This is how A.M.Y learns.
        """
        new_facts = thought.get("new_facts", [])

        for fact in new_facts:
            key = f"{fact.get('subject', '')}:{fact.get('predicate', '')}:{fact.get('object', '')}"
            new_confidence = fact.get("confidence", 0.5)

            if key in self.beliefs:
                existing = self.beliefs[key]
                # Bayesian-ish update: combine old and new evidence
                if abs(existing.confidence - new_confidence) < 0.2:
                    # Confirmation
                    existing.times_confirmed += 1
                    existing.confidence = min(1.0, existing.confidence + 0.05)
                else:
                    # Contradiction — this is interesting!
                    existing.times_contradicted += 1
                    # Move confidence toward the new evidence
                    existing.confidence = (existing.confidence + new_confidence) / 2
                    log.info(
                        "world_model.belief_contradicted",
                        key=key,
                        old_conf=existing.confidence,
                        new_conf=new_confidence,
                    )
            else:
                self.beliefs[key] = Belief(
                    content=key,
                    confidence=new_confidence,
                    source=f"cycle_{thought.get('cycle', 'unknown')}",
                )

    async def update_with_observations(self, observations: list[dict]):
        """Update the model with raw observations from the environment."""
        for obs in observations:
            # Generate new predictions based on observations
            self.predictions.append({
                "domain": obs.get("source", "unknown"),
                "content": obs.get("summary", str(obs)),
                "timestamp": time.time(),
            })

        # Prune old predictions (keep last 100)
        if len(self.predictions) > 100:
            self.predictions = self.predictions[-100:]

    async def generate_predictions(self, goal: str) -> list[dict]:
        """
        Generate predictions about what A.M.Y expects to find next.
        These predictions are what get compared to reality to compute surprise.
        """
        predictions = []

        # Based on current beliefs, what should we expect?
        high_confidence = [
            b for b in self.beliefs.values() if b.confidence > 0.7
        ]
        for belief in high_confidence[:5]:
            predictions.append({
                "domain": "beliefs",
                "content": belief.content,
                "confidence": belief.confidence,
            })

        self.predictions = predictions
        return predictions

    async def get_uncertainty_map(self) -> list[dict]:
        """
        What doesn't A.M.Y know? Where is her uncertainty highest?
        This feeds the curiosity module.
        """
        uncertain = [
            {"content": b.content, "confidence": b.confidence, "reliability": b.reliability}
            for b in self.beliefs.values()
            if b.confidence < 0.5 or b.reliability < 0.5
        ]
        return sorted(uncertain, key=lambda x: x["confidence"])

    async def prune_low_confidence(self, threshold: float = 0.2):
        """Remove beliefs that are consistently unreliable."""
        to_remove = [
            key for key, belief in self.beliefs.items()
            if belief.reliability < threshold and belief.times_contradicted > 3
        ]
        for key in to_remove:
            log.info("world_model.pruning_belief", key=key)
            del self.beliefs[key]

    @property
    def average_surprise(self) -> float:
        if self._observation_count == 0:
            return 0.5
        return self._total_surprise / self._observation_count
