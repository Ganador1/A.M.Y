#!/usr/bin/env python3
"""Hermetic tests that memory consolidation actually runs (2026-06-28 re-review).

Before: MemoryConsolidation was defined but never instantiated/called, so the
episodic→procedural skill extraction never ran and procedural memory stayed
permanently empty. Now the heartbeat owns a consolidator and runs it during
reflection.
"""
import pytest

from memory.consolidation import MemoryConsolidation
from memory.episodic import EpisodicMemory
from memory.semantic import SemanticMemory
from memory.procedural import ProceduralMemory
from core.heartbeat import Heartbeat


def _mem(tmp_path):
    ep = EpisodicMemory({"episodic_log_path": str(tmp_path / "ep.jsonl")})
    sem = SemanticMemory({"knowledge_graph_path": str(tmp_path / "kg.json"),
                          "knowledge_graph_save_interval": 999})
    proc = ProceduralMemory({"vector_db_path": str(tmp_path)})
    return ep, sem, proc


async def test_consolidation_extracts_skill_from_successful_experiment(tmp_path):
    ep, sem, proc = _mem(tmp_path)
    # A successful experiment with code → should become a procedural skill.
    await ep.record("experiment", "Test prime sieve",
                    metadata={"code": "print('sieve')", "result": {"success": True}})
    # A failed one → must NOT become a skill.
    await ep.record("experiment", "Broken thing",
                    metadata={"code": "boom", "result": {"success": False}})

    before = await proc.list_skills()
    assert len(before) == 0

    cons = MemoryConsolidation(ep, sem, proc)
    await cons.consolidate()

    after = await proc.list_skills()
    names = [s.get("name", "") for s in after]
    assert len(after) == 1, f"expected exactly the successful skill, got {names}"
    assert any("experiment_" in n for n in names)


async def test_consolidation_extracts_recurring_theme_to_semantic(tmp_path):
    ep, sem, proc = _mem(tmp_path)
    # A word appearing >= 5 times (len > 5) should become a recurring_theme fact.
    for _ in range(6):
        await ep.record("thought", "investigating cosmology cosmology deeply")
    cons = MemoryConsolidation(ep, sem, proc)
    await cons.consolidate()
    themes = [k for k in sem.facts if k.startswith("recurring_theme|")]
    assert any("cosmology" in k for k in themes), f"no recurring theme extracted: {list(sem.facts)}"


def test_heartbeat_wires_a_consolidator():
    # The heartbeat must actually own a consolidator (the bug was that nothing
    # ever constructed/called one).
    hb = Heartbeat.__new__(Heartbeat)
    # Attribute is set in __init__; assert the wiring contract exists in source.
    import inspect
    src = inspect.getsource(Heartbeat.__init__)
    assert "MemoryConsolidation" in src and "_consolidator" in src
    reflect_src = inspect.getsource(Heartbeat._reflect)
    assert "consolidate" in reflect_src, "_reflect does not trigger consolidation"


async def test_heartbeat_reflect_runs_consolidation_after_throttle(tmp_path):
    """Drive the REAL heartbeat _reflect() path (LLM reflection stubbed) and
    confirm it triggers consolidation on the throttle boundary, populating
    procedural memory from a successful experiment — the end-to-end behavior the
    6-min live run was too short to reach (reflection fires every 20 cycles)."""
    ep, sem, proc = _mem(tmp_path)
    await ep.record("experiment", "prime sieve",
                    metadata={"code": "print(1)", "result": {"success": True}})

    hb = Heartbeat.__new__(Heartbeat)
    hb.config = {}
    hb.episodic_memory = ep
    hb.semantic_memory = sem
    hb.procedural_memory = proc
    hb.world_model = None
    hb.goal_stack = None

    # Stub the LLM-backed reflection step; keep the real consolidation wiring.
    class _Reflect:
        async def reflect(self, world_model, goal_stack):
            return None
    hb.reflection = _Reflect()

    from core.heartbeat import CognitiveContext
    from core.metrics import HeartbeatMetrics
    hb.ctx = CognitiveContext()
    hb.metrics = HeartbeatMetrics()  # _reflect records reflection/consolidation metrics
    hb._consolidator = MemoryConsolidation(ep, sem, proc)
    hb._reflections_since_consolidation = 0
    hb._reflections_per_consolidation = 2

    # First reflection: below throttle -> no consolidation yet.
    await hb._reflect()
    assert len(await proc.list_skills()) == 0
    # Second reflection: hits the throttle -> consolidation runs.
    await hb._reflect()
    skills = await proc.list_skills()
    assert len(skills) == 1, "consolidation did not run on the throttle boundary"
    # Metrics recorded both reflections and exactly one consolidation.
    assert hb.metrics.reflections == 2
    assert hb.metrics.consolidations == 1
