"""
Enhanced Literature Search Service
Integrates real scientific database access
"""

import sys
import hashlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'improvements'))

from improvements.real_scientific_databases import RealScientificDatabasesV2
from typing import Dict, Any, Optional, List
import asyncio

from app.services.literature_offline_cache import LiteratureOfflineCache

class LiteratureSearchService:
    """Enhanced literature search with real databases"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        self.real_db = RealScientificDatabasesV2()
        self.offline_cache = LiteratureOfflineCache(cache_dir=cache_dir or "./literature_cache")
    
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a literature search request (BaseService interface)"""
        action = request_data.get("action", "search")
        
        if action in {"search", "search_literature"}:
            return await self.search_literature(request_data)
        elif action == "validate":
            hypothesis = request_data.get("hypothesis", "")
            return await self.validate_hypothesis(hypothesis)
        elif action == "cache_upsert":
            return await self._cache_upsert_async(request_data)
        elif action == "search_offline":
            return await self._search_offline_async(request_data)
        else:
            return await self.search_literature(request_data)

    def cache_upsert(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync wrapper for cache upsert (compatibility with sync callers)."""
        return asyncio.run(self._cache_upsert_async(request_data))

    def search_offline(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync wrapper for offline search (compatibility with sync callers)."""
        return asyncio.run(self._search_offline_async(request_data))

    async def _cache_upsert_async(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        papers = request_data.get("papers")
        if not isinstance(papers, list):
            return {"success": False, "error": "'papers' must be a list"}

        entries: List[Dict[str, Any]] = []
        for paper in papers:
            if not isinstance(paper, dict):
                continue

            paper_id = paper.get("paper_id") or paper.get("id")
            doi = paper.get("doi")
            title = paper.get("title") or ""

            if paper_id:
                key = f"paper:{paper_id}"
            elif doi:
                key = f"doi:{doi}"
            else:
                title_hash = hashlib.sha256(title.encode("utf-8", errors="ignore")).hexdigest()
                key = f"title:{title_hash}"

            metadata = {
                "paper_id": paper_id,
                "doi": doi,
                "title": title,
                "domain": request_data.get("domain"),
            }

            entries.append({"key": key, "content": paper, "metadata": metadata})

        if not entries:
            return {"success": True, "added": 0, "total": 0}

        results = await self.offline_cache.put_batch(entries)
        added = sum(1 for ok in results.values() if ok)

        return {
            "success": True,
            "added": added,
            "total": len(entries),
        }

    async def _search_offline_async(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        query = (request_data.get("query") or "").strip()
        if not query:
            return {"success": False, "error": "'query' is required"}

        max_results = int(request_data.get("max_results") or 20)
        query_l = query.lower()

        keys = await self.offline_cache.list_keys()
        # Prefer paper/doi/title keys; ignore other cache entries.
        candidate_keys = [
            k for k in keys
            if k.startswith("paper:") or k.startswith("doi:") or k.startswith("title:")
        ]

        papers: List[Dict[str, Any]] = []
        scanned = 0
        for key in candidate_keys:
            if len(papers) >= max_results:
                break

            scanned += 1
            content = await self.offline_cache.get(key)
            if not isinstance(content, dict):
                continue

            title = (content.get("title") or "").lower()
            abstract = (content.get("abstract") or "").lower()

            if query_l in title or query_l in abstract:
                papers.append(content)

        return {
            "success": True,
            "papers": papers,
            "summary": {
                "total_found": len(papers),
                "scanned": scanned,
            },
        }
    
    async def search_literature(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Search real scientific databases"""
        query = request_data.get("query", "")
        max_results = request_data.get("max_results", 50)
        
        # Search real databases
        results = await self.real_db.search_all_databases(
            query,
            max_results_per_db=max_results
        )
        
        # Convert to expected format
        papers = []
        for paper in results.get("papers", []):
            papers.append({
                "paper_id": paper.id,
                "title": paper.title,
                "authors": paper.authors,
                "abstract": paper.abstract,
                "journal": paper.journal,
                "year": paper.year,
                "doi": paper.doi,
                "citations": paper.citations
            })
        
        return {
            "success": True,
            "papers": papers,
            "total_results": len(papers)
        }
    
    async def validate_hypothesis(self, hypothesis: str) -> Dict[str, Any]:
        """Validate hypothesis against literature"""
        return await self.real_db.validate_hypothesis_against_literature(hypothesis)
