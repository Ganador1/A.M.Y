#!/usr/bin/env python3
"""Hermetic tests for the web_sensor async-I/O fix (2026-06-28 re-review).

The arXiv/PubMed/Semantic Scholar/fetch_page methods used blocking
urllib.request.urlopen directly inside async methods, stalling the event loop.
They now route through _urlopen_bytes (asyncio.to_thread). We mock that helper
so the tests are network-free and also confirm the loop is not blocked.
"""
import asyncio
import json

import pytest

import senses.web_sensor as ws
from senses.web_sensor import WebSensor


ARXIV_XML = b"""<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>A Test Paper</title>
    <summary>About prime gaps.</summary>
    <published>2026-01-01T00:00:00Z</published>
    <id>http://arxiv.org/abs/1234.5678</id>
  </entry>
</feed>"""


async def test_arxiv_search_parses_without_blocking(monkeypatch):
    async def fake(req, timeout=30):
        return ARXIV_XML
    monkeypatch.setattr(ws, "_urlopen_bytes", fake)
    # Disable rate-limit sleeps for the test.
    monkeypatch.setattr(ws, "_rate_limit", lambda source: asyncio.sleep(0))

    s = WebSensor({"max_papers_per_search": 5})
    out = await s._search_arxiv("prime gaps")
    assert len(out) == 1
    assert out[0]["title"] == "A Test Paper"
    assert out[0]["source"] == "arxiv"


async def test_pubmed_search_uses_real_descriptive_field(monkeypatch):
    esearch = json.dumps({"esearchresult": {"idlist": ["42"]}}).encode()
    esummary = json.dumps({"result": {"42": {
        "title": "Some Biomedical Title",
        "sorttitle": "some biomedical title",  # the WRONG field the bug used
        "source": "Nature",
        "pubdate": "2026 Jan",
    }}}).encode()
    calls = iter([esearch, esummary])

    async def fake(url, timeout=30):
        return next(calls)
    monkeypatch.setattr(ws, "_urlopen_bytes", fake)
    monkeypatch.setattr(ws, "_rate_limit", lambda source: asyncio.sleep(0))

    s = WebSensor({"max_papers_per_search": 5})
    out = await s._search_pubmed("cancer")
    assert len(out) == 1
    # summary must NOT be the lowercased sorttitle key.
    assert out[0]["summary"] != "some biomedical title"
    assert "Nature" in out[0]["summary"]
    assert out[0]["title"] == "Some Biomedical Title"


async def test_semantic_scholar_parses(monkeypatch):
    payload = json.dumps({"data": [
        {"title": "SS Paper", "abstract": "x" * 600, "year": 2025, "url": "http://x"}
    ]}).encode()

    async def fake(req, timeout=30):
        return payload
    monkeypatch.setattr(ws, "_urlopen_bytes", fake)
    monkeypatch.setattr(ws, "_rate_limit", lambda source: asyncio.sleep(0))

    s = WebSensor({"max_papers_per_search": 5})
    out = await s._search_semantic_scholar("q")
    assert out[0]["title"] == "SS Paper"
    assert len(out[0]["summary"]) == 500  # truncated


async def test_urlopen_bytes_runs_off_the_event_loop(monkeypatch):
    # _urlopen_bytes must use a worker thread (to_thread), proven by checking it
    # does not run urllib on the loop thread: we just verify it awaits and works.
    import threading
    loop_thread = threading.current_thread().name
    seen = {}

    def fake_urlopen(req, timeout=30):
        class _R:
            def __enter__(self_): return self_
            def __exit__(self_, *a): return False
            def read(self_):
                seen["thread"] = threading.current_thread().name
                return b"ok"
        return _R()

    import urllib.request
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    out = await ws._urlopen_bytes("http://x")
    assert out == b"ok"
    # The blocking read ran in a different (worker) thread, not the loop thread.
    assert seen["thread"] != loop_thread
