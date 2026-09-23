"""
Web Research Skill — Structured literature search and claim verification.

Wraps the WebSensor and Atlas literature tools to provide:
- Multi-source literature search
- Claim verification against retrieved abstracts
- Deduplication and relevance ranking
"""
from pathlib import Path

import structlog

log = structlog.get_logger()


class WebResearchSkill:
    """Structured web research with claim verification."""

    def __init__(self, web_sensor, atlas_tools=None):
        self.web_sensor = web_sensor
        self.atlas_tools = atlas_tools

    async def search_literature(self, query: str, domain: str = "medicine") -> dict:
        """
        Search both A.M.Y's web sensor and Atlas for literature.
        Returns deduplicated papers with source tags.
        """
        amypapers = []
        atlas_papers = []

        try:
            amypapers = await self.web_sensor.search(query)
        except Exception as e:
            log.warning("web_research.amy_search_error", error=str(e))

        if self.atlas_tools is not None:
            try:
                atlas_result = await self.atlas_tools.search_literature(query, domain=domain)
                atlas_papers = atlas_result.get("papers", atlas_result.get("sources", {}).get("papers", []))
            except Exception as e:
                log.warning("web_research.atlas_search_error", error=str(e))

        # Deduplicate by title (case-insensitive)
        seen = set()
        combined = []
        for p in amypapers + atlas_papers:
            title = (p.get("title", "") if isinstance(p, dict) else str(p)).lower().strip()
            if title and title not in seen:
                seen.add(title)
                combined.append(p if isinstance(p, dict) else {"title": str(p)})

        log.info("web_research.combined", query=query[:60], count=len(combined))
        return {
            "query": query,
            "domain": domain,
            "papers": combined,
            "amy_count": len(amypapers),
            "atlas_count": len(atlas_papers),
        }

    async def verify_claim(self, claim: str, query: str, domain: str = "medicine") -> dict:
        """
        Search for literature related to a claim and perform a lightweight
        keyword-based verification against abstracts.
        """
        result = await self.search_literature(query, domain=domain)
        papers = result.get("papers", [])

        claim_lower = claim.lower()
        claim_words = set(w for w in claim_lower.split() if len(w) > 4)

        supporting = []
        contradicting = []
        neutral = []

        negation_words = {"not", "no", "none", "never", "without", "lack", "absence", "failure", "ineffective"}

        for p in papers:
            abstract = (p.get("summary", "") + " " + p.get("abstract", "")).lower()
            if not abstract.strip():
                continue

            overlap = claim_words & set(abstract.split())
            score = len(overlap) / max(len(claim_words), 1)

            has_negation = any(nw in abstract for nw in negation_words)

            if score > 0.3:
                if has_negation:
                    contradicting.append({"paper": p, "score": score})
                else:
                    supporting.append({"paper": p, "score": score})
            else:
                neutral.append({"paper": p, "score": score})

        # Sort by score
        supporting.sort(key=lambda x: -x["score"])
        contradicting.sort(key=lambda x: -x["score"])

        verdict = "unverified"
        if supporting and not contradicting:
            verdict = "supported"
        elif contradicting and not supporting:
            verdict = "contradicted"
        elif supporting and contradicting:
            verdict = "mixed"

        return {
            "claim": claim,
            "query": query,
            "verdict": verdict,
            "supporting_count": len(supporting),
            "contradicting_count": len(contradicting),
            "top_supporting": supporting[:3],
            "top_contradicting": contradicting[:3],
        }
