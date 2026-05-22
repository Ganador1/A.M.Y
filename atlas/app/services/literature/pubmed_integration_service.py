#!/usr/bin/env python3
"""
PubMed/MEDLINE Integration Service
Provides access to real scientific literature and research data
"""
import asyncio
import httpx
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from app.core.bootstrap_logging import logger  # Use global logger instance
from app.core.config import settings
import json
import time
from app.middleware.trace_id_middleware import (
    TRACE_HEADER,
    get_current_trace_id,
    ensure_trace_id,
)
from app.exceptions.domain.biology import BiologyError


@dataclass
class PubMedArticle:
    """Scientific article from PubMed database."""
    pmid: str
    title: str
    abstract: str
    authors: List[str]
    journal: str
    pub_date: str
    doi: Optional[str] = None
    keywords: Optional[List[str]] = None
    citation_count: int = 0
    mesh_terms: Optional[List[str]] = None

@dataclass 
class PubMedSearchResult:
    """Result of PubMed search operation."""
    query: str
    total_results: int
    articles: List[PubMedArticle]
    search_time: float
    success: bool
    error: Optional[str] = None

class PubMedIntegrationService:
    """Service for integrating with PubMed/MEDLINE database."""
    
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.client = httpx.AsyncClient(
            timeout=30.0,
            event_hooks={
                "request": [self._inject_trace_id_async]
            },
        )
        self.rate_limit_delay = 0.5  # NCBI requests max 3 per second for non-registered
        self.last_request_time = 0
        logger.info("✅ PubMedIntegrationService initialized")
    
    async def _inject_trace_id_async(self, request: httpx.Request) -> None:
        tid = get_current_trace_id() or ensure_trace_id()
        if tid and TRACE_HEADER not in request.headers:
            request.headers[TRACE_HEADER] = tid

    async def _rate_limit(self):
        """Implement rate limiting for NCBI API."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    async def search_papers(
        self,
        query: str,
        max_results: int = 20,
        publication_years: Optional[tuple] = None,
        journal_filter: Optional[str] = None
    ) -> PubMedSearchResult:
        """
        Search scientific papers in PubMed database.
        
        Args:
            query: Search terms (e.g., "nanoparticles neural regeneration")
            max_results: Maximum number of papers to retrieve
            publication_years: Tuple of (start_year, end_year) to filter results
            journal_filter: Filter by specific journal name
            
        Returns:
            PubMedSearchResult with articles and metadata
        """
        start_time = time.time()
        
        try:
            # Build search query
            search_query = query
            if publication_years:
                start_year, end_year = publication_years
                search_query += f" AND (\"{start_year}\"[Date - Publication] : \"{end_year}\"[Date - Publication])"
            
            if journal_filter:
                search_query += f" AND \"{journal_filter}\"[Journal]"
            
            logger.info(f"🔍 Searching PubMed: {search_query}")
            
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
                return PubMedSearchResult(
                    query=query,
                    total_results=0,
                    articles=[],
                    search_time=time.time() - start_time,
                    success=False,
                    error=f"Search request failed: {search_response.status_code}"
                )
            
            # Parse search results
            search_root = ET.fromstring(search_response.text)
            pmids = [id_elem.text for id_elem in search_root.findall(".//Id") if id_elem.text is not None]
            count_elem = search_root.find(".//Count")
            total_count = int(count_elem.text) if count_elem is not None and count_elem.text else 0
            
            if not pmids:
                return PubMedSearchResult(
                    query=query,
                    total_results=total_count,
                    articles=[],
                    search_time=time.time() - start_time,
                    success=True
                )
            
            logger.info(f"📚 Found {len(pmids)} PMIDs out of {total_count} total results")
            
            # Step 2: Fetch detailed article information
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
                return PubMedSearchResult(
                    query=query,
                    total_results=total_count,
                    articles=[],
                    search_time=time.time() - start_time,
                    success=False,
                    error=f"Fetch request failed: {fetch_response.status_code}"
                )
            
            # Parse article details
            articles = self._parse_articles(fetch_response.text)
            
            return PubMedSearchResult(
                query=query,
                total_results=total_count,
                articles=articles,
                search_time=time.time() - start_time,
                success=True
            )
            
        except BiologyError as e:
            logger.error(f"❌ PubMed search failed: {str(e)}")
            return PubMedSearchResult(
                query=query,
                total_results=0,
                articles=[],
                search_time=time.time() - start_time,
                success=False,
                error=str(e)
            )
    
    def _parse_articles(self, xml_content: str) -> List[PubMedArticle]:
        """Parse XML response from PubMed efetch into article objects."""
        articles = []
        
        try:
            root = ET.fromstring(xml_content)
            
            for article_elem in root.findall(".//PubmedArticle"):
                try:
                    # Extract PMID
                    pmid_elem = article_elem.find(".//PMID")
                    pmid = pmid_elem.text if pmid_elem is not None else "unknown"
                    
                    # Extract title
                    title_elem = article_elem.find(".//ArticleTitle")
                    title = title_elem.text if title_elem is not None else "No title"
                    if title_elem is not None and title_elem.text is None:
                        # Handle cases where title has nested elements
                        title = "".join(title_elem.itertext())
                    
                    # Extract abstract
                    abstract_elems = article_elem.findall(".//AbstractText")
                    abstract_parts = []
                    for abs_elem in abstract_elems:
                        if abs_elem.text:
                            label = abs_elem.get('Label', '')
                            text = abs_elem.text
                            if label:
                                abstract_parts.append(f"{label}: {text}")
                            else:
                                abstract_parts.append(text)
                    abstract = "\n\n".join(abstract_parts) if abstract_parts else "No abstract available"
                    
                    # Extract authors
                    authors = []
                    for author_elem in article_elem.findall(".//Author"):
                        last_name = author_elem.find("LastName")
                        first_name = author_elem.find("ForeName")
                        if last_name is not None:
                            author_name = last_name.text or ""
                            if first_name is not None and first_name.text:
                                author_name += f", {first_name.text}"
                            authors.append(author_name)
                    
                    # Extract journal
                    journal_elem = article_elem.find(".//Journal/Title")
                    journal = journal_elem.text if journal_elem is not None else "Unknown journal"
                    
                    # Extract publication date
                    pub_date = "Unknown"
                    pub_date_elem = article_elem.find(".//PubDate")
                    if pub_date_elem is not None:
                        year_elem = pub_date_elem.find("Year")
                        month_elem = pub_date_elem.find("Month")
                        if year_elem is not None:
                            year = year_elem.text
                            month = month_elem.text if month_elem is not None else "01"
                            pub_date = f"{year}-{month.zfill(2)}"
                    
                    # Extract DOI
                    doi = None
                    for id_elem in article_elem.findall(".//ArticleId"):
                        if id_elem.get('IdType') == 'doi':
                            doi = id_elem.text
                            break
                    
                    # Extract MeSH terms
                    mesh_terms = []
                    for mesh_elem in article_elem.findall(".//MeshHeading/DescriptorName"):
                        if mesh_elem.text:
                            mesh_terms.append(mesh_elem.text)
                    
                    # Extract keywords
                    keywords = []
                    for keyword_elem in article_elem.findall(".//Keyword"):
                        if keyword_elem.text:
                            keywords.append(keyword_elem.text)
                    
                    article = PubMedArticle(
                        pmid=pmid,
                        title=title,
                        abstract=abstract,
                        authors=authors,
                        journal=journal,
                        pub_date=pub_date,
                        doi=doi,
                        keywords=keywords,
                        mesh_terms=mesh_terms
                    )
                    
                    articles.append(article)
                    
                except BiologyError as e:
                    logger.warning(f"⚠️ Failed to parse individual article: {str(e)}")
                    continue
                    
        except BiologyError as e:
            logger.error(f"❌ Failed to parse PubMed XML: {str(e)}")
        
        logger.info(f"✅ Successfully parsed {len(articles)} articles")
        return articles
    
    async def get_related_papers(self, pmid: str, max_results: int = 10) -> List[PubMedArticle]:
        """Find papers related to a specific PMID."""
        try:
            await self._rate_limit()
            response = await self.client.get(
                f"{self.base_url}elink.fcgi",
                params={
                    "dbfrom": "pubmed",
                    "db": "pubmed",
                    "id": pmid,
                    "linkname": "pubmed_pubmed",
                    "retmax": max_results,
                    "retmode": "xml"
                }
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Related papers request failed: {response.status_code}")
                return []
            
            # Parse related PMIDs
            root = ET.fromstring(response.text)
            related_pmids = [id_elem.text for id_elem in root.findall(".//Id")]
            
            if not related_pmids:
                return []
            
            # Fetch details for related papers
            await self._rate_limit()
            fetch_response = await self.client.get(
                f"{self.base_url}efetch.fcgi",
                params={
                    "db": "pubmed",
                    "id": ",".join(related_pmids[:max_results]),
                    "retmode": "xml"
                }
            )
            
            if fetch_response.status_code == 200:
                return self._parse_articles(fetch_response.text)
            else:
                return []
                
        except BiologyError as e:
            logger.error(f"❌ Failed to get related papers: {str(e)}")
            return []
    
    async def extract_research_trends(
        self,
        domain: str,
        years_range: int = 5
    ) -> Dict[str, Any]:
        """
        Analyze research trends in a specific domain over recent years.
        
        Args:
            domain: Scientific domain (e.g., "neuroscience", "materials_science")
            years_range: Number of recent years to analyze
            
        Returns:
            Dictionary with trend analysis
        """
        current_year = 2024
        start_year = current_year - years_range
        
        # Define domain-specific search terms
        domain_terms = {
            "neuroscience": "neuroscience OR neural OR brain OR neuronal",
            "materials_science": "materials science OR nanomaterials OR biomaterials",
            "drug_discovery": "drug discovery OR pharmaceutical OR therapeutic",
            "genomics": "genomics OR gene expression OR CRISPR",
            "biophysics": "biophysics OR molecular dynamics OR protein folding"
        }
        
        search_term = domain_terms.get(domain, domain)
        
        try:
            # Search for papers in the time range
            result = await self.search_papers(
                query=search_term,
                max_results=100,
                publication_years=(start_year, current_year)
            )
            
            if not result.success:
                return {
                    "success": False,
                    "error": result.error,
                    "domain": domain
                }
            
            # Analyze trends
            year_distribution = {}
            journal_distribution = {}
            keyword_frequency = {}
            mesh_frequency = {}
            
            for article in result.articles:
                # Year distribution
                year = article.pub_date.split('-')[0] if article.pub_date != "Unknown" else "Unknown"
                year_distribution[year] = year_distribution.get(year, 0) + 1
                
                # Journal distribution
                journal_distribution[article.journal] = journal_distribution.get(article.journal, 0) + 1
                
                # Keyword frequency
                if article.keywords:
                    for keyword in article.keywords:
                        keyword_frequency[keyword] = keyword_frequency.get(keyword, 0) + 1
                
                # MeSH term frequency
                if article.mesh_terms:
                    for mesh in article.mesh_terms:
                        mesh_frequency[mesh] = mesh_frequency.get(mesh, 0) + 1
            
            # Sort and limit results
            top_journals = sorted(journal_distribution.items(), key=lambda x: x[1], reverse=True)[:10]
            top_keywords = sorted(keyword_frequency.items(), key=lambda x: x[1], reverse=True)[:20]
            top_mesh = sorted(mesh_frequency.items(), key=lambda x: x[1], reverse=True)[:20]
            
            return {
                "success": True,
                "domain": domain,
                "search_term": search_term,
                "total_papers": len(result.articles),
                "time_range": f"{start_year}-{current_year}",
                "year_distribution": year_distribution,
                "top_journals": top_journals,
                "top_keywords": top_keywords,
                "top_mesh_terms": top_mesh,
                "growth_trend": self._calculate_growth_trend(year_distribution, start_year, current_year)
            }
            
        except BiologyError as e:
            logger.error(f"❌ Failed to extract research trends: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "domain": domain
            }
    
    def _calculate_growth_trend(self, year_dist: Dict[str, int], start_year: int, end_year: int) -> str:
        """Calculate if research in domain is growing, stable, or declining."""
        years = [str(y) for y in range(start_year, end_year + 1) if str(y) in year_dist]
        if len(years) < 2:
            return "insufficient_data"
        
        early_papers = sum(year_dist.get(str(y), 0) for y in range(start_year, start_year + 2))
        late_papers = sum(year_dist.get(str(y), 0) for y in range(end_year - 1, end_year + 1))
        
        if late_papers > early_papers * 1.2:
            return "growing"
        elif late_papers < early_papers * 0.8:
            return "declining"
        else:
            return "stable"
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
        logger.info("✅ PubMedIntegrationService closed")

# Factory function for tool integration
def create_pubmed_service() -> PubMedIntegrationService:
    """Factory function to create PubMed service instance."""
    return PubMedIntegrationService()
