"""Smoke test for MathematicsLoop."""
from app.autonomous.pipelines.mathematics_loop import MathematicsLoop
from app.autonomous.core.state_manager import StateManager


def dummy_provider():
    items = []
    for i in range(5):
        items.append({
            "id": f"c{i}",
            "importance": 0.5 + i * 0.1,
            "proveability": 0.4 + i * 0.05,
            "novelty": 0.3 + i * 0.07,
            "information_gain": 0.2 + i * 0.03,
            "estimated_cost": 1 + 0.2 * i,
            "statement": f"Hypothesis {i}"
        })
    return items

if __name__ == "__main__":
    loop = MathematicsLoop(provider=dummy_provider, state=StateManager())
    out = loop.run_iteration(1)
    print(out["summary"])  # basic confirmation
