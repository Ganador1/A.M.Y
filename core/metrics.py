"""Runtime metrics for A.M.Y's heartbeat — observability without log-grepping.

A.M.Y's premise is a process that runs indefinitely and only contacts you when
there's something to report. That makes a cheap, always-current status surface
valuable: how many cycles, how many errors, what it's been doing, how the
experiment success rate is trending, and whether memory is bounded — all
without tailing logs.

HeartbeatMetrics is a plain in-memory accumulator (no I/O, no deps beyond
stdlib + optional psutil). snapshot() returns a JSON-serializable dict.
"""
from collections import Counter, deque

# psutil is optional; RSS is best-effort and omitted if unavailable.
try:
    import psutil  # type: ignore
    _PROC = psutil.Process()
except Exception:  # pragma: no cover - environment dependent
    _PROC = None


class HeartbeatMetrics:
    """Bounded, allocation-light counters for the cognitive loop."""

    def __init__(self, *, recent_window: int = 50, monotonic=None):
        # Injected clock keeps this unit-testable without real time.
        import time as _time
        self._now = monotonic or _time.monotonic

        self.cycles = 0
        self.errors = 0
        self.started_at = self._now()
        self.last_cycle_at: float | None = None

        self.actions: Counter = Counter()          # action_type -> count
        self.experiments_succeeded = 0
        self.experiments_failed = 0
        self.papers_written = 0
        self.reflections = 0
        self.consolidations = 0

        # Bounded ring of recent cycle durations (seconds) for a rolling mean.
        self._durations: deque[float] = deque(maxlen=recent_window)
        # Bounded ring of recent error messages for the snapshot.
        self._recent_errors: deque[str] = deque(maxlen=10)

    # ── recording ────────────────────────────────────────────────────────────

    def record_cycle(self, duration_seconds: float):
        self.cycles += 1
        self.last_cycle_at = self._now()
        if duration_seconds >= 0:
            self._durations.append(duration_seconds)

    def record_error(self, message: str):
        self.errors += 1
        self._recent_errors.append(message[:200])

    def record_action(self, action_type: str, result: dict | None = None):
        self.actions[action_type or "unknown"] += 1
        if action_type == "experiment" and isinstance(result, dict):
            r = result.get("result", {})
            ok = r.get("success") if isinstance(r, dict) else None
            if ok is True:
                self.experiments_succeeded += 1
            elif ok is False:
                self.experiments_failed += 1
        elif action_type == "write_paper":
            self.papers_written += 1

    def record_reflection(self):
        self.reflections += 1

    def record_consolidation(self):
        self.consolidations += 1

    # ── derived ────────────────────────────────────────────────────────────

    def _avg_cycle_seconds(self) -> float:
        return round(sum(self._durations) / len(self._durations), 3) if self._durations else 0.0

    def _experiment_success_rate(self) -> float | None:
        total = self.experiments_succeeded + self.experiments_failed
        if total == 0:
            return None
        return round(self.experiments_succeeded / total, 3)

    @staticmethod
    def _rss_mb() -> float | None:
        # Prefer psutil (portable bytes); otherwise fall back to the stdlib
        # resource module so RSS is still reported without an extra dependency.
        if _PROC is not None:
            try:
                return round(_PROC.memory_info().rss / (1024 * 1024), 1)
            except Exception:
                pass
        try:
            import resource
            import sys
            rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            # ru_maxrss is bytes on macOS, kilobytes on Linux.
            divisor = 1024 * 1024 if sys.platform == "darwin" else 1024
            return round(rss / divisor, 1)
        except Exception:
            return None

    def snapshot(self) -> dict:
        """A JSON-serializable point-in-time view of the loop's health."""
        return {
            "uptime_seconds": round(self._now() - self.started_at, 1),
            "cycles": self.cycles,
            "errors": self.errors,
            "error_rate": round(self.errors / self.cycles, 3) if self.cycles else 0.0,
            "avg_cycle_seconds": self._avg_cycle_seconds(),
            "actions": dict(self.actions),
            "experiments": {
                "succeeded": self.experiments_succeeded,
                "failed": self.experiments_failed,
                "success_rate": self._experiment_success_rate(),
            },
            "papers_written": self.papers_written,
            "reflections": self.reflections,
            "consolidations": self.consolidations,
            "rss_mb": self._rss_mb(),
            "recent_errors": list(self._recent_errors),
        }
