"""Tests unitarios para ingestion.utils y contratos básicos de BaseFetcher."""
import json
from ingestion import utils
from ingestion.base_fetcher import BaseFetcher, FetchBatch


def test_normalize_text_basic():
    assert utils.normalize_text("Hola   mundo\nAI") == "Hola mundo AI"


def test_canonical_id_stability():
    a = utils.canonical_id("Título Ejemplo", 2024)
    b = utils.canonical_id("Título Ejemplo", 2024)
    assert a == b
    assert len(a) == 40  # sha1 hex


def test_retry_call_success_after_failures(tmp_path):
    attempts = {"n": 0}
    def flaky():
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise RuntimeError("fail")
        return 42
    result = utils.retry_call(flaky, retries=5, base_backoff=0.01)
    assert result == 42
    assert attempts["n"] == 3


def test_state_roundtrip(tmp_path, monkeypatch):
    # Redirigir STATE_FILE a carpeta temporal para no ensuciar repo
    monkeypatch.setattr(utils, "STATE_FILE", tmp_path / "state.json")
    s = {"cursor": 10}
    utils.save_state(s)
    loaded = utils.load_state()
    assert loaded == s


def test_log_event_and_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(utils, "LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(utils, "CACHE_DIR", tmp_path / "cache")
    utils.log_event("semantic", "start", page=1)
    assert any(p.name.startswith("ingestion_") for p in (tmp_path / "logs").iterdir())
    utils.write_cache("semantic", "page1", {"ok": True})
    day = next((tmp_path / "cache" / "semantic").iterdir())
    cache_file = day / "page1.json"
    data = json.loads(cache_file.read_text(encoding="utf-8"))
    assert data == {"ok": True}


class DummyFetcher(BaseFetcher):
    source_name = "dummy"
    def __init__(self):
        self.calls = 0
    def fetch_batch(self, state=None):  # type: ignore[override]
        self.calls += 1
        if state is None:
            return FetchBatch([{ "id": 1 }], {"cursor": 1}, 1)
        if state.get("cursor") == 1:
            return FetchBatch([{ "id": 2 }], None, 1)
        return FetchBatch([], None, 0)


def test_dummy_fetcher_sequence():
    f = DummyFetcher()
    b1 = f.fetch_batch()
    assert b1.items and b1.next_state == {"cursor": 1}
    b2 = f.fetch_batch(b1.next_state)
    assert b2.items[0]["id"] == 2 and b2.next_state is None
    assert f.calls == 2
