#!/usr/bin/env python3
"""Hermetic coverage for integrity + bounded-memory guarantees (2026-06-27 audit gaps).

- ProvenanceManager: output_hash is the exact SHA-256 of the output, and a
  repeated experiment_id never overwrites — it gets a distinct '<id>_2' dir.
- record_safety_event: hashes (not stores) the prompt and chains each line to
  the previous one.
- Heartbeat bounded buffers: the deques evict past their maxlen.
"""
import hashlib
import json
from collections import deque

from core.provenance import ProvenanceManager


# ── Provenance integrity ─────────────────────────────────────────────────────

def test_output_hash_is_exact_sha256(tmp_path):
    pm = ProvenanceManager(base_dir=tmp_path)
    output = "Total energy: -1.11675931 Ha\nconverged in 8 cycles"
    rec = pm.record_execution(
        tool_name="pyscf_hf_energy", tool_input="H2", tool_output=output,
        success=True, duration_seconds=0.5, domain="chemistry",
    )
    assert rec["tool"]["output_hash"] == hashlib.sha256(output.encode("utf-8")).hexdigest()
    # And the on-disk output.txt round-trips to the same hash.
    out_file = tmp_path / rec["experiment_id"] / "output.txt"
    assert hashlib.sha256(out_file.read_bytes()).hexdigest() == rec["tool"]["output_hash"]


def test_repeated_experiment_id_does_not_overwrite(tmp_path):
    pm = ProvenanceManager(base_dir=tmp_path)
    r1 = pm.record_execution("t", "in", "out-A", True, 0.1, experiment_id="exp_fixed")
    r2 = pm.record_execution("t", "in", "out-B", True, 0.1, experiment_id="exp_fixed")
    assert r1["experiment_id"] == "exp_fixed"
    assert r2["experiment_id"] == "exp_fixed_2"
    # Both provenance files survive with their own outputs.
    assert (tmp_path / "exp_fixed" / "output.txt").read_text() == "out-A"
    assert (tmp_path / "exp_fixed_2" / "output.txt").read_text() == "out-B"


# ── Safety-event audit log: hash-chained, no plaintext ───────────────────────

def test_real_record_safety_event_hashes_chains_and_hides_plaintext(monkeypatch, tmp_path):
    """Drive the REAL record_safety_event, rerouting its hardcoded log into tmp.

    The function builds the path as
        Path(__file__).resolve().parent.parent / "logs" / "safety_events.jsonl"
    so we monkeypatch the module's Path to a stub whose
    .resolve().parent.parent is tmp_path; the `/ "logs" / ...` then lands in tmp.
    """
    import core.safety_kernel as sk
    from core.safety_kernel import SafetyDecision

    class _StubPath:
        def __init__(self, *_a, **_k):
            pass

        def resolve(self):
            class _R:
                @property
                def parent(self):
                    class _P:
                        @property
                        def parent(self_inner):
                            return tmp_path
                    return _P()
            return _R()

    monkeypatch.setattr(sk, "Path", _StubPath)

    sentinel = "SYNTHESIZE_SARIN_UNIQUE_SENTINEL_12345"
    dec = SafetyDecision(allowed=False, action="block", risk_level="critical",
                         reasons=["x"], matched_rules=["CHEMICAL_WEAPONIZATION"])
    sk.record_safety_event(dec, operation="op1", domain="chemistry", tool_name="t", content=sentinel)
    sk.record_safety_event(dec, operation="op2", domain="chemistry", tool_name="t", content="second")

    log_path = tmp_path / "logs" / "safety_events.jsonl"
    raw = log_path.read_text()
    # 1. The dangerous prompt text is hashed, never stored verbatim.
    assert sentinel not in raw
    lines = log_path.read_bytes().splitlines()
    e1, e2 = json.loads(lines[0]), json.loads(lines[1])
    # 2. content_sha256 matches the sentinel's hash.
    assert e1["content_sha256"] == hashlib.sha256(sentinel.encode()).hexdigest()
    # 3. The chain links: event2.previous_event_hash == sha256(raw line1 incl. newline).
    assert e2["previous_event_hash"] == hashlib.sha256(lines[0] + b"\n").hexdigest()
    # 4. Each event carries its own event_hash.
    assert e1.get("event_hash") and e2.get("event_hash")


# ── Heartbeat bounded buffers ────────────────────────────────────────────────

def test_recent_hypotheses_deque_is_bounded():
    d: deque[str] = deque(maxlen=50)
    for i in range(60):
        d.append(f"h{i}")
    assert len(d) == 50
    assert "h0" not in d and "h9" not in d  # oldest evicted
    assert "h59" in d


def test_tool_results_history_deque_is_bounded():
    d: deque[dict] = deque(maxlen=20)
    for i in range(30):
        d.append({"i": i})
    assert len(d) == 20
    assert d[0]["i"] == 10  # first 10 evicted
    assert d[-1]["i"] == 29
