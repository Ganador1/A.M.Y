from app.autonomous.evaluation.novelty_assessor import NoveltyAssessor


def test_assess_returns_expected_keys():
    assessor = NoveltyAssessor()
    result = assessor.assess([0.2, 0.4, 0.6])
    assert set(result.keys()) == {"novelty_score", "centroid_distance", "density_proxy"}


def test_empty_embedding():
    assessor = NoveltyAssessor()
    result = assessor.assess([])
    assert result["novelty_score"] == 0.0


def test_novelty_score_bounds():
    assessor = NoveltyAssessor()
    for emb in ([0.0, 0.0, 0.0], [10.0, -10.0, 5.0], [0.5, 0.5, 0.5]):
        r = assessor.assess(emb)
        assert 0.0 <= r["novelty_score"] <= 1.0


def test_variance_influences_density():
    assessor = NoveltyAssessor()
    low_var = assessor.assess([0.5, 0.51, 0.49])
    high_var = assessor.assess([0.0, 1.0, -1.0])
    assert high_var["density_proxy"] >= low_var["density_proxy"]
