#!/usr/bin/env python3
"""
PubMed Integration Service - Simplified Working Version
Provides access to real scientific literature for the autonomous lab
"""
import asyncio
import httpx
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from app.core.bootstrap_logging import logger
import json
import time
from app.middleware.trace_id_middleware import (
    TRACE_HEADER,
    get_current_trace_id,
    ensure_trace_id,
)
from app.exceptions.domain.biology import BiologyError


@dataclass
class SimplePubMedArticle:
    """Simplified scientific article from PubMed database."""
    pmid: str
    title: str
    abstract: str
    journal: str
    pub_date: str
    authors_count: int = 0
    doi: Optional[str] = None

class PubMedService:
    """Simplified PubMed service for autonomous lab integration."""
    
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.client = httpx.AsyncClient(
            timeout=30.0,
            event_hooks={
                "request": [self._inject_trace_id_async]
            },
        )
        self.rate_limit_delay = 0.5  # NCBI rate limit
        self.last_request_time = 0
        logger.info("✅ PubMedService initialized")

    async def _inject_trace_id_async(self, request: httpx.Request) -> None:
        tid = get_current_trace_id() or ensure_trace_id()
        if tid and TRACE_HEADER not in request.headers:
            request.headers[TRACE_HEADER] = tid

    async def _rate_limit(self):
        """Implement NCBI API rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    async def search_papers(
        self,
        query: str,
        max_results: int = 10,
        recent_years: int = 5
    ) -> Dict[str, Any]:
        """
        Search scientific papers in PubMed.
        
        Args:
            query: Search terms
            max_results: Maximum papers to retrieve
            recent_years: Only papers from last N years
            
        Returns:
            Dictionary with search results and evidence metrics
        """
        start_time = time.time()
        current_year = 2024
        start_year = current_year - recent_years
        
        try:
            # Build search query with year filter
            search_query = f"{query} AND (\"{start_year}\"[Date - Publication] : \"{current_year}\"[Date - Publication])"
            
            logger.info(f"🔍 PubMed search: {query}")
            
            # Step 1: Search for PMIDs
            await self._rate_limit()
            search_response = await self.client.get(
                f"{self.base_url}esearch.fcgi",
                params={
                    "db": "pubmed",
                    "term": search_query,
                    "retmax": max_results,
                    "retmode": "xml",
                    "sort": "relevance"
                }
            )
            
            if search_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Search failed: {search_response.status_code}",
                    "evidence_score": 0.0
                }
            
            # Parse search results
            search_root = ET.fromstring(search_response.text)
            pmids = []
            for id_elem in search_root.findall(".//Id"):
                if id_elem.text:
                    pmids.append(id_elem.text)
            
            count_elem = search_root.find(".//Count")
            total_count = int(count_elem.text) if count_elem is not None and count_elem.text else 0
            
            if not pmids:
                return {
                    "success": True,
                    "total_found": total_count,
                    "articles": [],
                    "evidence_score": 0.0,
                    "search_time": time.time() - start_time
                }
            
            # Step 2: Fetch article details
            await self._rate_limit()
            fetch_response = await self.client.get(
                f"{self.base_url}efetch.fcgi",
                params={
                    "db": "pubmed",
                    "id": ",".join(pmids),
                    "retmode": "xml"
                }
            )
            
            if fetch_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Fetch failed: {fetch_response.status_code}",
                    "evidence_score": 0.0
                }
            
            # Parse articles
            articles = self._parse_articles_simple(fetch_response.text)
            
            # Calculate evidence score based on result quality
            evidence_score = self._calculate_evidence_score(articles, total_count, query)
            
            return {
                "success": True,
                "total_found": total_count,
                "articles": articles,
                "evidence_score": evidence_score,
                "search_time": time.time() - start_time,
                "query_terms": query.split()
            }
            
        except BiologyError as e:
            logger.error(f"❌ PubMed search error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "evidence_score": 0.0
            }
    
    def _parse_articles_simple(self, xml_content: str) -> List[SimplePubMedArticle]:
        """Parse XML response into simplified article objects."""
        articles = []
        
        try:
            root = ET.fromstring(xml_content)
            
            for article_elem in root.findall(".//PubmedArticle"):
                try:
                    # PMID
                    pmid_elem = article_elem.find(".//PMID")
                    pmid = pmid_elem.text if pmid_elem is not None and pmid_elem.text else "unknown"
                    
                    # Title
                    title_elem = article_elem.find(".//ArticleTitle")
                    title = "No title"
                    if title_elem is not None:
                        title = title_elem.text if title_elem.text else "".join(title_elem.itertext())
                    
                    # Abstract
                    abstract_parts = []
                    for abs_elem in article_elem.findall(".//AbstractText"):
                        if abs_elem.text:
                            abstract_parts.append(abs_elem.text)
                    abstract = " ".join(abstract_parts) if abstract_parts else "No abstract available"
                    
                    # Journal
                    journal_elem = article_elem.find(".//Journal/Title")
                    journal = journal_elem.text if journal_elem is not None and journal_elem.text else "Unknown journal"
                    
                    # Publication date
                    pub_date = "Unknown"
                    pub_date_elem = article_elem.find(".//PubDate")
                    if pub_date_elem is not None:
                        year_elem = pub_date_elem.find("Year")
                        if year_elem is not None and year_elem.text:
                            year = year_elem.text
                            month_elem = pub_date_elem.find("Month")
                            month = month_elem.text if month_elem is not None and month_elem.text else "01"
                            # Handle month safely
                            if month.isdigit():
                                pub_date = f"{year}-{month.zfill(2)}"
                            else:
                                pub_date = f"{year}-01"
                    
                    # Authors count
                    authors_count = len(article_elem.findall(".//Author"))
                    
                    # DOI
                    doi = None
                    for id_elem in article_elem.findall(".//ArticleId"):
                        if id_elem.get('IdType') == 'doi' and id_elem.text:
                            doi = id_elem.text
                            break
                    
                    article = SimplePubMedArticle(
                        pmid=pmid,
                        title=title,
                        abstract=abstract,
                        journal=journal,
                        pub_date=pub_date,
                        authors_count=authors_count,
                        doi=doi
                    )
                    
                    articles.append(article)
                    
                except BiologyError as e:
                    logger.warning(f"⚠️ Failed to parse article: {str(e)}")
                    continue
                    
        except BiologyError as e:
            logger.error(f"❌ Failed to parse PubMed XML: {str(e)}")
        
        logger.info(f"✅ Parsed {len(articles)} articles from PubMed")
        return articles
    
    def _calculate_evidence_score(self, articles: List[SimplePubMedArticle], total_found: int, query: str) -> float:
        """Calculate evidence quality score based on search results."""
        if not articles:
            return 0.0
        
        # Base score from number of results
        result_score = min(total_found / 100, 1.0) * 0.3
        
        # Quality score from articles
        quality_score = 0.0
        for article in articles:
            article_quality = 0.0
            
            # Abstract quality
            if len(article.abstract) > 200:
                article_quality += 0.3
            
            # Recency bonus
            if article.pub_date != "Unknown":
                try:
                    year = int(article.pub_date.split('-')[0])
                    if year >= 2020:
                        article_quality += 0.2
                    elif year >= 2015:
                        article_quality += 0.1
                except BiologyError as e:
                    logger.debug(f"Failed to parse pub_date '{article.pub_date}': {e}")
            
            # Author collaboration indicator
            if article.authors_count >= 3:
                article_quality += 0.1
            
            # DOI availability (suggests journal quality)
            if article.doi:
                article_quality += 0.1
            
            quality_score += article_quality
        
        quality_score = quality_score / len(articles) * 0.7
        
        return min(result_score + quality_score, 1.0)
    
    async def get_domain_evidence(self, domain: str, hypothesis_keywords: List[str]) -> Dict[str, Any]:
        """
        Get evidence for a specific scientific domain and hypothesis.
        Designed for integration with ToolEvidenceOrchestrator.
        """
        # Domain-specific search terms
        domain_mapping = {
            "neuroscience": "neuroscience OR neural OR brain OR neuronal",
            "materials_science": "materials science OR nanomaterials OR biomaterials",
            "drug_discovery": "drug discovery OR pharmaceutical OR therapeutic",
            "genomics": "genomics OR gene expression OR CRISPR",
            "biophysics": "biophysics OR molecular dynamics OR protein",
            "biomedical_engineering": "biomedical engineering OR tissue engineering"
        }
        
        base_query = domain_mapping.get(domain, domain)
        
        # Combine with hypothesis keywords
        if hypothesis_keywords:
            keyword_query = " OR ".join(hypothesis_keywords[:3])  # Top 3 keywords
            combined_query = f"({base_query}) AND ({keyword_query})"
        else:
            combined_query = base_query
        
        result = await self.search_papers(combined_query, max_results=10, recent_years=3)
        
        if result["success"]:
            # Format for tool evidence system
            return {
                "success": True,
                "domain": domain,
                "literature_evidence": {
                    "papers_found": result["total_found"],
                    "papers_analyzed": len(result["articles"]),
                    "evidence_strength": result["evidence_score"],
                    "recent_research": result["evidence_score"] > 0.5,
                    "query_used": combined_query
                },
                "top_papers": [
                    {
                        "pmid": article.pmid,
                        "title": article.title[:100] + "..." if len(article.title) > 100 else article.title,
                        "journal": article.journal,
                        "year": article.pub_date.split('-')[0] if article.pub_date != "Unknown" else "Unknown"
                    }
                    for article in result["articles"][:3]
                ]
            }
        else:
            return {
                "success": False,
                "error": result["error"],
                "domain": domain
            }
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
        logger.info("✅ PubMedService closed")

# Factory function for tool integration
def create_pubmed_service() -> PubMedService:
    """Factory function to create PubMed service instance."""
    return PubMedService()
