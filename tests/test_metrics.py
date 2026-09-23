#!/usr/bin/env python3
"""Hermetic tests for the observability surface (HeartbeatMetrics + snapshot).

Adds a status/metrics surface so A.M.Y's loop health is visible without
grepping logs (2026-06-28 re-review improvement).
"""
import pytest

from core.metrics import HeartbeatMetrics
from core.heartbeat import Heartbeat, CognitiveContext, CognitiveState


def _fake_clock():
    """A controllable monotonic clock for deterministic timing assertions."""
    t = {"now": 1000.0}
    def now():
        return t["now"]
    now.advance = lambda dt: t.__setitem__("now", t["now"] + dt)
    return now


def test_counts_cycles_errors_and_rate():
    m = HeartbeatMetrics(monotonic=_fake_clock())
    for _ in range(4):
        m.record_cycle(0.5)
    m.record_error("boom")
    snap = m.snapshot()
    assert snap["cycles"] == 4
    assert snap["errors"] == 1
    assert snap["error_rate"] == 0.25
    assert "boom" in snap["recent_errors"]


def test_avg_cycle_seconds_is_rolling_and_bounded():
    m = HeartbeatMetrics(recent_window=3, monotonic=_fake_clock())
    for d in (1.0, 2.0, 3.0, 4.0):  # window keeps only the last 3
        m.record_cycle(d)
    # mean of last 3 = (2+3+4)/3 = 3.0
    assert m.snapshot()["avg_cycle_seconds"] == 3.0


def test_action_mix_and_experiment_success_rate():
    m = HeartbeatMetrics(monotonic=_fake_clock())
    m.record_action("experiment", {"result": {"success": True}})
    m.record_action("experiment", {"result": {"success": True}})
    m.record_action("experiment", {"result": {"success": False}})
    m.record_action("search_literature")
    m.record_action("write_paper")
    snap = m.snapshot()
    assert snap["actions"]["experiment"] == 3
    assert snap["actions"]["search_literature"] == 1
    assert snap["experiments"]["succeeded"] == 2
    assert snap["experiments"]["failed"] == 1
    assert snap["experiments"]["success_rate"] == round(2 / 3, 3)
    assert snap["papers_written"] == 1


def test_experiment_success_rate_none_when_no_experiments():
    m = HeartbeatMetrics(monotonic=_fake_clock())
    assert m.snapshot()["experiments"]["success_rate"] is None


def test_uptime_uses_injected_clock():
    clock = _fake_clock()
    m = HeartbeatMetrics(monotonic=clock)
    clock.advance(42.0)
    assert m.snapshot()["uptime_seconds"] == 42.0


def test_recent_errors_bounded_to_10():
    m = HeartbeatMetrics(monotonic=_fake_clock())
    for i in range(15):
        m.record_error(f"err{i}")
    snap = m.snapshot()
    assert snap["errors"] == 15  # total count keeps climbing
    assert len(snap["recent_errors"]) == 10  # but only last 10 kept
    assert snap["recent_errors"][-1] == "err14"


def test_reflections_and_consolidations_counted():
    m = HeartbeatMetrics(monotonic=_fake_clock())
    m.record_reflection()
    m.record_reflection()
    m.record_consolidation()
    snap = m.snapshot()
    assert snap["reflections"] == 2
    assert snap["consolidations"] == 1


def test_rss_mb_is_reported():
    # Works via psutil or the stdlib resource fallback; must be a positive number.
    snap = HeartbeatMetrics(monotonic=_fake_clock()).snapshot()
    assert snap["rss_mb"] is None or snap["rss_mb"] > 0


def test_snapshot_is_json_serializable():
    import json
    m = HeartbeatMetrics(monotonic=_fake_clock())
    m.record_cycle(0.1)
    m.record_action("experiment", {"result": {"success": True}})
    json.dumps(m.snapshot())  # must not raise


# ── Heartbeat.status_snapshot integration ────────────────────────────────────

def test_heartbeat_status_snapshot_merges_context_and_metrics():
    hb = Heartbeat.__new__(Heartbeat)
    hb.metrics = HeartbeatMetrics(monotonic=_fake_clock())
    hb.metrics.record_cycle(0.2)
    hb._running = True
    hb._current_interval = 30
    hb.ctx = CognitiveContext()
    hb.ctx.state = CognitiveState.THINKING
    hb.ctx.cycle_number = 7
    hb.ctx.current_goal = "investigate prime gaps"
    hb.ctx.current_focus = "twin primes"

    snap = hb.status_snapshot()
    # metrics fields present
    assert snap["cycles"] == 1
    # context fields merged in
    assert snap["running"] is True
    assert snap["state"] == "thinking"
    assert snap["cycle_number"] == 7
    assert snap["current_goal"] == "investigate prime gaps"
    assert snap["current_interval_seconds"] == 30
    import json
    json.dumps(snap)  # JSON-serializable
