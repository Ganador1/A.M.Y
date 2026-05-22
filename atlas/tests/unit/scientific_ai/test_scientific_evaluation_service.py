from app.services.scientific_evaluation_service import scientific_evaluation_service, EvaluationInput


def test_evaluation_basic_structure():
    data = EvaluationInput(novelty_score=0.8, evidence_strength=0.6, stability_score=0.7, text="Random control statistical baseline test")
    result = scientific_evaluation_service.evaluate(data)
    assert set(result.keys()) == {"formula_version", "components", "composite_score", "explanation"}
    comps = result["components"]
    for key in ["novelty", "evidence", "robustness", "methodological_rigor", "reproducibility"]:
        assert key in comps
        assert 0.0 <= comps[key] <= 1.0
    assert 0.0 <= result["composite_score"] <= 1.0


def test_evaluation_determinism():
    data = EvaluationInput(novelty_score=0.3, evidence_strength=0.9, stability_score=0.5, text="baseline test")
    r1 = scientific_evaluation_service.evaluate(data)
    r2 = scientific_evaluation_service.evaluate(data)
    assert r1 == r2


def test_methodological_rigor_heuristic_scaling():
    low = scientific_evaluation_service.evaluate(EvaluationInput(text="simple"))['components']['methodological_rigor']
    high = scientific_evaluation_service.evaluate(EvaluationInput(text="control random statistical ablation sensitivity baseline"))['components']['methodological_rigor']
    assert high >= low
    assert high <= 1.0
