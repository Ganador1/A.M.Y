#!/usr/bin/env python3
"""Hermetic tests for embedding-backed recall (2026-06-28 re-review, L item).

A fake (deterministic, offline) embed function stands in for the Ollama client,
so these tests need no network. They cover SemanticIndex add/query + fail-soft
behavior, and SkillLibrary semantic retrieval with keyword fallback.
"""
import pytest

# chromadb is an optional dependency (only needed for embedding recall); skip
# this whole module where it isn't installed (e.g. the minimal-deps CI lane).
pytest.importorskip("chromadb")

from memory.semantic_index import SemanticIndex
from skills.library import SkillLibrary


# A tiny deterministic "embedder": map keywords to orthogonal-ish vectors so
# semantically-grouped texts land near each other without a real model.
_AXES = ["plot", "prime", "web", "chem"]


def _vec_for(text: str) -> list[float]:
    t = text.lower()
    v = [float(t.count(a) + (1.0 if a in t else 0.0)) for a in _AXES]
    # add a tiny base so an all-zero text still yields a usable vector
    return v if any(v) else [0.01, 0.01, 0.01, 0.01]


async def _fake_embed(text: str):
    return _vec_for(text)


# ── SemanticIndex ────────────────────────────────────────────────────────────

async def test_semantic_index_add_and_query_ranks_by_meaning():
    idx = SemanticIndex(_fake_embed, name="t_meaning")
    await idx.add("plotter", "make a chart and plot the data")
    await idx.add("primes", "compute prime numbers and prime gaps")
    hits = await idx.query("plot a graph", n_results=2)
    assert hits, "no hits returned"
    assert hits[0]["id"] == "plotter"  # plotting query → plotting skill first


async def test_semantic_index_empty_when_no_docs():
    idx = SemanticIndex(_fake_embed, name="t_empty")
    assert await idx.query("anything") == []


async def test_semantic_index_failsoft_on_embed_error():
    async def boom(text):
        raise RuntimeError("embed service down")
    idx = SemanticIndex(boom, name="t_fail")
    # add and query must not raise; both degrade to no-op / empty.
    assert await idx.add("x", "doc") is False
    assert await idx.query("q") == []


# ── SkillLibrary with the index ──────────────────────────────────────────────

async def test_skill_library_semantic_retrieve(monkeypatch):
    idx = SemanticIndex(_fake_embed, name="t_skills")
    lib = SkillLibrary({"library_path": ":memory:"}, semantic_index=idx)
    await lib.register_skill("make_plot", "render a chart from data points", "code")
    await lib.register_skill("find_primes", "sieve of eratosthenes", "code")

    # A query with NO exact token overlap with "make_plot"/"render a chart"
    # but the same meaning axis ('plot') — keyword match would miss it.
    hits = await lib.retrieve("plot")
    assert hits, "semantic retrieve returned nothing"
    assert hits[0]["name"] == "make_plot"


async def test_skill_library_falls_back_to_keyword_when_no_index():
    lib = SkillLibrary({"library_path": ":memory:"})  # no index
    await lib.register_skill("make_plot", "render a chart from data points", "code")
    hits = await lib.retrieve("render data")  # shares tokens with description
    assert any(h["name"] == "make_plot" for h in hits)


async def test_skill_library_falls_back_when_index_returns_nothing():
    # Index whose embedder fails → query() returns [] → keyword fallback runs.
    async def boom(text):
        raise RuntimeError("down")
    idx = SemanticIndex(boom, name="t_fb")
    lib = SkillLibrary({"library_path": ":memory:"}, semantic_index=idx)
    await lib.register_skill("make_plot", "render a chart from data points", "code")
    hits = await lib.retrieve("render chart")
    assert any(h["name"] == "make_plot" for h in hits), "keyword fallback did not run"
