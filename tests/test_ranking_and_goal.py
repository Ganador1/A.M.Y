#!/usr/bin/env python3
"""Hermetic tests for the Elo ranking math and mission-goal wiring.

Covers two correctness fixes from the 2026-06-27 audit plus the previously
untested core ranking math:

- run_tournament/select_top_k no longer report a prior tournament's stale
  elo/record when re-ranking an already-ranked pool (the d.update(r.extra)
  clobber); _RESERVED_KEYS keeps computed fields out of extra.
- Elo fundamentals: expected_score logistic, FIDE K-factor steps, determinism,
  zero-sum conservation, INITIAL_ELO, n<2 passthrough, candidate > control.
- Heartbeat.ctx.current_goal is synced from the goal stack's mission instead
  of staying "".
"""
import pytest

from cognition.ranking_agent import (
    INITIAL_ELO,
    expected_score,
    _k_factor,
    run_tournament,
    select_top_k,
)


# ── Elo fundamentals (coverage gap: zero pytest coverage before) ─────────────

def test_expected_score_equal_ratings_is_half():
    assert expected_score(1200, 1200) == pytest.approx(0.5)


def test_expected_score_monotonic_in_gap():
    assert expected_score(1400, 1200) > 0.5
    assert expected_score(1000, 1200) < 0.5


def test_k_factor_fide_steps():
    assert _k_factor(4) == 40
    assert _k_factor(5) == 20
    assert _k_factor(14) == 20
    assert _k_factor(15) == 10


def test_tournament_is_deterministic_for_fixed_seed():
    cands = [
        {"hypothesis": "A control", "novelty_status": "known_control", "confidence": 0.85},
        {"hypothesis": "B candidate measure test compare", "novelty_status": "candidate_novelty", "confidence": 0.7},
        {"hypothesis": "C observation", "novelty_status": "observation", "confidence": 0.6},
    ]
    r1 = run_tournament([dict(c) for c in cands], rounds=2, seed=42)
    r2 = run_tournament([dict(c) for c in cands], rounds=2, seed=42)
    assert [r.elo for r in r1] == [r.elo for r in r2]
    assert [r.hypothesis for r in r1] == [r.hypothesis for r in r2]


def test_tournament_conserves_total_elo():
    cands = [
        {"hypothesis": f"H{i}", "novelty_status": "observation", "confidence": 0.5}
        for i in range(4)
    ]
    ranked = run_tournament(cands, rounds=2, seed=1)
    total = sum(r.elo for r in ranked)
    # Zero-sum updates: total stays at n * INITIAL_ELO.
    assert total == pytest.approx(len(cands) * INITIAL_ELO, abs=1e-6)


def test_tournament_passthrough_when_fewer_than_two():
    one = [{"hypothesis": "solo", "confidence": 0.5}]
    ranked = run_tournament(one, rounds=2, seed=1)
    assert len(ranked) == 1
    assert ranked[0].elo == INITIAL_ELO


def test_candidate_novelty_outranks_known_control():
    cands = [
        {"hypothesis": "Textbook constant, no test", "novelty_status": "known_control", "confidence": 0.5},
        {"hypothesis": "Novel claim; testable via measuring and comparing against baseline",
         "novelty_status": "candidate_novelty", "confidence": 0.8},
    ]
    top = select_top_k(cands, k=1, seed=42)[0]
    assert top["novelty_status"] == "candidate_novelty"


# ── select_top_k must report FRESH elo, not stale carried-in values ──────────

def test_select_top_k_ignores_stale_carried_elo():
    # Simulate re-ranking dicts that already carry elo/record from a prior run.
    cands = [
        {"hypothesis": "Strong; testable via measuring", "novelty_status": "candidate_novelty",
         "confidence": 0.9, "elo": 9999.9, "tournament_record": "99W-0L-0D"},
        {"hypothesis": "Weak control", "novelty_status": "known_control",
         "confidence": 0.4, "elo": -123.4, "tournament_record": "0W-99L-0D"},
    ]
    out = select_top_k(cands, k=2, seed=42)
    elos = {d["hypothesis"]: d["elo"] for d in out}
    # The stale 9999.9 / -123.4 must NOT survive — fresh values are near 1200.
    assert all(1000 < e < 1400 for e in elos.values()), elos
    recs = {d["tournament_record"] for d in out}
    assert "99W-0L-0D" not in recs and "0W-99L-0D" not in recs


# ── Heartbeat current_goal sync ──────────────────────────────────────────────

async def test_heartbeat_syncs_current_goal_from_mission():
    from core.heartbeat import Heartbeat, CognitiveContext
    from cognition.goal_stack import GoalStack

    hb = Heartbeat.__new__(Heartbeat)
    hb.ctx = CognitiveContext()
    hb.goal_stack = GoalStack({})
    await hb.goal_stack.set_mission(goal="Investigate prime gaps", description="desc")

    assert hb.ctx.current_goal == ""
    hb._sync_current_goal_from_mission()
    assert hb.ctx.current_goal == "Investigate prime gaps"


def test_sync_current_goal_is_noop_without_mission():
    from core.heartbeat import Heartbeat, CognitiveContext
    from cognition.goal_stack import GoalStack

    hb = Heartbeat.__new__(Heartbeat)
    hb.ctx = CognitiveContext()
    hb.goal_stack = GoalStack({})
    hb._sync_current_goal_from_mission()  # no mission set
    assert hb.ctx.current_goal == ""
