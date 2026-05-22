from app.services.hypothesis_tournament_service import hypothesis_tournament_service


def test_hypothesis_ranking():
    hyps = [
        {"id": "h1", "scores": {"novelty": 0.9, "evidence_strength": 0.4, "methodological_rigor": 0.7, "reproducibility_likelihood": 0.6}},
        {"id": "h2", "scores": {"novelty": 0.5, "evidence_strength": 0.9, "methodological_rigor": 0.6, "reproducibility_likelihood": 0.6}},
    ]
    res = hypothesis_tournament_service.rank(hyps)
    assert res["count"] == 2
    assert res["ranking"][0]["composite"] >= res["ranking"][1]["composite"]
