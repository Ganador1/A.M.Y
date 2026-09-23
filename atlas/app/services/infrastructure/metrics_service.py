"""
Metrics Service for Literature Mining Service
Provides Prometheus metrics for monitoring and observability
"""

from prometheus_client import Counter, Gauge, Histogram, Summary, generate_latest
from prometheus_client.exposition import start_http_server
import time
from typing import Dict, Any, Optional
import logging
import httpx
from app.exceptions.domain.biology import BiologyError

logger = logging.getLogger(__name__)

class LiteratureMiningMetrics:
    """Metrics collection for Literature Mining Service"""
    
    def __init__(self):
        # API Call Metrics
        self.api_calls_total = Counter(
            'literature_mining_api_calls_total',
            'Total API calls made by literature mining service',
            ['api_name', 'status']
        )
        
        self.api_call_duration = Histogram(
            'literature_mining_api_call_duration_seconds',
            'Duration of API calls in seconds',
            ['api_name']
        )
        
        # Search Metrics
        self.searches_total = Counter(
            'literature_mining_searches_total',
            'Total literature searches performed',
            ['domain', 'status']
        )
        
        self.search_duration = Histogram(
            'literature_mining_search_duration_seconds',
            'Duration of literature searches in seconds',
            ['domain']
        )
        
        # Processing Metrics
        self.papers_processed_total = Counter(
            'literature_mining_papers_processed_total',
            'Total papers processed',
            ['processing_stage']
        )
        
        self.processing_duration = Histogram(
            'literature_mining_processing_duration_seconds',
            'Duration of paper processing stages in seconds',
            ['processing_stage']
        )
        
        # Entity Extraction Metrics
        self.entities_extracted_total = Counter(
            'literature_mining_entities_extracted_total',
            'Total entities extracted from papers',
            ['entity_type']
        )
        
        # Impact Metrics
        self.avg_citations = Gauge(
            'literature_mining_avg_citations',
            'Average citations per paper in search results'
        )
        
        self.h_index_estimate = Gauge(
            'literature_mining_h_index_estimate',
            'Estimated h-index of search results'
        )
        
        self.impact_score = Gauge(
            'literature_mining_impact_score',
            'Composite impact score of search results'
        )
        
        # Cache Metrics
        self.cache_hits_total = Counter(
            'literature_mining_cache_hits_total',
            'Total cache hits',
            ['cache_type']
        )
        
        self.cache_misses_total = Counter(
            'literature_mining_cache_misses_total',
            'Total cache misses',
            ['cache_type']
        )
        
        # Error Metrics
        self.errors_total = Counter(
            'literature_mining_errors_total',
            'Total errors encountered',
            ['error_type', 'component']
        )
        
        # Rate Limit Metrics
        self.rate_limited_requests = Counter(
            'literature_mining_rate_limited_requests_total',
            'Total requests that were rate limited',
            ['api_name']
        )
    
    def start_metrics_server(self, port: int = 8000):
        """Start Prometheus metrics HTTP server"""
        try:
            start_http_server(port)
            logger.info(f"Prometheus metrics server started on port {port}")
            return True
        except BiologyError as e:
            logger.error(f"Failed to start metrics server: {e}")
            return False
    
    def record_api_call(self, api_name: str, duration: float, success: bool = True):
        """Record API call metrics"""
        status = 'success' if success else 'failure'
        self.api_calls_total.labels(api_name=api_name, status=status).inc()
        self.api_call_duration.labels(api_name=api_name).observe(duration)
        
        if not success:
            self.errors_total.labels(error_type='api_call', component=api_name).inc()
    
    def record_search(self, domain: str, duration: float, papers_count: int, success: bool = True):
        """Record search operation metrics"""
        status = 'success' if success else 'failure'
        self.searches_total.labels(domain=domain, status=status).inc()
        self.search_duration.labels(domain=domain).observe(duration)
        self.papers_processed_total.labels(processing_stage='search').inc(papers_count)
        
        if not success:
            self.errors_total.labels(error_type='search', component='search_engine').inc()
    
    def record_processing_stage(self, stage: str, duration: float, items_processed: int = 1):
        """Record processing stage metrics"""
        self.processing_duration.labels(processing_stage=stage).observe(duration)
        self.papers_processed_total.labels(processing_stage=stage).inc(items_processed)
    
    def record_entity_extraction(self, entity_type: str, count: int = 1):
        """Record entity extraction metrics"""
        self.entities_extracted_total.labels(entity_type=entity_type).inc(count)
    
    def record_impact_metrics(self, metrics: Dict[str, Any]):
        """Record impact analysis metrics"""
        if 'avg_citations_per_paper' in metrics:
            self.avg_citations.set(metrics['avg_citations_per_paper'])
        
        if 'h_index_estimate' in metrics:
            self.h_index_estimate.set(metrics['h_index_estimate'])
        
        if 'impact_score' in metrics:
            self.impact_score.set(metrics['impact_score'])
    
    def record_cache_operation(self, cache_type: str, hit: bool):
        """Record cache operation metrics"""
        if hit:
            self.cache_hits_total.labels(cache_type=cache_type).inc()
        else:
            self.cache_misses_total.labels(cache_type=cache_type).inc()
    
    def record_error(self, error_type: str, component: str):
        """Record error metrics"""
        self.errors_total.labels(error_type=error_type, component=component).inc()
    
    def record_rate_limit(self, api_name: str):
        """Record rate limit event"""
        self.rate_limited_requests.labels(api_name=api_name).inc()
    
    def get_metrics(self) -> str:
        """Get current metrics in Prometheus format"""
        return generate_latest().decode('utf-8')

# Global metrics instance
metrics = LiteratureMiningMetrics()