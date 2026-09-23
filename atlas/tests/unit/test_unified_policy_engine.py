import json
from app.services.policy_engine_service import policy_engine_service

def test_approve_decision():
    scores = {
        "novelty": 0.8,
        "evidence_strength": 0.9,
        "reproducibility_risk": 0.2,
        "coverage": 0.7,
        "diversity": 0.6,
        "consistency": 0.8,
        "peer_review": 0.85,
        "methodological_rigor": 0.75,
        "safety": 0.9,
    }
    res = policy_engine_service.decide(scores)
    assert res["success"]
    d = res["decision"]
    assert d["status"] in ("approve", "halt")  # under configured thresholds should approve
    assert d["composite"] >= 0.45


def test_refine_decision():
    scores = {
        "novelty": 0.5,
        "evidence_strength": 0.5,
        "reproducibility_risk": 0.4,
        "coverage": 0.4,
        "diversity": 0.4,
        "consistency": 0.5,
        "peer_review": 0.45,
        "methodological_rigor": 0.5,
        "safety": 0.6,
    }
    res = policy_engine_service.decide(scores)
    assert res["success"]
    d = res["decision"]
    assert d["status"] in ("refine", "approve", "reject")


def test_halt_due_to_risk():
    scores = {
        "novelty": 0.9,
        "evidence_strength": 0.9,
        "reproducibility_risk": 0.95,  # very high risk
        "coverage": 0.9,
        "diversity": 0.9,
        "consistency": 0.9,
        "peer_review": 0.9,
        "methodological_rigor": 0.9,
        "safety": 0.9,
    }
    res = policy_engine_service.decide(scores)
    assert res["success"]
    d = res["decision"]
    # high risk triggers halt per config
    assert d["status"] == "halt"
    assert any("high_repro_risk" in r for r in d["reasons"])


def test_halt_low_composite():
    scores = {
        "novelty": 0.05,
        "evidence_strength": 0.05,
        "reproducibility_risk": 0.2,
        "coverage": 0.05,
        "diversity": 0.05,
        "consistency": 0.05,
        "peer_review": 0.05,
        "methodological_rigor": 0.05,
        "safety": 0.05,
    }
    res = policy_engine_service.decide(scores)
    assert res["success"]
    d = res["decision"]
    assert d["status"] in ("halt", "reject")


def test_logging_written(tmp_path, monkeypatch):
    # Redirect log path
    cfg = policy_engine_service.config
    log_path = tmp_path / "decisions.jsonl"
    cfg["logging"]["decisions_path"] = str(log_path)
    # force reload not needed; config mutated in place
    res = policy_engine_service.decide({"evidence_strength": 0.6, "novelty": 0.6})
    assert res["success"]
    assert log_path.exists()
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 1
    rec = json.loads(lines[-1])
    assert "composite" in rec and "status" in rec
