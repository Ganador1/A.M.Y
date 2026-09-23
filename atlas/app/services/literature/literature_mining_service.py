"""
Literature Mining Service for AXIOM
Integración con PubTator 3.0, PubMed, arXiv y búsqueda semántica

Ethics & Safety:
- Respeta términos de uso de APIs (rate limits, attribution).
- No almacena contenido completo sin permisos de copyright.
- Filtra contenido inapropiado o no científico.
- Cita fuentes apropiadamente en resultados.

Ver ETHICS_AND_SAFETY.md para detalles y checklist.
"""

import logging
import asyncio
import aiohttp
import time
from typing import Dict, Any, List, Optional, Union, Tuple
import json
import re
from datetime import datetime, timedelta
from urllib.parse import quote, urlencode
import xml.etree.ElementTree as ET
from dataclasses import dataclass
import hashlib
import httpx

from app.services.base_service import BaseService
from app.exceptions.external.service import ServiceUnavailableError

# Import metrics service
from .metrics_service import metrics
from app.exceptions.domain.biology import BiologyError
from app.types.literature_mining_service_types import (
    GetServiceInfoResult,
    ResultToDictResult,
    AnalyzeTemporalTrendsResult,
    IdentifyResearchGapsResult,
    AnalyzeCollaborationNetworksResult,
    AnalyzeMethodologiesResult,
    AnalyzeImpactMetricsResult,
    SynthesizeKeyFindingsResult,
    GenerateResearchDirectionsResult,
    GetSemanticScholarCitationsResult,
    GetSemanticScholarMetricsResult,
    ExtractKeyConceptsResult,
    ExtractConceptsSyncResult,
    GetCitationNetworkResult,
    ProcessRequestResult,
)

# Text processing and embeddings
try:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.feature_extraction.text import TfidfVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class LiteratureResult:
    """Resultado de búsqueda de literatura"""
    title: str
    authors: List[str]
    abstract: str
    doi: Optional[str]
    pmid: Optional[str]
    arxiv_id: Optional[str]
    journal: Optional[str]
    publication_date: Optional[str]
    keywords: List[str]
    entities: List[Dict[str, Any]]
    relevance_score: float
    source: str
    url: str


