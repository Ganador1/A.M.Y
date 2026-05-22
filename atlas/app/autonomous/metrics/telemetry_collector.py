"""Telemetry collector for Agent 3 autonomous loops.
Wraps core metrics operations with domain-specific counters/histograms.
"""
from __future__ import annotations

from typing import Dict, Any
import time
from app.monitoring.metrics import metrics


class AutonomousTelemetry:
    def __init__(self):
        self.start_time = time.time()

    def record_iteration(self, domain: str, duration_s: float, selected: int, mutations: int, sketches: int):
        """Record metrics for a single autonomous loop iteration.

        Parameters
        ----------
        domain: str
            Domain label (e.g., "mathematics"). Used for domain-specific counters.
        duration_s: float
            Execution time of the iteration in seconds.
        selected: int
            Number of hypotheses/conjectures selected after scheduling & budgeting.
        mutations: int
            Number of mutation variants produced.
        sketches: int
            Number of proof sketches generated.
        """
        metrics.increment_counter("autonomous_iterations_total")
        metrics.increment_counter(f"autonomous_iterations_domain_{domain}")
        metrics.record_histogram("conjecture_priority_latency_seconds", duration_s)
        metrics.set_gauge("autonomous_selected_last", float(selected))
        metrics.set_gauge("autonomous_mutations_last", float(mutations))
        metrics.set_gauge("autonomous_sketches_last", float(sketches))
        if selected:
            metrics.set_gauge("mutation_yield_ratio", mutations / max(selected, 1))

    def uptime_seconds(self) -> float:
        return time.time() - self.start_time

    def summary(self) -> Dict[str, Any]:
        data = metrics.get_metrics_summary()
        data["autonomous_uptime_seconds"] = self.uptime_seconds()
        return data

telemetry = AutonomousTelemetry()

__all__ = ["telemetry", "AutonomousTelemetry"]
