from app.services.paper_analysis_service import paper_analysis_service


def test_claim_relation_mapping_basic():
    # Crear hipótesis (simulada) sólo para variables; evaluación forzará persistencia base
    hyp_id = "HYP-MAP-001"
    # Generar algunos claims persistidos a través de análisis
    papers = [
        {
            "paper_id": "P-MAP-1",
            "title": "Stability and Robust Method Advances",
            "abstract": "We show that our robust method improves stability significantly in control scenarios.",
        },
        {
            "paper_id": "P-MAP-2",
            "title": "Ablation of Randomized Baseline",
            "abstract": "Results indicate that the randomized baseline method enhances robustness.",
        },
    ]
    analysis = paper_analysis_service.analyze_papers(papers, hypothesis_variables=["robust", "stability", "method"])
    assert analysis["count"] == 2
    # Map claims -> hypothesis
    mapping_res = paper_analysis_service.map_claims_to_hypothesis(hypothesis_id=hyp_id, hypothesis_variables=["robust", "stability", "method"])
    assert mapping_res["success"] is True
    assert mapping_res["created_relations"] >= 1
