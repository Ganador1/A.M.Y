#!/usr/bin/env python3
"""Hermetic tests for episodic-memory persistence fixes (2026-06-28 re-review).

Before: __init__ set _buffer=[] / _count=0 and never read the JSONL, so A.M.Y
was amnesiac across restarts and new ids reset to 0, colliding with prior runs.
Now: _load() rehydrates the bounded tail and seeds the id counter past the
highest existing id; writes go through asyncio.to_thread.
"""
import json

import pytest

from memory.episodic import EpisodicMemory


def _cfg(tmp_path, **over):
    cfg = {"episodic_log_path": str(tmp_path / "ep.jsonl")}
    cfg.update(over)
    return cfg


async def test_record_then_reload_restores_history_and_continues_ids(tmp_path):
    cfg = _cfg(tmp_path)
    m1 = EpisodicMemory(cfg)
    await m1.record("experiment", "ran prime gap analysis")
    await m1.record("reflection", "noticed a pattern")
    assert await m1.count() == 2

    # Simulate a restart: a fresh instance on the same path.
    m2 = EpisodicMemory(cfg)
    recent = await m2.get_recent(10)
    assert len(recent) == 2, "buffer was not rehydrated on restart"
    assert recent[-1]["content"] == "noticed a pattern"
    # New ids must continue past the highest existing id (no collision).
    await m2.record("experiment", "third event")
    ids = [e["id"] for e in await m2.get_recent(10)]
    assert ids == sorted(set(ids)), f"ids collided: {ids}"
    assert max(ids) == 2  # 0,1 from m1, then 2 from m2 — not a reset to 0


async def test_load_seeds_counter_from_max_id(tmp_path):
    path = tmp_path / "ep.jsonl"
    # Pre-seed a log whose ids are non-contiguous; counter must be max+1.
    path.write_text("\n".join(
        json.dumps({"id": i, "timestamp": 1.0, "event_type": "x", "content": f"e{i}", "metadata": {}})
        for i in (0, 1, 5, 9)
    ) + "\n", encoding="utf-8")
    m = EpisodicMemory(_cfg(tmp_path))
    assert await m.count() == 10  # max id 9 -> next is 10
    await m.record("x", "new")
    assert (await m.get_recent(1))[0]["id"] == 10


async def test_load_tolerates_corrupt_lines(tmp_path):
    path = tmp_path / "ep.jsonl"
    path.write_text(
        json.dumps({"id": 0, "timestamp": 1.0, "event_type": "x", "content": "ok", "metadata": {}}) + "\n"
        + "{ this is a torn half-written line\n"
        + json.dumps({"id": 1, "timestamp": 1.0, "event_type": "x", "content": "ok2", "metadata": {}}) + "\n",
        encoding="utf-8",
    )
    m = EpisodicMemory(_cfg(tmp_path))
    recent = await m.get_recent(10)
    # The two valid lines survive; the corrupt one is skipped, not fatal.
    assert [e["content"] for e in recent] == ["ok", "ok2"]
    assert await m.count() == 2


async def test_load_bounded_to_max_before_consolidation(tmp_path):
    path = tmp_path / "ep.jsonl"
    with open(path, "w", encoding="utf-8") as f:
        for i in range(50):
            f.write(json.dumps({"id": i, "timestamp": 1.0, "event_type": "x",
                                "content": f"e{i}", "metadata": {}}) + "\n")
    m = EpisodicMemory(_cfg(tmp_path, max_episodic_before_consolidation=10))
    recent = await m.get_recent(1000)
    assert len(recent) == 10, "buffer hydration was not bounded"
    assert recent[-1]["content"] == "e49"  # kept the tail
    assert await m.count() == 50  # counter still seeded from the true max id
