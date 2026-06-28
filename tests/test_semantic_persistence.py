#!/usr/bin/env python3
"""Hermetic tests for semantic-memory persistence fixes (2026-06-28 re-review).

Covers: debounced (not per-write) saves, atomic write, flush() on shutdown,
corrupt-file backup instead of silent wipe, evidence-weighted confidence, and
source dedup/cap.
"""
import json

import pytest

from memory.semantic import SemanticMemory


def _cfg(tmp_path, **over):
    cfg = {"knowledge_graph_path": str(tmp_path / "kg.json")}
    cfg.update(over)
    return cfg


# ── Debounced + atomic + flush ───────────────────────────────────────────────

async def test_add_fact_debounces_disk_writes(tmp_path):
    # The first add persists promptly (so an early crash loses nothing); rapid
    # subsequent adds within the interval are debounced and only land on flush().
    m = SemanticMemory(_cfg(tmp_path, knowledge_graph_save_interval=999))
    path = tmp_path / "kg.json"
    await m.add_fact("a", "b", "c", 0.8, "s1")  # first save: immediate
    data = json.loads(path.read_text())
    assert set(data["facts"].keys()) == {"a|b|c"}
    await m.add_fact("d", "e", "f", 0.8, "s1")  # within interval -> debounced
    data = json.loads(path.read_text())
    assert set(data["facts"].keys()) == {"a|b|c"}, "second add was not debounced"
    await m.flush()  # forces the pending change to disk
    data = json.loads(path.read_text())
    assert set(data["facts"].keys()) == {"a|b|c", "d|e|f"}


async def test_first_save_after_interval_zero_is_immediate(tmp_path):
    m = SemanticMemory(_cfg(tmp_path, knowledge_graph_save_interval=0))
    await m.add_fact("a", "b", "c", 0.8, "s1")
    assert (tmp_path / "kg.json").exists()


async def test_flush_noop_when_clean(tmp_path):
    m = SemanticMemory(_cfg(tmp_path, knowledge_graph_save_interval=0))
    await m.add_fact("a", "b", "c", 0.8, "s1")  # saved immediately
    path = tmp_path / "kg.json"
    mtime = path.stat().st_mtime_ns
    await m.flush()  # nothing dirty -> should not rewrite
    assert path.stat().st_mtime_ns == mtime


async def test_save_is_atomic_no_tmp_left_behind(tmp_path):
    m = SemanticMemory(_cfg(tmp_path, knowledge_graph_save_interval=0))
    await m.add_fact("a", "b", "c", 0.8, "s1")
    assert not (tmp_path / "kg.json.tmp").exists(), "atomic temp file leaked"


async def test_heartbeat_stop_flushes_debounced_facts(tmp_path):
    # The mission-complete shutdown path goes through heartbeat.stop(), NOT
    # amy.stop(); a fact added within the debounce window must still be flushed.
    from core.heartbeat import Heartbeat, CognitiveContext

    m = SemanticMemory(_cfg(tmp_path, knowledge_graph_save_interval=999))
    path = tmp_path / "kg.json"
    await m.add_fact("a", "b", "c", 0.8, "s1")  # first save immediate
    await m.add_fact("d", "e", "f", 0.8, "s1")  # debounced, still in memory only
    assert "d|e|f" not in json.loads(path.read_text())["facts"]

    hb = Heartbeat.__new__(Heartbeat)
    hb.ctx = CognitiveContext()
    hb._running = True
    hb.semantic_memory = m
    await hb.stop()  # must flush

    assert "d|e|f" in json.loads(path.read_text())["facts"], "heartbeat.stop did not flush"


# ── Corrupt load backs up instead of silently wiping ─────────────────────────

def test_corrupt_graph_is_backed_up_not_silently_wiped(tmp_path):
    path = tmp_path / "kg.json"
    path.write_text("{ truncated invalid json", encoding="utf-8")
    m = SemanticMemory(_cfg(tmp_path))
    assert m.facts == {}
    backups = list(tmp_path.glob("kg.json.corrupt.*"))
    assert backups, "corrupt graph was wiped without a backup"
    assert "truncated invalid json" in backups[0].read_text()


# ── Evidence-weighted confidence ─────────────────────────────────────────────

async def test_confidence_is_evidence_weighted_not_naive_average(tmp_path):
    m = SemanticMemory(_cfg(tmp_path, knowledge_graph_save_interval=999))
    # Confirm the fact strongly many times.
    for _ in range(10):
        await m.add_fact("sky", "is", "blue", 0.95, "obs")
    conf_before = m.facts["sky|is|blue"]["confidence"]
    seen_before = m.facts["sky|is|blue"]["times_seen"]
    # One weak re-observation must NOT collapse it the way (old+new)/2 would.
    await m.add_fact("sky", "is", "blue", 0.1, "obs")
    conf_after = m.facts["sky|is|blue"]["confidence"]
    naive = (conf_before + 0.1) / 2
    assert conf_after > naive + 0.1, f"update looks like naive averaging: {conf_after} vs naive {naive}"
    # Expected weighted value: (conf_before*seen + 0.1)/(seen+1)
    expected = (conf_before * seen_before + 0.1) / (seen_before + 1)
    assert conf_after == pytest.approx(expected)


# ── Source dedup + cap ───────────────────────────────────────────────────────

async def test_sources_dedup_same_source(tmp_path):
    m = SemanticMemory(_cfg(tmp_path, knowledge_graph_save_interval=999))
    for _ in range(20):
        await m.add_fact("a", "b", "c", 0.5, "cycle_0")  # same source each time
    assert m.facts["a|b|c"]["sources"] == ["cycle_0"], "duplicate sources accumulated"
    assert m.facts["a|b|c"]["times_seen"] == 20  # still counts the observations


async def test_sources_capped(tmp_path):
    m = SemanticMemory(_cfg(tmp_path, knowledge_graph_save_interval=999, max_sources_per_fact=5))
    for i in range(20):
        await m.add_fact("a", "b", "c", 0.5, f"src_{i}")  # all distinct
    srcs = m.facts["a|b|c"]["sources"]
    assert len(srcs) == 5, f"sources not capped: {len(srcs)}"
    assert srcs[-1] == "src_19"  # kept the most recent
