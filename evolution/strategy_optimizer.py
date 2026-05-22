"""
Strategy Optimizer — Optimizes A.M.Y's research strategies over time.

Learns from past successes and failures to improve:
- Which research directions are most fruitful
- When to pivot vs persist
- Optimal resource allocation
"""
import structlog

log = structlog.get_logger()


class StrategyOptimizer:
    """Optimizes research strategies based on historical performance."""

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.strategy_history: list[dict] = []
        self.action_success_rates: dict[str, dict] = {}  # action_type -> {successes, failures}

    def record_outcome(self, action_type: str, success: bool, metadata: dict | None = None):
        """Record the outcome of an action for strategy learning."""
        if action_type not in self.action_success_rates:
            self.action_success_rates[action_type] = {"successes": 0, "failures": 0}

        if success:
            self.action_success_rates[action_type]["successes"] += 1
        else:
            self.action_success_rates[action_type]["failures"] += 1

        self.strategy_history.append({
            "action_type": action_type,
            "success": success,
            "metadata": metadata or {},
        })

        log.debug(
            "strategy_optimizer.recorded",
            action=action_type,
            success=success,
            rate=self.get_success_rate(action_type),
        )

    def get_success_rate(self, action_type: str) -> float:
        """Get the success rate for an action type."""
        stats = self.action_success_rates.get(action_type, {"successes": 0, "failures": 0})
        total = stats["successes"] + stats["failures"]
        return stats["successes"] / max(total, 1)

    def recommend_action(self, available_actions: list[str]) -> str | None:
        """Recommend the action with the highest expected success rate."""
        if not available_actions:
            return None

        # Score each action by success rate + exploration bonus
        scores = {}
        for action in available_actions:
            rate = self.get_success_rate(action)
            # Exploration bonus: actions with fewer trials get a boost
            stats = self.action_success_rates.get(action, {"successes": 0, "failures": 0})
            total = stats["successes"] + stats["failures"]
            exploration_bonus = 1.0 / (1 + total)  # Decays with more trials
            scores[action] = rate + exploration_bonus

        best_action = max(scores, key=scores.get)
        log.info(
            "strategy_optimizer.recommendation",
            action=best_action,
            score=scores[best_action],
        )
        return best_action

    def get_insights(self) -> dict:
        """Return strategic insights based on history."""
        if not self.strategy_history:
            return {"message": "No strategy history yet"}

        # Find best and worst performing actions
        rates = {
            action: self.get_success_rate(action)
            for action in self.action_success_rates
        }

        return {
            "best_action": max(rates, key=rates.get) if rates else None,
            "worst_action": min(rates, key=rates.get) if rates else None,
            "action_rates": rates,
            "total_actions": len(self.strategy_history),
            "overall_success_rate": sum(1 for h in self.strategy_history if h["success"]) / len(self.strategy_history),
        }
