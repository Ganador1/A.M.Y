#!/usr/bin/env python3
"""Tests that the self-retrain + meta-review feedback loop is wired into the
live heartbeat (2026-06-29 — closing the 'learns for real' disconnection gap).

Before: SelfRetrainModule + MetaReviewAgent existed but were never instantiated
in amy.py or called by the heartbeat, so neither belief recalibration nor
cross-cycle feedback ran in the autonomous loop. Now _reflect() drives
retrain_world_model and the meta-review feedback reaches the reasoning prompt.
"""
import pytest

from core.heartbeat import Heartbeat, CognitiveContext
from core.metrics import HeartbeatMetrics
from cognition.reasoning import ReasoningEngine
from evolution.self_retrain import SelfRetrainModule


# ── _reflect drives self_retrain.retrain_world_model on the throttle boundary ─

async def test_reflect_runs_self_retrain_on_throttle():
    calls = {"retrain": 0}

    class _StubRetrain:
        async def retrain_world_model(self, wm, ep, sem):
            calls["retrain"] += 1
            return {"type": "world_model", "beliefs_updated": 0}

    class _Reflect:
        async def reflect(self, world_model, goal_stack):
            return None

    hb = Heartbeat.__new__(Heartbeat)
    hb.ctx = CognitiveContext()
    hb.metrics = HeartbeatMetrics()
    hb.reflection = _Reflect()
    hb.world_model = None
    hb.goal_stack = None
    hb.episodic_memory = None
    hb.semantic_memory = None
    hb.procedural_memory = None
    # Disable the consolidation branch (set far in the future).
    hb._consolidator = type("C", (), {"consolidate": staticmethod(lambda: None)})()
    hb._reflections_since_consolidation = 0
    hb._reflections_per_consolidation = 10_000
    # Self-retrain every 2 reflections.
    hb.self_retrain = _StubRetrain()
    hb._reflections_since_retrain = 0
    hb._reflections_per_retrain = 2

    await hb._reflect()
    assert calls["retrain"] == 0, "should not retrain before the throttle"
    await hb._reflect()
    assert calls["retrain"] == 1, "should retrain on the throttle boundary"


async def test_reflect_safe_without_self_retrain():
    # self_retrain=None must be a clean no-op (tests / minimal configs).
    class _Reflect:
        async def reflect(self, world_model, goal_stack):
            return None

    hb = Heartbeat.__new__(Heartbeat)
    hb.ctx = CognitiveContext()
    hb.metrics = HeartbeatMetrics()
    hb.reflection = _Reflect()
    hb.world_model = hb.goal_stack = hb.semantic_memory = None
    hb.procedural_memory = None
    hb._consolidator = type("C", (), {"consolidate": staticmethod(lambda: None)})()
    hb._reflections_since_consolidation = 0
    hb._reflections_per_consolidation = 10_000
    hb.self_retrain = None
    hb._reflections_since_retrain = 0
    hb._reflections_per_retrain = 1
    await hb._reflect()  # must not raise


# ── real SelfRetrainModule: recalibrates belief confidences ──────────────────

async def test_self_retrain_recalibrates_belief_confidence():
    from core.world_model import WorldModel, Belief
    wm = WorldModel.__new__(WorldModel)
    wm.beliefs = {
        "k": Belief(content="k", confidence=0.5, source="x",
                    times_confirmed=9, times_contradicted=1),
    }
    sr = SelfRetrainModule({})
    rec = await sr.retrain_world_model(wm, None, None)
    assert rec and rec["beliefs_updated"] == 1
    # reliability = 9/10 = 0.9; new = 0.5*0.5 + 0.5*0.9 = 0.7
    assert wm.beliefs["k"].confidence == pytest.approx(0.7)


# ── meta-review feedback reaches the reasoning prompt ────────────────────────

def test_meta_review_feedback_appears_in_reasoning_prompt():
    re = ReasoningEngine.__new__(ReasoningEngine)
    msgs = re._build_reasoning_prompt(
        focus={"content": "f", "source": "s", "type": "t"},
        context={
            "current_goal": "g",
            "cycle": 1,
            "meta_review_feedback": "RECURRING: ungrounded numbers — cite provenance.",
        },
        world_model=None,
    )
    user = msgs[-1]["content"]
    assert "Lessons From Prior Reviews" in user
    assert "ungrounded numbers" in user


def test_no_meta_block_when_feedback_empty():
    re = ReasoningEngine.__new__(ReasoningEngine)
    msgs = re._build_reasoning_prompt(
        focus={"content": "f", "source": "s", "type": "t"},
        context={"current_goal": "g", "cycle": 1, "meta_review_feedback": ""},
        world_model=None,
    )
    assert "Lessons From Prior Reviews" not in msgs[-1]["content"]


# ── end-to-end: record_review -> feedback_prompt_suffix accumulates ──────────

def test_record_review_feeds_meta_review_loop():
    sr = SelfRetrainModule({})
    real_issues = {"issues": [
        {"severity": "high", "section": "Discussion",
         "message": "3 of 5 numerical claims in Discussion not found in provenance.",
         "suggestion": "x"},
    ]}
    for _ in range(2):  # recurring across two papers
        sr.record_review(reflection_result=real_issues)
    suffix = sr.feedback_prompt_suffix().lower()
    assert "provenance" in suffix or "numerical claim" in suffix
