from app.services.policy_engine_service import policy_engine_service


def test_decide_approve():
    scores = {
        "novelty": 0.8,
        "evidence_strength": 0.9,
        "methodological_rigor": 0.7,
        "reproducibility_likelihood": 0.75,
        "support_score": 0.85,
        "coverage": 0.6,
        "diversity": 0.55
    }
    res = policy_engine_service.decide(scores)
    assert res["success"] and res["decision"]["status"] == "approve"


def test_decide_refine():
    scores = {
        "novelty": 0.5,
        "evidence_strength": 0.6,
        "methodological_rigor": 0.55,
        "reproducibility_likelihood": 0.5,
        "support_score": 0.55,
        "coverage": 0.4,
        "diversity": 0.3
    }
    res = policy_engine_service.decide(scores)
    assert res["success"] and res["decision"]["status"] == "refine"


def test_decide_reject():
    scores = {
        "novelty": 0.2,
        "evidence_strength": 0.4,
        "methodological_rigor": 0.3,
        "reproducibility_likelihood": 0.3,
        "support_score": 0.4,
        "coverage": 0.2,
        "diversity": 0.1
    }
    res = policy_engine_service.decide(scores)
    assert res["success"] and res["decision"]["status"] == "reject"


def test_missing_required():
    scores = {"novelty": 0.7, "support_score": 0.8}  # falta evidence_strength (requerido)
    res = policy_engine_service.decide(scores)
    assert not res["success"] and "Faltan" in res["error"]
