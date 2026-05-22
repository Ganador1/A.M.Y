from app.mathlab.conjectures.evidence_ratio import EvidenceRatioEngine


def test_goldbach_ratio_small_range():
    eng = EvidenceRatioEngine(lower=4, upper=50)
    res = eng.compute({"type": "goldbach"})
    assert res["conjecture"] == "goldbach"
    assert res["evaluated"] > 0
    assert 0.0 <= res["evidence_ratio"] <= 1.0


def test_sum_two_squares_ratio_small_range():
    eng = EvidenceRatioEngine(lower=1, upper=100)
    res = eng.compute({"type": "sum_two_squares"})
    assert res["conjecture"] == "sum_two_squares"
    assert res["evaluated"] > 0
    assert 0.0 <= res["evidence_ratio"] <= 1.0


