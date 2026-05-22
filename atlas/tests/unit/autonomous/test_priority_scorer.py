import math

import pytest

from app.autonomous.core.priority_scoring import PriorityScorer, WeightConfig


@pytest.fixture
def scorer():
    return PriorityScorer()


def test_compute_score_default_weights(scorer):
    item = {
        "importance": 0.8,
        "proveability": 0.6,
        "novelty": 0.5,
        "information_gain": 0.7,
        "estimated_cost": 0.2,
    }

    score = scorer.compute_score(item)

    expected = 0.8 + 0.6 + 0.5 + 0.7 - 0.2
    assert score == pytest.approx(expected, rel=1e-5)


def test_compute_score_falls_back_to_novelty_score(scorer):
    item = {
        "importance": 0.5,
        "proveability": 0.4,
        "novelty_score": 0.9,
        "information_gain": 0.3,
        "estimated_cost": 0.1,
    }

    score = scorer.compute_score(item)
    assert score == pytest.approx(0.5 + 0.4 + 0.9 + 0.3 - 0.1, rel=1e-6)


def test_rank_orders_items_descending(scorer):
    items = [
        {"importance": 0.1, "novelty": 0.1, "information_gain": 0.1, "proveability": 0.1, "estimated_cost": 0.1},
        {"importance": 0.9, "novelty": 0.9, "information_gain": 0.8, "proveability": 0.7, "estimated_cost": 0.2},
        {"importance": 0.3, "novelty": 0.4, "information_gain": 0.2, "proveability": 0.5, "estimated_cost": 0.1},
    ]

    ranked = scorer.rank(items)

    assert ranked[0]["importance"] == 0.9
    assert ranked[-1]["importance"] == 0.1
    assert all("score" in item for item in ranked)


def test_update_weights_validates_keys():
    config = WeightConfig()
    scorer = PriorityScorer(config)

    scorer.update_weights(importance=2.0, novelty=1.5, unused=99)

    assert config.importance == 2.0
    assert config.novelty == 1.5
    assert not hasattr(config, "unused")


def test_compute_score_handles_non_numeric_inputs(scorer):
    item = {"importance": "0.5", "proveability": 0.4, "novelty": 0.3, "information_gain": 0.2, "estimated_cost": 0.1}

    score = scorer.compute_score(item)
    assert score == pytest.approx(0.5 + 0.4 + 0.3 + 0.2 - 0.1, rel=1e-6)


def test_rank_gracefully_handles_errors():
    scorer = PriorityScorer()
    items = [
        {"importance": 0.5, "novelty": 0.6, "information_gain": 0.4, "proveability": 0.7, "estimated_cost": 0.2},
        {"importance": "bad"},
    ]

    ranked = scorer.rank(items)
    assert math.isnan(ranked[-1]["score"])
