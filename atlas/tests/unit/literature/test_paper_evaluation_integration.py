from app.services.paper_analysis_service import paper_analysis_service
from app.services.peer_review_service import peer_review_service
from app.services.scientific_evaluation_service import scientific_evaluation_service, EvaluationInput


def test_paper_analysis_peer_review_evaluation_integration():
    paper = {
        "paper_id": "RND-TEST-001",
        "title": "A Robust Randomized Control Baseline for Novel Statistical Methods",
        "abstract": (
            "We demonstrate that our method achieves significant improvements. "
            "We show that results indicate that the approach is robust and provides significant benefits with p=0.03 across random trials (n=120). "
            "Additional sensitivity analysis and ablation confirm stability."
        ),
        "citations": 12,
    }

    analysis = paper_analysis_service.analyze_papers([paper], hypothesis_variables=["method", "robust", "stability"])
    assert analysis["count"] == 1
    enriched = analysis["papers"][0]

    # coverage_ratio debe ser > 0 dado que variables aparecen en claims
    assert enriched["coverage_ratio"] > 0

    peer = peer_review_service.review(analysis["papers"][0:1])
    assert peer["count"] == 1
    consensus = peer["papers"][0]["consensus_score"]
    assert consensus > 0

    # Evaluación con y sin señales externas para comparar boosting
    base_eval = scientific_evaluation_service.evaluate(EvaluationInput(
        hypothesis_id="HYP-DEMO",
        novelty_score=0.65,
        evidence_strength=0.7,
        stability_score=0.6,
        text=paper["abstract"],
    ))
    boosted_eval = scientific_evaluation_service.evaluate(EvaluationInput(
        hypothesis_id="HYP-DEMO",
        novelty_score=0.65,
        evidence_strength=0.7,
        stability_score=0.6,
        text=paper["abstract"],
        coverage_ratio=enriched["coverage_ratio"],
        peer_review_consensus=consensus,
    ))

    assert boosted_eval["composite_score"] >= base_eval["composite_score"]
    # Asegura que explicación incluye external_signals
    assert "external_signals" in boosted_eval["explanation"]


def test_evaluation_without_external_signals_then_with_boost():
    paper = {
        "paper_id": "RND-TEST-002",
        "title": "Methodological Advances in Randomized Robust Stability Analysis",
        "abstract": (
            "We show that the proposed method provides significant robustness gains. "
            "Results indicate stability improvements confirmed by ablation and sensitivity experiments (n=60)."
        ),
        "citations": 5,
    }
    analysis = paper_analysis_service.analyze_papers([paper], hypothesis_variables=["method", "stability"])
    enriched = analysis["papers"][0]
    peer = peer_review_service.review(analysis["papers"])  # list con enriched
    consensus = peer["papers"][0]["consensus_score"]

    base = scientific_evaluation_service.evaluate(EvaluationInput(
        hypothesis_id="HYP-BASE",
        novelty_score=0.55,
        evidence_strength=0.6,
        stability_score=0.55,
        text=paper["abstract"],
    ))
    boosted = scientific_evaluation_service.evaluate(EvaluationInput(
        hypothesis_id="HYP-BASE",
        novelty_score=0.55,
        evidence_strength=0.6,
        stability_score=0.55,
        text=paper["abstract"],
        coverage_ratio=enriched["coverage_ratio"],
        peer_review_consensus=consensus,
    ))
    assert boosted["composite_score"] >= base["composite_score"]
