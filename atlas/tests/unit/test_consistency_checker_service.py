from app.services.consistency_checker_service import consistency_checker_service


def test_missing_terms_and_contradiction():
    text = "There is no evidence of effect. Later we claim strong evidence appears."
    res = consistency_checker_service.check(text, required_terms=["effect", "control"])
    assert res["issue_count"] >= 2
    assert any(i["type"] == "missing_term" for i in res["issues"])


def test_clean_text_score_high():
    text = "This experiment shows consistent behavior with appropriate control group."
    res = consistency_checker_service.check(text, required_terms=["control"])
    assert res["score"] > 0.8
