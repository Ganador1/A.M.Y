#!/usr/bin/env python3
"""Hermetic tests for the rapid-round fixes (curiosity, skills, ollama client).

From the 2026-06-28 re-review: curiosity _explored_topics grows unbounded and
the epistemic_weight knob was dead; skills register_skill silently reset usage
stats; ollama embed had no failover and 429 Retry-After was ignored.
"""
import time

import pytest

from cognition.curiosity import CuriosityModule
from skills.library import SkillLibrary
from core.ollama_client import OllamaCloudClient


# ── Curiosity: bounded explored-topics + working epistemic_weight ────────────

class _FakeWorldModel:
    average_surprise = 0.0
    async def get_uncertainty_map(self):
        return []


async def test_explored_topics_evicted_below_floor():
    c = CuriosityModule({"novelty_decay": 0.5, "novelty_floor": 0.05})
    c._explored_topics = {"old": 0.06, "fresh": 1.0}
    await c.get_signal(_FakeWorldModel(), None)
    # 0.06 * 0.5 = 0.03 < floor -> evicted; 1.0 * 0.5 = 0.5 kept.
    assert "old" not in c._explored_topics
    assert "fresh" in c._explored_topics


async def test_explored_topics_bounded_by_max():
    c = CuriosityModule({"novelty_decay": 1.0, "novelty_floor": 0.0, "max_explored_topics": 10})
    c._explored_topics = {f"t{i}": (i + 1) / 100 for i in range(50)}
    await c.get_signal(_FakeWorldModel(), None)
    assert len(c._explored_topics) <= 10


async def test_epistemic_weight_actually_affects_signal():
    wm = _FakeWorldModel()
    # With no uncertainties, model_uncertainty = 0.8; novelty/surprise terms = 0
    # (empty topics -> novelty 1.0 actually). Compare two epistemic weights.
    c_hi = CuriosityModule({"epistemic_weight": 0.9})
    c_lo = CuriosityModule({"epistemic_weight": 0.1})
    sig_hi = await c_hi.get_signal(wm, None)
    sig_lo = await c_lo.get_signal(wm, None)
    # Different weights must yield different curiosity levels (knob is live).
    assert sig_hi["level"] != sig_lo["level"]


# ── Skills: re-register preserves usage stats; unknown usage warns ───────────

async def test_register_skill_preserves_usage_stats():
    lib = SkillLibrary({"library_path": ":memory:"})
    await lib.register_skill("s", "does a thing", "print(1)")
    await lib.record_usage("s", success=True)
    await lib.record_usage("s", success=True)
    assert lib.skills["s"]["times_used"] == 2
    # Re-register (e.g. consolidation re-extracts) must NOT wipe the history.
    await lib.register_skill("s", "does a thing v2", "print(2)")
    assert lib.skills["s"]["times_used"] == 2
    assert lib.skills["s"]["success_count"] == 2
    assert lib.skills["s"]["description"] == "does a thing v2"  # metadata updated


async def test_record_usage_unknown_skill_is_noop_not_crash():
    lib = SkillLibrary({"library_path": ":memory:"})
    # Should not raise (and should not create a phantom entry).
    await lib.record_usage("nonexistent", success=True)
    assert "nonexistent" not in lib.skills


# ── Ollama: Retry-After parsing + cooldown honoring + embed failover ─────────

def _client_stub(n_keys=2):
    c = OllamaCloudClient.__new__(OllamaCloudClient)
    c._keys = ["k"] * n_keys
    c._key_failures = {}
    c._cooldown_seconds = 120
    return c


def test_parse_retry_after():
    assert OllamaCloudClient._parse_retry_after("30") == 30.0
    assert OllamaCloudClient._parse_retry_after(None) is None
    assert OllamaCloudClient._parse_retry_after("garbage") is None


def test_record_failure_honors_retry_after():
    c = _client_stub()
    exc = Exception("429")
    exc.retry_after = 300  # server says wait 300s, longer than 120 cooldown
    before = time.time()
    c._record_failure(0, exc)
    # _pick_key compares (now - last_fail) > cooldown; with retry_after the key
    # should remain unavailable until ~300s from now, i.e. last_fail is in the
    # future relative to a plain time.time() failure.
    assert c._key_failures[0] > before  # pushed forward to honor retry_after
    # Effective ready-time = last_fail + cooldown ≈ now + 300.
    ready_in = c._key_failures[0] + c._cooldown_seconds - before
    assert 290 < ready_in < 310


def test_record_failure_default_cooldown_without_retry_after():
    c = _client_stub()
    c._record_failure(0, Exception("boom"))
    # No retry_after -> last_fail ≈ now (standard 120s cooldown applies).
    assert abs(c._key_failures[0] - time.time()) < 2


async def test_embed_fails_over_across_keys(monkeypatch):
    c = _client_stub(n_keys=2)
    from itertools import cycle
    c._key_cycle = cycle(range(2))
    calls = {"n": 0}

    async def fake_do(endpoint, payload, api_key):
        calls["n"] += 1
        if calls["n"] == 1:
            raise Exception("first key down")
        return {"embeddings": [[0.1, 0.2]]}

    monkeypatch.setattr(c, "_do_request", fake_do)
    out = await c.embed("model", "text")
    assert out == [[0.1, 0.2]]
    assert calls["n"] == 2  # it retried the second key