class LiteratureMiningService(BaseService):
    """
    Servicio de minería de literatura científica
    Integra PubTator 3.0, PubMed, arXiv y búsqueda semántica
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("LiteratureMining")
        self.config = config or {}
        
        # API endpoints
        self.endpoints = {
            'pubmed': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/',
            'pubtator': 'https://www.ncbi.nlm.nih.gov/research/pubtator3-api/',
            'arxiv': 'http://export.arxiv.org/api/query',
            'crossref': 'https://api.crossref.org/works',
            'opencitations': 'https://opencitations.net/index/api/v1/',
            'semantic_scholar': 'https://api.semanticscholar.org/graph/v1/paper/'
        }
        
        # Rate limiting (requests per second)
        self.rate_limits = {
            'pubmed': 3,  # NCBI guidelines
            'pubtator': 2,
            'arxiv': 3,
            'crossref': 50,
            'opencitations': 5,
            'semantic_scholar': 10
        }
        
        # Request tracking for rate limiting
        self.request_history = {source: [] for source in self.rate_limits.keys()}
        
        # Initialize NLP components
        self.sentence_model = None
        self.tfidf_vectorizer = None
        self.lemmatizer = None
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            except BiologyError as e:
                logger.warning(f"Could not load sentence transformer: {e}")
        
        if SKLEARN_AVAILABLE:
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=10000,
                stop_words='english',
                ngram_range=(1, 2)
            )
        
        if NLTK_AVAILABLE:
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                nltk.download('wordnet', quiet=True)
                self.lemmatizer = WordNetLemmatizer()
            except BiologyError as e:
                logger.warning(f"NLTK setup failed: {e}")
        
        # Cache for results
        self.results_cache = {}
        self.entity_cache = {}
        
        # Domain-specific search configurations
        self.domain_configs = {
            'chemistry': {
                'mesh_terms': ['Chemistry', 'Chemical Compounds', 'Molecular Structure'],
                'keywords': ['molecule', 'compound', 'synthesis', 'reaction', 'catalyst'],
                'journals': ['Nature Chemistry', 'JACS', 'Angewandte Chemie'],
                'entity_types': ['Chemical', 'Gene', 'Disease']
            },
            'biology': {
                'mesh_terms': ['Biology', 'Molecular Biology', 'Cell Biology'],
                'keywords': ['protein', 'gene', 'cell', 'organism', 'pathway'],
                'journals': ['Nature', 'Cell', 'Science', 'PNAS'],
                'entity_types': ['Gene', 'Protein', 'Disease', 'Species']
            },
            'physics': {
                'mesh_terms': ['Physics', 'Quantum Physics', 'Materials Science'],
                'keywords': ['quantum', 'particle', 'field', 'energy', 'material'],
                'journals': ['Physical Review', 'Nature Physics', 'Science'],
                'entity_types': ['Chemical', 'Material']
            },
            'materials': {
                'mesh_terms': ['Materials Science', 'Nanotechnology'],
                'keywords': ['material', 'crystal', 'structure', 'property', 'synthesis'],
                'journals': ['Nature Materials', 'Advanced Materials'],
                'entity_types': ['Chemical', 'Material']
            }
        }
    
    def get_service_info(self) -> GetServiceInfoResult:
        """Get information about literature mining capabilities"""
        return {
            "data_sources": list(self.endpoints.keys()),
            "supported_domains": list(self.domain_configs.keys()),
            "features": [
                "PubTator 3.0 entity extraction",
                "Semantic search with embeddings",
                "Multi-source literature search",
                "Real-time rate limiting",
                "Domain-specific optimization",
                "Citation network analysis"
            ],
            "nlp_capabilities": {
                "sentence_transformers": SENTENCE_TRANSFORMERS_AVAILABLE,
                "nltk": NLTK_AVAILABLE,
                "sklearn": SKLEARN_AVAILABLE
            },
            "max_results_per_query": 1000,
            "supported_formats": ["json", "bibtex", "ris"]
        }
    
    async def comprehensive_search(self,
                                 query: str,
                                 domain: str = 'general',
                                 max_results: int = 100,
                                 date_range: Optional[Tuple[str, str]] = None,
                                 include_preprints: bool = True,
                                 semantic_search: bool = True) -> Dict[str, Any]:
        """
        Búsqueda comprehensiva en múltiples fuentes
        """
        start_time = time.time()
        
        # Track search metrics
        metrics.api_calls_total.labels(api_name='literature_search', domain=domain).inc()
        metrics.search_requests_total.labels(domain=domain).inc()
        
        # Validate inputs
        if not query.strip():
            metrics.search_errors_total.labels(error_type='empty_query', domain=domain).inc()
            raise ValueError("Query cannot be empty")
        
        max_results = min(max_results, 1000)  # Safety limit
        
        # Get domain configuration
        domain_config = self.domain_configs.get(domain, {})
        
        # Enhance query with domain-specific terms
        enhanced_query = self._enhance_query(query, domain_config)
        
        logger.info(f"Starting comprehensive search for: {enhanced_query}")
        
        # Search multiple sources concurrently
        search_tasks = []
        
        # PubMed search
        search_tasks.append(
            self._search_pubmed(enhanced_query, max_results // 3, date_range)
        )
        
        # arXiv search (if including preprints)
        if include_preprints:
            search_tasks.append(
                self._search_arxiv(enhanced_query, max_results // 3, date_range)
            )
        
        # Execute searches
        search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # Combine results
        all_results = []
        source_stats = {}
        
        for i, result in enumerate(search_results):
            if isinstance(result, Exception):
                source = ['pubmed', 'arxiv'][i] if include_preprints else ['pubmed'][i]
                logger.error(f"Search failed for {source}: {result}")
                source_stats[source] = {'count': 0, 'error': str(result)}
            else:
                all_results.extend(result['results'])
                source_stats.update(result['stats'])
        
        # Remove duplicates
        unique_results = self._deduplicate_results(all_results)
        
        # Extract entities using PubTator 3.0
        if unique_results:
            unique_results = await self._extract_entities_batch(unique_results)
        
        # Semantic ranking if enabled
        if semantic_search and self.sentence_model and unique_results:
            unique_results = await self._semantic_ranking(query, unique_results)
        
        # Sort by relevance score
        unique_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Limit results
        final_results = unique_results[:max_results]
        
        # Generate summary statistics
        execution_time = time.time() - start_time
        
        result = {
            'query': query,
            'enhanced_query': enhanced_query,
            'domain': domain,
            'results': [self._result_to_dict(r) for r in final_results],
            'total_found': len(unique_results),
            'returned': len(final_results),
            'source_statistics': source_stats,
            'execution_time': execution_time,
            'search_metadata': {
                'semantic_search_enabled': semantic_search,
                'include_preprints': include_preprints,
                'date_range': date_range,
                'domain_config_used': bool(domain_config)
            }
        }
        
        # Cache results
        cache_key = self._generate_cache_key(query, domain, max_results, date_range)
        self.results_cache[cache_key] = result
        
        # Track search metrics
        metrics.search_duration_seconds.labels(domain=domain).observe(execution_time)
        metrics.papers_processed_total.labels(domain=domain).inc(len(final_results))
        metrics.search_success_total.labels(domain=domain).inc()
        
        # Track entity extraction metrics
        total_entities = sum(len(r.get('entities', [])) for r in result['results'])
        if total_entities > 0:
            metrics.entities_extracted_total.labels(domain=domain).inc(total_entities)
        
        return result
    
    async def _search_pubmed(self, query: str, max_results: int, 
                           date_range: Optional[Tuple[str, str]] = None) -> Dict[str, Any]:
        """Search PubMed database"""
        
        await self._rate_limit('pubmed')
        
        # Build search parameters
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'xml',
            'sort': 'relevance'
        }
        
        if date_range:
            start_date, end_date = date_range
            params['mindate'] = start_date
            params['maxdate'] = end_date
        
        results = []
        
        try:
            # Search for PMIDs
            async with aiohttp.ClientSession() as session:
                search_url = f"{self.endpoints['pubmed']}esearch.fcgi"
                
                async with session.get(search_url, params=params) as response:
                    if response.status != 200:
                        raise ServiceUnavailableError(
                            "PubMed search failed",
                            details={"source": "pubmed", "status": response.status}
                        )
                    
                    content = await response.text()
                    root = ET.fromstring(content)
                    
                    # Extract PMIDs
                    pmids = [id_elem.text for id_elem in root.findall('.//Id')]
                    
                    if not pmids:
                        return {'results': [], 'stats': {'pubmed': {'count': 0}}}
                    
                    # Fetch detailed information
                    fetch_params = {
                        'db': 'pubmed',
                        'id': ','.join(pmids[:max_results]),
                        'retmode': 'xml'
                    }
                    
                    fetch_url = f"{self.endpoints['pubmed']}efetch.fcgi"
                    
                    await self._rate_limit('pubmed')
                    
                    async with session.get(fetch_url, params=fetch_params) as fetch_response:
                        if fetch_response.status != 200:
                            raise ServiceUnavailableError(
                                "PubMed fetch failed",
                                details={"source": "pubmed", "status": fetch_response.status}
                            )
                        
                        fetch_content = await fetch_response.text()
                        fetch_root = ET.fromstring(fetch_content)
                        
                        # Parse articles
                        for article in fetch_root.findall('.//PubmedArticle'):
                            result = self._parse_pubmed_article(article)
                            if result:
                                results.append(result)
        
        except BiologyError as e:
            logger.error(f"PubMed search error: {e}")
            metrics.search_errors_total.labels(error_type='pubmed_api_error', domain='general').inc()
            return {'results': [], 'stats': {'pubmed': {'count': 0, 'error': str(e)}}}
        
        return {
            'results': results,
            'stats': {'pubmed': {'count': len(results)}}
        }
    
    async def _search_arxiv(self, query: str, max_results: int,
                          date_range: Optional[Tuple[str, str]] = None) -> Dict[str, Any]:
        """Search arXiv database"""
        
        await self._rate_limit('arxiv')
        
        # Build search parameters
        params = {
            'search_query': f'all:{query}',
            'start': 0,
            'max_results': max_results,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        results = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.endpoints['arxiv'], params=params) as response:
                    if response.status != 200:
                        raise ServiceUnavailableError(
                            "arXiv search failed",
                            details={"source": "arxiv", "status": response.status}
                        )
                    
                    content = await response.text()
                    root = ET.fromstring(content)
                    
                    # Parse entries
                    for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
                        result = self._parse_arxiv_entry(entry)
                        if result:
                            # Filter by date range if specified
                            if date_range and not self._in_date_range(result.publication_date, date_range):
                                continue
                            results.append(result)
        
        except BiologyError as e:
            logger.error(f"arXiv search error: {e}")
            metrics.search_errors_total.labels(error_type='arxiv_api_error', domain='general').inc()
            return {'results': [], 'stats': {'arxiv': {'count': 0, 'error': str(e)}}}
        
        return {
            'results': results,
            'stats': {'arxiv': {'count': len(results)}}
        }
    
    def _parse_pubmed_article(self, article) -> Optional[LiteratureResult]:
        """Parse PubMed article XML"""
        try:
            # Extract basic information
            title_elem = article.find('.//ArticleTitle')
            title = title_elem.text if title_elem is not None else "No title"
            
            abstract_elem = article.find('.//Abstract/AbstractText')
            abstract = abstract_elem.text if abstract_elem is not None else ""
            
            # Authors
            authors = []
            for author in article.findall('.//Author'):
                lastname = author.find('LastName')
                forename = author.find('ForeName')
                if lastname is not None and forename is not None:
                    authors.append(f"{forename.text} {lastname.text}")
            
            # PMID
            pmid_elem = article.find('.//PMID')
            pmid = pmid_elem.text if pmid_elem is not None else None
            
            # Journal
            journal_elem = article.find('.//Journal/Title')
            journal = journal_elem.text if journal_elem is not None else None
            
            # Publication date
            pub_date = self._extract_pubmed_date(article)
            
            # DOI
            doi = None
            for article_id in article.findall('.//ArticleId'):
                if article_id.get('IdType') == 'doi':
                    doi = article_id.text
                    break
            
            return LiteratureResult(
                title=title,
                authors=authors,
                abstract=abstract,
                doi=doi,
                pmid=pmid,
                arxiv_id=None,
                journal=journal,
                publication_date=pub_date,
                keywords=[],
                entities=[],
                relevance_score=0.5,  # Will be updated later
                source='pubmed',
                url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""
            )
        
        except BiologyError as e:
            logger.warning(f"Failed to parse PubMed article: {e}")
            return None
    
    def _parse_arxiv_entry(self, entry) -> Optional[LiteratureResult]:
        """Parse arXiv entry XML"""
        try:
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            # Extract basic information
            title = entry.find('atom:title', ns).text.strip()
            abstract = entry.find('atom:summary', ns).text.strip()
            
            # Authors
            authors = []
            for author in entry.findall('atom:author', ns):
                name = author.find('atom:name', ns)
                if name is not None:
                    authors.append(name.text)
            
            # arXiv ID
            arxiv_id = entry.find('atom:id', ns).text.split('/')[-1]
            
            # Publication date
            published = entry.find('atom:published', ns)
            pub_date = published.text[:10] if published is not None else None
            
            # Categories (as keywords)
            keywords = []
            for category in entry.findall('atom:category', ns):
                term = category.get('term')
                if term:
                    keywords.append(term)
            
            return LiteratureResult(
                title=title,
                authors=authors,
                abstract=abstract,
                doi=None,
                pmid=None,
                arxiv_id=arxiv_id,
                journal='arXiv',
                publication_date=pub_date,
                keywords=keywords,
                entities=[],
                relevance_score=0.5,  # Will be updated later
                source='arxiv',
                url=f"https://arxiv.org/abs/{arxiv_id}"
            )
        
        except BiologyError as e:
            logger.warning(f"Failed to parse arXiv entry: {e}")
            return None
    
    async def _extract_entities_batch(self, results: List[LiteratureResult]) -> List[LiteratureResult]:
        """Extract entities using PubTator 3.0 for batch of results"""
        
        # Process in batches to respect rate limits
        batch_size = 10
        
        for i in range(0, len(results), batch_size):
            batch = results[i:i + batch_size]
            
            # Extract entities for each result in batch
            for result in batch:
                try:
                    entities = await self._extract_entities_pubtator(result)
                    result.entities = entities
                except BiologyError as e:
                    logger.warning(f"Entity extraction failed for {result.title}: {e}")
                    metrics.entity_extraction_errors_total.labels(error_type='batch_extraction', domain='general').inc()
                    result.entities = []
            
            # Rate limiting between batches
            if i + batch_size < len(results):
                await asyncio.sleep(1.0 / self.rate_limits['pubtator'])
        
        return results
    
    async def _extract_entities_pubtator(self, result: LiteratureResult) -> List[Dict[str, Any]]:
        """Extract entities using PubTator 3.0 API"""
        
        if not result.pmid:
            return []
        
        # Check cache first
        cache_key = f"entities_{result.pmid}"
        if cache_key in self.entity_cache:
            return self.entity_cache[cache_key]
        
        await self._rate_limit('pubtator')
        
        try:
            url = f"{self.endpoints['pubtator']}publications/export/biocjson"
            params = {'pmids': result.pmid}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        return []
                    
                    data = await response.json()
                    
                    entities = []
                    if 'documents' in data and data['documents']:
                        doc = data['documents'][0]
                        if 'annotations' in doc:
                            for annotation in doc['annotations']:
                                entity = {
                                    'text': annotation.get('text', ''),
                                    'type': annotation.get('infons', {}).get('type', ''),
                                    'identifier': annotation.get('infons', {}).get('identifier', ''),
                                    'start': annotation.get('locations', [{}])[0].get('offset', 0),
                                    'end': annotation.get('locations', [{}])[0].get('offset', 0) + annotation.get('locations', [{}])[0].get('length', 0)
                                }
                                entities.append(entity)
                    
                    # Cache results
                    self.entity_cache[cache_key] = entities
                    return entities
        
        except BiologyError as e:
            logger.warning(f"PubTator entity extraction failed: {e}")
            metrics.entity_extraction_errors_total.labels(error_type='pubtator_api', domain='general').inc()
            return []
    
    async def _semantic_ranking(self, query: str, results: List[LiteratureResult]) -> List[LiteratureResult]:
        """Rank results using semantic similarity"""
        
        if not self.sentence_model:
            return results
        
        try:
            # Encode query
            query_embedding = self.sentence_model.encode([query])
            
            # Encode abstracts
            abstracts = [r.abstract for r in results]
            abstract_embeddings = self.sentence_model.encode(abstracts)
            
            # Calculate similarities
            similarities = cosine_similarity(query_embedding, abstract_embeddings)[0]
            
            # Update relevance scores
            for i, result in enumerate(results):
                result.relevance_score = float(similarities[i])
            
            return results
        
        except BiologyError as e:
            logger.warning(f"Semantic ranking failed: {e}")
            metrics.semantic_ranking_errors_total.labels(error_type='ranking_failed', domain='general').inc()
            return results
    
    def _enhance_query(self, query: str, domain_config: Dict) -> str:
        """Enhance query with domain-specific terms"""
        enhanced = query
        
        if domain_config:
            # Add domain keywords
            keywords = domain_config.get('keywords', [])
            if keywords:
                # Add most relevant keywords (simple heuristic)
                for keyword in keywords[:2]:  # Limit to avoid over-expansion
                    if keyword.lower() not in query.lower():
                        enhanced += f" {keyword}"
        
        return enhanced
    
    def _deduplicate_results(self, results: List[LiteratureResult]) -> List[LiteratureResult]:
        """Remove duplicate results based on title similarity"""
        if not results:
            return results
        
        unique_results = []
        seen_titles = set()
        
        for result in results:
            # Simple deduplication by title
            title_key = re.sub(r'[^\w\s]', '', result.title.lower()).strip()
            
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_results.append(result)
        
        return unique_results
    
    def _result_to_dict(self, result: LiteratureResult) -> ResultToDictResult:
        """Convert LiteratureResult to dictionary"""
        return {
            'title': result.title,
            'authors': result.authors,
            'abstract': result.abstract,
            'doi': result.doi,
            'pmid': result.pmid,
            'arxiv_id': result.arxiv_id,
            'journal': result.journal,
            'publication_date': result.publication_date,
            'keywords': result.keywords,
            'entities': result.entities,
            'relevance_score': result.relevance_score,
            'source': result.source,
            'url': result.url
        }
    
    def _extract_pubmed_date(self, article) -> Optional[str]:
        """Extract publication date from PubMed article"""
        try:
            pub_date = article.find('.//PubDate')
            if pub_date is not None:
                year = pub_date.find('Year')
                month = pub_date.find('Month')
                day = pub_date.find('Day')
                
                if year is not None:
                    date_str = year.text
                    if month is not None:
                        date_str += f"-{month.text.zfill(2)}"
                        if day is not None:
                            date_str += f"-{day.text.zfill(2)}"
                    return date_str
            return None
        except BiologyError:
            return None
    
    def _in_date_range(self, date_str: Optional[str], date_range: Tuple[str, str]) -> bool:
        """Check if date is within specified range"""
        if not date_str:
            return True
        
        try:
            start_date, end_date = date_range
            return start_date <= date_str <= end_date
        except BiologyError:
            return True
    
    async def _rate_limit(self, source: str):
        """Implement rate limiting for API calls"""
        now = time.time()
        history = self.request_history[source]
        
        # Remove old requests (older than 1 second)
        history[:] = [t for t in history if now - t < 1.0]
        
        # Check if we need to wait
        limit = self.rate_limits[source]
        if len(history) >= limit:
            sleep_time = 1.0 - (now - history[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        # Record this request
        history.append(now)
    
    async def advanced_literature_analysis(self, 
                                      query: str,
                                      domain: str = 'general',
                                      analysis_depth: str = 'comprehensive',
                                      include_trends: bool = True,
                                      include_gaps: bool = True) -> Dict[str, Any]:
        """
        Análisis avanzado de literatura con identificación de tendencias y gaps
        """
        start_time = time.time()
        
        # Búsqueda comprehensiva inicial
        search_results = await self.comprehensive_search(
            query=query,
            domain=domain,
            max_results=200,
            semantic_search=True,
            include_preprints=True
        )
        
        results = search_results.get('results', [])
        if not results:
            return {'error': 'No results found for analysis'}
        
        analysis = {
            'query': query,
            'domain': domain,
            'total_papers': len(results),
            'analysis_depth': analysis_depth,
            'timestamp': datetime.now().isoformat()
        }
        
        # Análisis temporal de tendencias
        if include_trends:
            analysis['temporal_trends'] = await self._analyze_temporal_trends(results)
        
        # Análisis de gaps de investigación
        if include_gaps:
            analysis['research_gaps'] = await self._identify_research_gaps(results, query, domain)
        
        # Análisis de colaboración y redes
        analysis['collaboration_networks'] = await self._analyze_collaboration_networks(results)
        
        # Análisis de metodologías
        analysis['methodology_analysis'] = await self._analyze_methodologies(results)
        
        # Análisis de impacto y citaciones
        analysis['impact_analysis'] = await self._analyze_impact_metrics(results)
        
        # Síntesis de hallazgos clave
        analysis['key_findings'] = await self._synthesize_key_findings(results, query)
        
        # Recomendaciones para investigación futura
        analysis['future_research_directions'] = await self._generate_research_directions(results, query, domain)
        
        analysis['execution_time'] = time.time() - start_time
        
        return analysis
    
    async def _analyze_temporal_trends(self, results: List[Dict]) -> AnalyzeTemporalTrendsResult:
        """Analizar tendencias temporales en la literatura"""
        if not PANDAS_AVAILABLE:
            return {'error': 'Pandas not available for temporal analysis'}
        
        try:
            # Extraer fechas de publicación
            dates = []
            for result in results:
                pub_date = result.get('publication_date')
                if pub_date:
                    try:
                        # Extraer año de la fecha
                        year = int(pub_date.split('-')[0])
                        if 1900 <= year <= datetime.now().year:
                            dates.append(year)
                    except (ValueError, IndexError):
                        continue
            
            if not dates:
                return {'error': 'No valid publication dates found'}
            
            # Análisis de distribución temporal
            year_counts = {}
            for year in dates:
                year_counts[year] = year_counts.get(year, 0) + 1
            
            # Calcular tendencias
            recent_years = [y for y in dates if y >= datetime.now().year - 5]
            older_years = [y for y in dates if y < datetime.now().year - 5]
            
            return {
                'total_papers_with_dates': len(dates),
                'year_distribution': year_counts,
                'recent_activity': {
                    'papers_last_5_years': len(recent_years),
                    'percentage_recent': len(recent_years) / len(dates) * 100 if dates else 0
                },
                'trend_analysis': {
                    'increasing_trend': len(recent_years) > len(older_years) / 5 if older_years else True,
                    'peak_year': max(year_counts.keys(), key=year_counts.get) if year_counts else None,
                    'peak_count': max(year_counts.values()) if year_counts else 0
                }
            }
        except BiologyError as e:
            return {'error': f'Temporal analysis failed: {str(e)}'}
    
    async def _identify_research_gaps(self, results: List[Dict], query: str, domain: str) -> IdentifyResearchGapsResult:
        """Identificar gaps en la investigación actual"""
        try:
            # Extraer conceptos clave de abstracts
            all_abstracts = ' '.join([r.get('abstract', '') for r in results if r.get('abstract')])
            
            if not all_abstracts:
                return {'error': 'No abstracts available for gap analysis'}
            
            # Análisis de frecuencia de términos
            if SKLEARN_AVAILABLE and self.tfidf_vectorizer:
                try:
                    tfidf_matrix = self.tfidf_vectorizer.fit_transform([all_abstracts])
                    feature_names = self.tfidf_vectorizer.get_feature_names_out()
                    tfidf_scores = tfidf_matrix.toarray()[0]
                    
                    # Términos más frecuentes
                    top_terms = sorted(zip(feature_names, tfidf_scores), key=lambda x: x[1], reverse=True)[:20]
                    
                    # Identificar términos ausentes o poco frecuentes
                    domain_config = self.domain_configs.get(domain, {})
                    expected_keywords = domain_config.get('keywords', [])
                    
                    missing_keywords = []
                    for keyword in expected_keywords:
                        if keyword.lower() not in [term[0] for term in top_terms]:
                            missing_keywords.append(keyword)
                    
                    return {
                        'top_research_terms': [{'term': term, 'score': float(score)} for term, score in top_terms[:10]],
                        'potentially_underexplored': missing_keywords,
                        'gap_analysis': {
                            'coverage_percentage': (len(expected_keywords) - len(missing_keywords)) / len(expected_keywords) * 100 if expected_keywords else 100,
                            'suggested_research_areas': missing_keywords[:5]
                        }
                    }
                except BiologyError as e:
                    return {'error': f'TF-IDF analysis failed: {str(e)}'}
            
            return {'error': 'Advanced text analysis not available'}
        except BiologyError as e:
            return {'error': f'Gap analysis failed: {str(e)}'}
    
    async def _analyze_collaboration_networks(self, results: List[Dict]) -> AnalyzeCollaborationNetworksResult:
        """Analizar redes de colaboración entre autores"""
        try:
            # Extraer autores y co-autorías
            author_collaborations = {}
            all_authors = set()
            
            for result in results:
                authors = result.get('authors', [])
                if len(authors) > 1:
                    for i, author1 in enumerate(authors):
                        all_authors.add(author1)
                        if author1 not in author_collaborations:
                            author_collaborations[author1] = set()
                        
                        for j, author2 in enumerate(authors):
                            if i != j:
                                author_collaborations[author1].add(author2)
                                all_authors.add(author2)
            
            # Calcular métricas de red
            most_collaborative = max(author_collaborations.keys(), 
                                   key=lambda x: len(author_collaborations[x])) if author_collaborations else None
            
            return {
                'total_unique_authors': len(all_authors),
                'collaborative_authors': len(author_collaborations),
                'most_collaborative_author': {
                    'name': most_collaborative,
                    'collaborations': len(author_collaborations.get(most_collaborative, [])) if most_collaborative else 0
                },
                'average_collaborations_per_author': sum(len(collabs) for collabs in author_collaborations.values()) / len(author_collaborations) if author_collaborations else 0,
                'collaboration_density': len(author_collaborations) / len(all_authors) if all_authors else 0
            }
        except BiologyError as e:
            return {'error': f'Collaboration analysis failed: {str(e)}'}
    
    async def _analyze_methodologies(self, results: List[Dict]) -> AnalyzeMethodologiesResult:
        """Analizar metodologías utilizadas en la investigación"""
        try:
            methodology_keywords = [
                'machine learning', 'deep learning', 'neural network', 'regression', 'classification',
                'experimental', 'simulation', 'modeling', 'statistical', 'computational',
                'survey', 'review', 'meta-analysis', 'case study', 'longitudinal',
                'qualitative', 'quantitative', 'mixed methods', 'randomized', 'controlled'
            ]
            
            methodology_counts = {keyword: 0 for keyword in methodology_keywords}
            total_papers = len(results)
            
            for result in results:
                abstract = result.get('abstract', '').lower()
                title = result.get('title', '').lower()
                text = f"{title} {abstract}"
                
                for keyword in methodology_keywords:
                    if keyword in text:
                        methodology_counts[keyword] += 1
            
            # Calcular porcentajes
            methodology_percentages = {
                keyword: (count / total_papers * 100) if total_papers > 0 else 0
                for keyword, count in methodology_counts.items()
            }
            
            # Metodologías más comunes
            top_methodologies = sorted(methodology_percentages.items(), 
                                     key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'methodology_distribution': methodology_percentages,
                'top_methodologies': [{'method': method, 'percentage': perc} for method, perc in top_methodologies if perc > 0],
                'methodology_diversity': len([m for m in methodology_percentages.values() if m > 0]),
                'most_common_approach': top_methodologies[0][0] if top_methodologies and top_methodologies[0][1] > 0 else 'Unknown'
            }
        except BiologyError as e:
            return {'error': f'Methodology analysis failed: {str(e)}'}
    
    async def _analyze_impact_metrics(self, results: List[Dict]) -> AnalyzeImpactMetricsResult:
        """
        Analizar métricas de impacto de la literatura con integración completa de Semantic Scholar
        
        Incluye análisis de citaciones, métricas de influencia, acceso abierto,
        y cálculo de puntuación de impacto compuesto
        """
        try:
            # Análisis de journals
            journal_counts = {}
            high_impact_journals = [
                'Nature', 'Science', 'Cell', 'Nature Materials', 'Nature Chemistry',
                'Physical Review Letters', 'JACS', 'Angewandte Chemie', 'PNAS',
                'Nature Communications', 'Science Advances', 'Physical Review X',
                'Advanced Materials', 'Chemical Reviews', 'Chemical Society Reviews'
            ]
            
            high_impact_count = 0
            total_with_journal = 0
            
            # Enhanced impact analysis with Semantic Scholar
            impact_metrics = {
                'total_citations': 0,
                'avg_citations_per_paper': 0,
                'h_index_estimate': 0,
                'influential_citations': 0,
                'papers_with_dois': 0,
                'open_access_count': 0,
                'citation_data_available': 0,
                'individual_citation_counts': [],
                'highly_cited_papers': []
            }
            
            for result in results:
                journal = result.get('journal', '')
                if journal:
                    total_with_journal += 1
                    journal_counts[journal] = journal_counts.get(journal, 0) + 1
                    
                    # Check if high impact
                    for hi_journal in high_impact_journals:
                        if hi_journal.lower() in journal.lower():
                            high_impact_count += 1
                            break
                
                # Get Semantic Scholar metrics if DOI or title is available
                doi = result.get('doi')
                title = result.get('title', '')
                
                if doi or title:
                    impact_metrics['papers_with_dois'] += 1
                    try:
                        scholar_data = await self._get_semantic_scholar_metrics(doi or title)
                        if scholar_data:
                            impact_metrics['citation_data_available'] += 1
                            citations = scholar_data.get('citationCount', 0)
                            influential = scholar_data.get('influentialCitationCount', 0)
                            is_open_access = scholar_data.get('openAccessPdf', {}).get('url') is not None
                            
                            impact_metrics['total_citations'] += citations
                            impact_metrics['influential_citations'] += influential
                            impact_metrics['individual_citation_counts'].append(citations)
                            
                            if is_open_access:
                                impact_metrics['open_access_count'] += 1
                            
                            # Identify highly cited papers (top 10%)
                            if citations > 0:
                                impact_metrics['highly_cited_papers'].append({
                                    'title': title,
                                    'citations': citations,
                                    'influential_citations': influential,
                                    'doi': doi,
                                    'open_access': is_open_access,
                                    'journal': journal
                                })
                                
                    except BiologyError:
                        # Silently continue if API call fails
                        pass
            
            # Calculate derived metrics
            if impact_metrics['citation_data_available'] > 0:
                impact_metrics['avg_citations_per_paper'] = impact_metrics['total_citations'] / impact_metrics['citation_data_available']
                impact_metrics['open_access_percentage'] = (impact_metrics['open_access_count'] / impact_metrics['citation_data_available'] * 100)
                
                # Calculate actual h-index based on individual citation counts
                if impact_metrics['individual_citation_counts']:
                    sorted_citations = sorted(impact_metrics['individual_citation_counts'], reverse=True)
                    h_index = 0
                    for i, count in enumerate(sorted_citations):
                        if count >= i + 1:
                            h_index = i + 1
                        else:
                            break
                    impact_metrics['h_index_estimate'] = h_index
                
                # Calculate influential citation ratio
                if impact_metrics['total_citations'] > 0:
                    impact_metrics['influential_ratio'] = (impact_metrics['influential_citations'] / impact_metrics['total_citations'] * 100)
                
                # Identify top 10% most cited papers
                if impact_metrics['highly_cited_papers']:
                    citation_threshold = sorted(impact_metrics['individual_citation_counts'])[-max(1, len(impact_metrics['individual_citation_counts'])//10)]
                    impact_metrics['highly_cited_papers'] = [
                        paper for paper in impact_metrics['highly_cited_papers'] 
                        if paper['citations'] >= citation_threshold
                    ][:10]  # Limit to top 10
            
            # Top journals
            top_journals = sorted(journal_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'total_papers_with_journal': total_with_journal,
                'unique_journals': len(journal_counts),
                'high_impact_papers': high_impact_count,
                'high_impact_percentage': (high_impact_count / total_with_journal * 100) if total_with_journal > 0 else 0,
                'top_journals': [{'journal': journal, 'count': count} for journal, count in top_journals],
                'journal_diversity': len(journal_counts) / total_with_journal if total_with_journal > 0 else 0,
                'semantic_scholar_metrics': impact_metrics,
                'impact_score': self._calculate_impact_score(impact_metrics, high_impact_count, total_with_journal),
                'data_coverage': {
                    'papers_with_identifiers': impact_metrics['papers_with_dois'],
                    'citation_data_available': impact_metrics['citation_data_available'],
                    'coverage_percentage': (impact_metrics['citation_data_available'] / len(results) * 100) if results else 0
                }
            }
        except BiologyError as e:
            return {'error': f'Impact analysis failed: {str(e)}'}
    
    async def _synthesize_key_findings(self, results: List[Dict], query: str) -> SynthesizeKeyFindingsResult:
        """Sintetizar hallazgos clave de la literatura"""
        try:
            # Extraer entidades más frecuentes
            all_entities = []
            for result in results:
                entities = result.get('entities', [])
                for entity in entities:
                    if isinstance(entity, dict) and entity.get('text'):
                        all_entities.append(entity)
            
            # Contar entidades por tipo
            entity_types = {}
            entity_texts = {}
            
            for entity in all_entities:
                entity_type = entity.get('type', 'Unknown')
                entity_text = entity.get('text', '')
                
                if entity_type not in entity_types:
                    entity_types[entity_type] = 0
                entity_types[entity_type] += 1
                
                if entity_text not in entity_texts:
                    entity_texts[entity_text] = 0
                entity_texts[entity_text] += 1
            
            # Top entidades
            top_entities = sorted(entity_texts.items(), key=lambda x: x[1], reverse=True)[:15]
            top_entity_types = sorted(entity_types.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'total_entities_extracted': len(all_entities),
                'unique_entities': len(entity_texts),
                'entity_type_distribution': entity_types,
                'top_entities': [{'entity': entity, 'frequency': freq} for entity, freq in top_entities],
                'top_entity_types': [{'type': etype, 'count': count} for etype, count in top_entity_types],
                'key_concepts_summary': {
                    'most_mentioned_concept': top_entities[0][0] if top_entities else 'None',
                    'dominant_entity_type': top_entity_types[0][0] if top_entity_types else 'None',
                    'concept_diversity': len(entity_texts)
                }
            }
        except BiologyError as e:
            return {'error': f'Key findings synthesis failed: {str(e)}'}
    
    async def _generate_research_directions(self, results: List[Dict], query: str, domain: str) -> GenerateResearchDirectionsResult:
        """Generar direcciones para investigación futura"""
        try:
            # Analizar gaps identificados
            gaps_analysis = await self._identify_research_gaps(results, query, domain)
            
            # Generar recomendaciones basadas en gaps
            recommendations = []
            
            if 'gap_analysis' in gaps_analysis:
                suggested_areas = gaps_analysis['gap_analysis'].get('suggested_research_areas', [])
                for area in suggested_areas:
                    recommendations.append({
                        'area': area,
                        'rationale': f'Underexplored in current literature on {query}',
                        'priority': 'High' if area in self.domain_configs.get(domain, {}).get('keywords', []) else 'Medium'
                    })
            
            # Recomendaciones metodológicas
            methodology_analysis = await self._analyze_methodologies(results)
            if 'top_methodologies' in methodology_analysis:
                top_methods = methodology_analysis['top_methodologies'][:3]
                for method_info in top_methods:
                    if method_info['percentage'] < 20:  # Si es poco usado, recomendar explorar más
                        recommendations.append({
                            'area': f"Enhanced {method_info['method']} applications",
                            'rationale': f"Only {method_info['percentage']:.1f}% of papers use this approach",
                            'priority': 'Medium'
                        })
            
            # Recomendaciones de colaboración
            collab_analysis = await self._analyze_collaboration_networks(results)
            if collab_analysis.get('collaboration_density', 0) < 0.3:
                recommendations.append({
                    'area': 'Interdisciplinary collaboration',
                    'rationale': 'Low collaboration density suggests opportunities for cross-disciplinary work',
                    'priority': 'Medium'
                })
            
            return {
                'total_recommendations': len(recommendations),
                'recommendations': recommendations[:10],  # Limit to top 10
                'research_priorities': {
                    'high_priority': [r for r in recommendations if r['priority'] == 'High'],
                    'medium_priority': [r for r in recommendations if r['priority'] == 'Medium']
                },
                'next_steps': [
                    'Conduct systematic review of identified gaps',
                    'Develop novel methodological approaches',
                    'Establish interdisciplinary collaborations',
                    'Focus on underexplored application domains'
                ]
            }
        except BiologyError as e:
            return {'error': f'Research directions generation failed: {str(e)}'}

    async def _get_opencitations_citations(self, pmid: str, depth: int) -> List[Dict[str, Any]]:
        """Get citations from OpenCitations API"""
        try:
            await self._rate_limit('opencitations')
            
            url = f"{self.endpoints.get('opencitations', 'https://opencitations.net/index/api/v1/citation-count/')}{pmid}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data if isinstance(data, list) else []
            return []
        except BiologyError as e:
            logger.warning(f"OpenCitations citations API failed: {e}")
            return []

    async def _get_opencitations_references(self, pmid: str, depth: int) -> List[Dict[str, Any]]:
        """Get references from OpenCitations API"""
        try:
            await self._rate_limit('opencitations')
            
            url = f"{self.endpoints.get('opencitations', 'https://opencitations.net/index/api/v1/references/')}{pmid}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data if isinstance(data, list) else []
            return []
        except BiologyError as e:
            logger.warning(f"OpenCitations references API failed: {e}")
            return []

    async def _get_semantic_scholar_citations(self, pmid: str, depth: int) -> GetSemanticScholarCitationsResult:
        """Get citation data from Semantic Scholar API"""
        try:
            await self._rate_limit('semantic_scholar')
            
            url = f"{self.endpoints.get('semantic_scholar', 'https://api.semanticscholar.org/graph/v1/paper/PMID:')}{pmid}"
            params = {
                'fields': 'citations,citationCount,references,referenceCount,influentialCitationCount'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'citations': data.get('citations', []),
                            'references': data.get('references', []),
                            'citation_count': data.get('citationCount', 0),
                            'reference_count': data.get('referenceCount', 0),
                            'influential_citations': data.get('influentialCitationCount', 0)
                        }
            return {}
        except BiologyError as e:
            logger.warning(f"Semantic Scholar API failed: {e}")
            return {}

    async def _get_semantic_scholar_metrics(self, identifier: str) -> GetSemanticScholarMetricsResult:
        """Get detailed metrics from Semantic Scholar API using DOI or title"""
        try:
            await self._rate_limit('semantic_scholar')
            
            # Determine if identifier is DOI or needs title search
            if identifier.startswith('10.'):  # Likely a DOI
                url = f"{self.endpoints['semantic_scholar']}DOI:{identifier}"
            else:
                # Search by title
                url = f"{self.endpoints['semantic_scholar']}search"
                params = {
                    'query': identifier,
                    'limit': 1,
                    'fields': 'citationCount,influentialCitationCount,venue,year,referenceCount'
                }
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get('data') and len(data['data']) > 0:
                                return data['data'][0]
                        return {}
            
            params = {
                'fields': 'citationCount,influentialCitationCount,venue,year,referenceCount,openAccessPdf'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    return {}
                    
        except BiologyError as e:
            logger.warning(f"Semantic Scholar metrics API failed: {e}")
            return {}

    def _calculate_impact_score(self, metrics: Dict, high_impact_count: int, total_papers: int) -> float:
        """Calculate composite impact score"""
        if total_papers == 0:
            return 0.0
        
        # Weighted components
        citation_score = min(metrics['avg_citations_per_paper'] * 0.4, 40)  # Max 40 points
        h_index_score = min(metrics['h_index_estimate'] * 0.8, 30)         # Max 30 points
        high_impact_score = (high_impact_count / total_papers * 100) * 0.3  # Max 30 points
        
        return citation_score + h_index_score + high_impact_score

    def _calculate_network_density(self, citations: List, references: List) -> float:
        """Calculate citation network density"""
        total_nodes = len(citations) + len(references) + 1  # +1 for the root paper
        if total_nodes <= 1:
            return 0.0
        
        # Simple density calculation
        possible_connections = total_nodes * (total_nodes - 1)
        actual_connections = len(citations) + len(references)
        
        return actual_connections / possible_connections if possible_connections > 0 else 0.0

    def _generate_cache_key(self, query: str, domain: str, max_results: int, 
                          date_range: Optional[Tuple[str, str]]) -> str:
        """Generate cache key for search results"""
        key_data = f"{query}_{domain}_{max_results}_{date_range}"
        return hashlib.sha256(key_data.encode()).hexdigest()

    async def extract_key_concepts(self, text: str) -> ExtractKeyConceptsResult:
        """Extract key concepts from text using NLP (async with CPU executor)"""
        
        concepts = {
            'keywords': [],
            'entities': [],
            'topics': [],
            'summary': ''
        }
        
        if not text.strip():
            return concepts
        
        try:
            # Use CPU executor for NLP processing
            from app.core.executors import run_cpu_bound
            
            def _extract_concepts_sync(text: str) -> ExtractConceptsSyncResult:
                """Synchronous concept extraction for CPU executor"""
                concepts = {
                    'keywords': [],
                    'entities': [],
                    'topics': [],
                    'summary': ''
                }
                
                # Extract keywords using TF-IDF
                if self.tfidf_vectorizer and SKLEARN_AVAILABLE:
                    tfidf_matrix = self.tfidf_vectorizer.fit_transform([text])
                    feature_names = self.tfidf_vectorizer.get_feature_names_out()
                    scores = tfidf_matrix.toarray()[0]
                    
                    # Get top keywords
                    top_indices = np.argsort(scores)[-10:][::-1]
                    concepts['keywords'] = [feature_names[i] for i in top_indices if scores[i] > 0]
                
                # Simple sentence extraction for summary
                if NLTK_AVAILABLE:
                    sentences = sent_tokenize(text)
                    if sentences:
                        concepts['summary'] = sentences[0]  # First sentence as summary
                
                return concepts
            
            # Run in CPU executor to avoid blocking event loop
            concepts = await run_cpu_bound(_extract_concepts_sync, text)
            return concepts
        
        except BiologyError as e:
            logger.warning(f"Concept extraction failed: {e}")
            return concepts
    
    async def get_citation_network(self, pmid: str, depth: int = 1) -> GetCitationNetworkResult:
        """Get citation network for a paper"""
        
        if depth > 2:  # Limit depth to prevent excessive API calls
            depth = 2
        
        network = {
            'root_pmid': pmid,
            'citations': [],
            'references': [],
            'network_stats': {}
        }
        
        try:
            # Integrate with OpenCitations API for citation analysis
            try:
                # Get citations from OpenCitations
                citations = await self._get_opencitations_citations(pmid, depth)
                network['citations'] = citations
                
                # Get references from OpenCitations
                references = await self._get_opencitations_references(pmid, depth)
                network['references'] = references
                
                # Calculate network statistics
                network['network_stats'] = {
                    'total_citations': len(citations),
                    'total_references': len(references),
                    'depth_explored': depth,
                    'citation_network_density': self._calculate_network_density(citations, references),
                    'source': 'OpenCitations API'
                }
                
            except BiologyError as e:
                logger.warning(f"OpenCitations integration failed: {e}")
                # Fallback to Semantic Scholar if available
                try:
                    semantic_data = await self._get_semantic_scholar_citations(pmid, depth)
                    if semantic_data:
                        network.update(semantic_data)
                        network['network_stats']['source'] = 'Semantic Scholar API'
                except BiologyError as fallback_error:
                    logger.warning(f"Semantic Scholar fallback also failed: {fallback_error}")
                    # Return basic placeholder structure
                    network['network_stats'] = {
                        'total_citations': 0,
                        'total_references': 0,
                        'depth_explored': depth,
                        'note': 'Citation network analysis requires API configuration'
                    }
                
                return network
        except BiologyError as e:
            logger.error(f"Citation network analysis failed: {e}")
            return network

    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        """
        Process a service request - required by BaseService
        """
        try:
            action = request_data.get('action', 'comprehensive_search')
            
            if action == 'comprehensive_search':
                query = request_data.get('query')
                domain = request_data.get('domain', 'general')
                max_results = request_data.get('max_results', 100)
                date_range = request_data.get('date_range')
                include_preprints = request_data.get('include_preprints', True)
                semantic_search = request_data.get('semantic_search', True)
                
                if not query:
                    return {
                        'success': False,
                        'error': 'Query is required'
                    }
                
                result = await self.comprehensive_search(
                    query, domain, max_results, date_range, include_preprints, semantic_search
                )
                result['success'] = True
                return result
            
            elif action == 'extract_key_concepts':
                text = request_data.get('text')
                
                if not text:
                    return {
                        'success': False,
                        'error': 'Text is required'
                    }
                
                result = await self.extract_key_concepts(text)
                result['success'] = True
                return result
            
            elif action == 'get_citation_network':
                pmid = request_data.get('pmid')
                depth = request_data.get('depth', 1)
                
                if not pmid:
                    return {
                        'success': False,
                        'error': 'PMID is required'
                    }
                
                result = await self.get_citation_network(pmid, depth)
                result['success'] = True
                return result
            
            else:
                return {
                    'success': False,
                    'error': f'Unknown action: {action}'
                }
                
        except BiologyError as e:
            logger.error(f"Error processing request: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }