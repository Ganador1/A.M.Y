from fastapi import APIRouter
from typing import List, Dict, Any, Optional
from app.services.paper_analysis_service import paper_analysis_service
from app.services.peer_review_service import peer_review_service
from app.services.literature_search import LiteratureSearchService

router = APIRouter(prefix="/papers", tags=["papers"])
_lit = LiteratureSearchService()

@router.post("/analyze")
def analyze(papers: List[Dict[str, Any]], hypothesis_variables: Optional[List[str]] = None):
    return paper_analysis_service.analyze_papers(papers, hypothesis_variables)

@router.post("/analyze-from-search")
def analyze_from_search(query: str, domain: str = "", max_results: int = 10, hypothesis_variables: Optional[List[str]] = None):
    # reutiliza servicio existente de búsqueda
    res = _lit.search_offline({"query": query, "domain": domain, "max_results": max_results})
    papers = [p for p in res.get("papers", [])]
    return paper_analysis_service.analyze_papers(papers, hypothesis_variables)

@router.post("/peer-review")
def peer_review(enriched_papers: List[Dict[str, Any]]):
    return peer_review_service.review(enriched_papers)
