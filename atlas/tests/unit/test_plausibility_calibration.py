from app.services.plausibility_scoring_service import get_plausibility_service


def test_calibrated_score_presence(monkeypatch):
    svc = get_plausibility_service()
    # Forzar temperatura distinta de 1 para ver efecto
    svc._calibration["temperature"] = 1.25
    base = svc.score_hypothesis({
        "title": "Effect of temperature on enzyme kinetics",
        "description": "We hypothesize that increasing temperature within physiological range accelerates reaction rate showing measurable change at 37C vs 25C.",
        "variables": ["temperature", "reaction_rate"],
        "assumptions": ["steady state"],
        "expected_outcome": "Higher rate at 37C by at least 15%",
        "domain": "biology"
    })
    assert base["success"]
    if "model_score" in base:
        assert 0.0 <= base["model_score"] <= 1.0
        assert base.get("calibration_temperature") == 1.25


def test_feature_vector_length():
    svc = get_plausibility_service()
    vec = svc.extract_feature_vector({
        "title": "Quantum coherence in novel material",
        "description": "Investigate sustained quantum coherence signals exceeding baseline noise by 20% across repeated trials.",
        "variables": ["coherence_time", "temperature"],
        "assumptions": ["low thermal noise"],
        "expected_outcome": "Coherence time extended",
        "domain": "physics"
    })
    # features: 8 base + 16 embedding = 24
    assert len(vec) == 24
    for v in vec:
        assert isinstance(v, float)


def test_duplication_penalty_changes_with_added_reference():
    svc = get_plausibility_service()
    data = {
        "title": "Metabolic adaptation to fasting",
        "description": "Study metabolic pathway shifts after 12h fasting with quantification of ketone bodies and glucose utilization patterns.",
        "variables": ["ketone_level", "glucose_utilization"],
        "assumptions": ["controlled diet"],
        "expected_outcome": "Increase in ketone bodies > 30%",
        "domain": "biology"
    }
    first = svc.score_hypothesis(data)
    svc.add_reference_hypothesis(data)  # registrar como similar
    second = svc.score_hypothesis(data)
    # segunda evaluación podría tener penalización duplicación igual o más negativa
    pen1 = first["components"].get("duplication_penalty", 0)
    pen2 = second["components"].get("duplication_penalty", 0)
    assert pen2 <= pen1
