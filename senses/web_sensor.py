"""
Web Sensor — A.M.Y's eyes on the internet.

Searches academic papers (arXiv, PubMed, Semantic Scholar),
news, and general web for information relevant to the mission.

Rate limiting:
- arXiv recommends >= 3s between requests (https://arxiv.org/help/api/user-manual)
- PubMed E-utilities: 3 requests/second without API key
- Semantic Scholar: 1 request/second (100/5min)
"""
import asyncio
import time
import structlog

log = structlog.get_logger()

# Per-source rate limit state (shared across all instances)
_last_request: dict[str, float] = {}
_MIN_INTERVAL: dict[str, float] = {
    "arxiv": 5.0,            # 5s between arXiv requests
    "pubmed": 0.4,           # ~3/s for PubMed
    "semantic_scholar": 2.0, # ~1/s for Semantic Scholar
}


async def _rate_limit(source: str) -> None:
    """Async sleep to respect per-source rate limits."""
    now = time.monotonic()
    last = _last_request.get(source, 0.0)
    wait = _MIN_INTERVAL.get(source, 1.0) - (now - last)
    if wait > 0:
        await asyncio.sleep(wait)
    _last_request[source] = time.monotonic()


class WebSensor:
    """
    Asynchronous web research capabilities with polite rate limiting.
    """

    def __init__(self, config: dict):
        self.config = config
        self.max_papers = config.get("max_papers_per_search", 10)
        self.sources = config.get("sources", ["arxiv"])

    async def search(self, query: str) -> list[dict]:
        """Search the web for information related to a query."""
        results = []

        for source in self.sources:
            try:
                if source == "arxiv":
                    results.extend(await self._search_arxiv(query))
                elif source == "pubmed":
                    results.extend(await self._search_pubmed(query))
                elif source == "semantic_scholar":
                    results.extend(await self._search_semantic_scholar(query))
            except Exception as e:
                log.warning("web_sensor.source_error", source=source, error=str(e))

        log.info("web_sensor.search_complete", query=query[:60], results=len(results))
        return results

    async def _search_arxiv(self, query: str) -> list[dict]:
        """Search arXiv for papers (respects 5s rate limit)."""
        import urllib.request
        import urllib.parse
        import xml.etree.ElementTree as ET

        await _rate_limit("arxiv")

        url = (
            f"https://export.arxiv.org/api/query?"
            f"search_query=all:{urllib.parse.quote(query)}"
            f"&start=0&max_results={min(self.max_papers, 10)}"
            f"&sortBy=submittedDate&sortOrder=descending"
        )

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "AMY-AutonomousResearch/1.0 (mailto:contact@amy.ai)"},
            )
            response = urllib.request.urlopen(req, timeout=30)
            xml_data = response.read()
            root = ET.fromstring(xml_data)

            ns = {"atom": "http://www.w3.org/2005/Atom"}
            results = []

            for entry in root.findall("atom:entry", ns):
                title = entry.find("atom:title", ns)
                summary = entry.find("atom:summary", ns)
                published = entry.find("atom:published", ns)
                link = entry.find("atom:id", ns)

                results.append({
                    "source": "arxiv",
                    "title": title.text.strip().replace("\n", " ") if title is not None else "",
                    "summary": summary.text.strip().replace("\n", " ")[:500] if summary is not None else "",
                    "date": published.text if published is not None else "",
                    "url": link.text if link is not None else "",
                })

            return results
        except Exception as e:
            log.warning("web_sensor.arxiv_error", error=str(e))
            return []

    async def _search_pubmed(self, query: str) -> list[dict]:
        """Search PubMed for biomedical papers (respects 0.4s rate limit)."""
        import urllib.request
        import urllib.parse
        import json as json_module

        await _rate_limit("pubmed")

        base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        search_url = (
            f"{base}/esearch.fcgi?db=pubmed"
            f"&term={urllib.parse.quote(query)}"
            f"&retmax={self.max_papers}&retmode=json"
            f"&tool=AMY&email=contact@amy.ai"
        )

        try:
            response = urllib.request.urlopen(search_url, timeout=30)
            data = json_module.loads(response.read())
            ids = data.get("esearchresult", {}).get("idlist", [])

            if not ids:
                return []

            await _rate_limit("pubmed")
            ids_str = ",".join(ids)
            summary_url = (
                f"{base}/esummary.fcgi?db=pubmed&id={ids_str}&retmode=json"
                f"&tool=AMY&email=contact@amy.ai"
            )
            response = urllib.request.urlopen(summary_url, timeout=30)
            summaries = json_module.loads(response.read())

            results = []
            for pid in ids:
                info = summaries.get("result", {}).get(pid, {})
                results.append({
                    "source": "pubmed",
                    "title": info.get("title", ""),
                    "summary": info.get("sorttitle", ""),
                    "date": info.get("pubdate", ""),
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/",
                })

            return results
        except Exception as e:
            log.warning("web_sensor.pubmed_error", error=str(e))
            return []

    async def _search_semantic_scholar(self, query: str) -> list[dict]:
        """Search Semantic Scholar API (respects 2s rate limit)."""
        import urllib.request
        import urllib.parse
        import json as json_module

        await _rate_limit("semantic_scholar")

        url = (
            f"https://api.semanticscholar.org/graph/v1/paper/search"
            f"?query={urllib.parse.quote(query)}"
            f"&limit={self.max_papers}"
            f"&fields=title,abstract,year,url"
        )

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "AMY-AutonomousResearch/1.0"},
            )
            response = urllib.request.urlopen(req, timeout=30)
            data = json_module.loads(response.read())

            results = []
            for paper in data.get("data", []):
                results.append({
                    "source": "semantic_scholar",
                    "title": paper.get("title", ""),
                    "summary": (paper.get("abstract", "") or "")[:500],
                    "date": str(paper.get("year", "")),
                    "url": paper.get("url", ""),
                })

            return results
        except Exception as e:
            log.warning("web_sensor.semantic_scholar_error", error=str(e))
            return []

    async def fetch_page(self, url: str) -> str:
        """Fetch the content of a web page."""
        import urllib.request
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "AMY-AutonomousResearch/1.0"},
            )
            response = urllib.request.urlopen(req, timeout=30)
            return response.read().decode("utf-8", errors="ignore")[:10000]
        except Exception as e:
            log.warning("web_sensor.fetch_error", url=url, error=str(e))
            return ""
