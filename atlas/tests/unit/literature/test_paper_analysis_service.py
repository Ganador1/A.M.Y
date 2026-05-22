from app.services.paper_analysis_service import paper_analysis_service
from app.services.peer_review_service import peer_review_service


def test_paper_analysis_basic():
    papers = [
        {"paper_id": "p1", "title": "A Study", "abstract": "We demonstrate that variable X improves Y significantly.", "citations": 10},
        {"paper_id": "p2", "title": "Another Study", "abstract": "Results indicate that X has no effect.", "citations": 2},
    ]
    enriched = paper_analysis_service.analyze_papers(papers, hypothesis_variables=["X", "Y"])
    assert enriched["count"] == 2
    assert any(p["coverage_ratio"] > 0 for p in enriched["papers"])


def test_peer_review_stub():
    papers = [
        {"paper_id": "p1", "title": "A Study", "abstract": "We show that control baseline improves robustness."},
    ]
    enriched = paper_analysis_service.analyze_papers(papers)
    reviewed = peer_review_service.review(enriched["papers"])
    assert reviewed["count"] == 1
    assert reviewed["papers"][0]["consensus_score"] > 0
