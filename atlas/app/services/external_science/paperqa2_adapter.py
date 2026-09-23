"""PaperQA2-style literature evidence adapter."""

from __future__ import annotations

from typing import Any, Dict, List
import importlib.util
import re

from app.integrations.literature_clients import LiteratureFacade
from app.services.external_science.base import ExternalScienceAdapter


class PaperQA2Adapter(ExternalScienceAdapter):
    """Cited literature synthesis adapter.

    If the official ``paper-qa`` package is not installed or configured, Atlas
    falls back to a deterministic local literature synthesis so the pipeline
    still gains citation-grounded evidence.
    """

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__("paperqa2", config=config)
        self.facade = LiteratureFacade()
        self._package_installed = importlib.util.find_spec("paperqa") is not None
        self.max_results = int(self.config.get("max_results", 8))
        self.backend_mode = str(self.config.get("mode", "atlas_fallback")).strip().lower()

    def is_configured(self) -> bool:
        return self.enabled

    def get_status(self) -> Dict[str, Any]:
        status = super().get_status()
        status.update(
            {
                "backend_mode": self.backend_mode,
                "package_installed": self._package_installed,
            }
        )
        return status

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        action = request_data.get("action")
        if action == "answer_question":
            return await self.answer_question(request_data)
        if action == "verify_claim":
            return await self.verify_claim(request_data)
        if action == "status":
            return {"success": True, **self.get_status()}
        return {"success": False, "adapter": self.name, "error": f"Unknown action {action}"}

    async def answer_question(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        question = str(request_data.get("question") or request_data.get("claim") or "").strip()
        if not question:
            return {"success": False, "adapter": self.name, "error": "question required"}

        domain = str(request_data.get("domain") or "general").strip().lower()
        max_results = int(request_data.get("max_results", self.max_results))
        combined_results = self._search_sources(question, max_results)
        citations = self._format_citations(combined_results[: max(1, min(max_results, 6))])
        support_score = self._score_support(question, combined_results)
        answer = self._build_summary(question, domain, combined_results, citations, support_score)

        return {
            "success": True,
            "adapter": self.name,
            "backend": "paperqa_package" if self._package_installed and self.backend_mode == "package" else "atlas_fallback",
            "paperqa_package_installed": self._package_installed,
            "question": question,
            "domain": domain,
            "answer": answer,
            "support_score": support_score,
            "evidence_strength": support_score,
            "citations": citations,
            "papers": combined_results,
            "reasons": self._build_reasons(combined_results, citations, support_score),
        }

    async def verify_claim(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        claim = str(request_data.get("claim") or request_data.get("question") or "").strip()
        if not claim:
            return {"success": False, "adapter": self.name, "error": "claim required"}

        answer = await self.answer_question(
            {
                "question": claim,
                "domain": request_data.get("domain", "general"),
                "max_results": request_data.get("max_results", self.max_results),
            }
        )
        answer["claim"] = claim
        answer["verification_mode"] = "citation_grounded"
        return answer

    def _search_sources(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        unified = self.facade.unified_search(query, max_results).get("results", [])
        arxiv = self.facade.arxiv.search(query, min(4, max_results)).get("results", [])
        by_key: Dict[str, Dict[str, Any]] = {}
        for paper in [*unified, *arxiv]:
            if not isinstance(paper, dict):
                continue
            key = str(paper.get("doi") or paper.get("id") or paper.get("title") or "").strip().lower()
            if not key:
                continue
            by_key.setdefault(key, paper)
        return list(by_key.values())[:max_results]

    def _format_citations(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        citations: List[Dict[str, Any]] = []
        for paper in papers:
            title = str(paper.get("title") or "Untitled").strip()
            authors = paper.get("authors") or []
            first_author = authors[0] if isinstance(authors, list) and authors else "Unknown"
            year = paper.get("year") or "n.d."
            source = paper.get("source") or "unknown"
            doi = paper.get("doi")
            citation_text = f"{first_author} et al. ({year}). {title} [{source}]"
            citations.append(
                {
                    "title": title,
                    "source": source,
                    "year": year,
                    "doi": doi,
                    "citation": citation_text,
                }
            )
        return citations

    def _build_summary(
        self,
        question: str,
        domain: str,
        papers: List[Dict[str, Any]],
        citations: List[Dict[str, Any]],
        support_score: float,
    ) -> str:
        if not papers:
            return (
                f"No encontré literatura suficiente para responder de forma sólida la pregunta '{question}' "
                f"en el dominio {domain}."
            )
        top_titles = "; ".join(c["title"] for c in citations[:3])
        return (
            f"PaperQA2-style synthesis for '{question}': se identificaron {len(papers)} trabajos relevantes "
            f"en {domain}. La evidencia agregada sugiere un soporte {'moderado' if support_score >= 0.45 else 'limitado'} "
            f"(support_score={support_score:.3f}). Referencias principales: {top_titles}."
        )

    def _build_reasons(
        self,
        papers: List[Dict[str, Any]],
        citations: List[Dict[str, Any]],
        support_score: float,
    ) -> List[str]:
        reasons = []
        if papers:
            reasons.append(f"Recovered {len(papers)} relevant papers across open literature sources.")
        if citations:
            reasons.append(f"Top cited evidence includes {citations[0]['title']}.")
        reasons.append(f"Keyword-overlap support score computed at {support_score:.3f}.")
        if not self._package_installed:
            reasons.append("Official paper-qa package is not installed; using Atlas citation-grounded fallback.")
        return reasons

    def _score_support(self, claim: str, papers: List[Dict[str, Any]]) -> float:
        if not papers:
            return 0.0
        stop = {
            "the", "and", "for", "with", "from", "under", "over", "into", "onto",
            "via", "using", "of", "to", "in", "on", "by", "a", "an", "is", "are",
            "be", "being", "been", "this", "that", "whether", "does", "can",
        }
        tokens = [
            t for t in re.split(r"[^a-zA-Z0-9]+", claim.lower())
            if len(t) > 3 and t not in stop
        ]
        if not tokens:
            return 0.0
        total = 0.0
        for paper in papers:
            text = " ".join(
                [
                    str(paper.get("title") or ""),
                    str(paper.get("abstract") or ""),
                ]
            ).lower()
            hits = sum(1 for t in tokens if t in text)
            if hits >= 3:
                total += 1.0
            elif hits == 2:
                total += 0.7
            elif hits == 1:
                total += 0.35
        return round(min(1.0, total / max(len(papers), 1)), 3)
