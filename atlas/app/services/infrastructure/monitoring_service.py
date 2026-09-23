"""
AXIOM META 4 - Monitoring and Metrics Service
============================================

Advanced monitoring and observability service for AXIOM scientific platform.

Features:
- Prometheus metrics collection
- System resource monitoring
- Service health checks
- Performance analytics
- Alert management
- Grafana dashboard integration

Dependencies:
- prometheus_client
- psutil
- grafana_api
- asyncio
- logging
"""

import asyncio
import logging
import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
from grafana_api.grafana_face import GrafanaFace
import json
import httpx
from app.exceptions.domain.biology import BiologyError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MetricConfig:
    """Configuration for monitoring metrics"""
    collection_interval: int = 30  # seconds
    retention_days: int = 30
    alert_thresholds: Dict[str, float] = None
    grafana_url: Optional[str] = None
    grafana_token: Optional[str] = None

@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    network_io: Dict[str, int]
    timestamp: datetime

@dataclass
class ServiceMetrics:
    """Service-specific metrics"""
    service_name: str
    request_count: int
    response_time: float
    error_rate: float
    active_connections: int
    timestamp: datetime

from app.services.base_service import BaseService

class MonitoringService(BaseService):
    """
    Advanced monitoring and metrics collection service
    
    Provides comprehensive system and application monitoring with:
    - Real-time metrics collection
    - Prometheus integration
    - Grafana dashboard management
    - Alert system
    - Performance analytics
    """
    
    def __init__(self, config: MetricConfig = None):
        """Initialize monitoring service"""
        super().__init__("MonitoringService")
        self.config = config or MetricConfig()
        self.registry = CollectorRegistry()
        self.grafana_client = None
        
        # Initialize Prometheus metrics
        self._init_prometheus_metrics()
        
        # Initialize Grafana client if configured
        if self.config.grafana_url and self.config.grafana_token:
            self._init_grafana_client()
        
        # Metrics storage
        self.system_metrics_history: List[SystemMetrics] = []
        self.service_metrics_history: Dict[str, List[ServiceMetrics]] = {}
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_task = None
        
        logger.info("Monitoring service initialized")
    
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a service request"""
        try:
            action = request_data.get("action")
            if action == "get_metrics":
                return {"success": True, "data": self.get_current_metrics()}
            elif action == "get_history":
                return {"success": True, "data": {
                    "system": [m.__dict__ for m in self.system_metrics_history],
                    "services": {k: [m.__dict__ for m in v] for k, v in self.service_metrics_history.items()}
                }}
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return self.handle_error(e, "process_request")

    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics collectors"""
        # System metrics
        self.cpu_usage = Gauge('system_cpu_usage_percent', 'CPU usage percentage', registry=self.registry)
        self.memory_usage = Gauge('system_memory_usage_percent', 'Memory usage percentage', registry=self.registry)
        self.disk_usage = Gauge('system_disk_usage_percent', 'Disk usage percentage', registry=self.registry)
        
        # Network metrics
        self.network_bytes_sent = Counter('network_bytes_sent_total', 'Total bytes sent', registry=self.registry)
        self.network_bytes_recv = Counter('network_bytes_received_total', 'Total bytes received', registry=self.registry)
        
        # Service metrics
        self.request_count = Counter('service_requests_total', 'Total service requests', ['service'], registry=self.registry)
        self.response_time = Histogram('service_response_time_seconds', 'Service response time', ['service'], registry=self.registry)
        self.error_rate = Gauge('service_error_rate', 'Service error rate', ['service'], registry=self.registry)
        
        # AXIOM-specific metrics
        self.causal_discoveries = Counter('axiom_causal_discoveries_total', 'Total causal discoveries', registry=self.registry)
        self.federated_rounds = Counter('axiom_federated_rounds_total', 'Total federated learning rounds', registry=self.registry)
        self.synthetic_data_generated = Counter('axiom_synthetic_data_generated_total', 'Total synthetic data generated', registry=self.registry)
        self.multimodal_analyses = Counter('axiom_multimodal_analyses_total', 'Total multimodal analyses', registry=self.registry)
        self.quantum_circuits = Counter('axiom_quantum_circuits_total', 'Total quantum circuits executed', registry=self.registry)
    
    def _init_grafana_client(self):
        """Initialize Grafana API client"""
        try:
            self.grafana_client = GrafanaFace(
                auth=self.config.grafana_token,
                host=self.config.grafana_url
            )
            logger.info("Grafana client initialized")
        except BiologyError as e:
            logger.error(f"Failed to initialize Grafana client: {e}")
    
    async def start_monitoring(self):
        """Start continuous monitoring"""
        if self.is_monitoring:
            logger.warning("Monitoring already running")
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Monitoring started")
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Clean old metrics
                self._cleanup_old_metrics()
                
                # Check alerts
                await self._check_alerts()
                
                # Wait for next collection
                await asyncio.sleep(self.config.collection_interval)
                
            except BiologyError as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Brief pause on error
    
    async def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.cpu_usage.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.memory_usage.set(memory_percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.disk_usage.set(disk_percent)
            
            # Network I/O
            network = psutil.net_io_counters()
            self.network_bytes_sent.inc(network.bytes_sent)
            self.network_bytes_recv.inc(network.bytes_recv)
            
            # Store metrics
            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_usage=disk_percent,
                network_io={
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv
                },
                timestamp=datetime.now()
            )
            
            self.system_metrics_history.append(metrics)
            
        except BiologyError as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    def record_service_metric(self, service_name: str, response_time: float, 
                            error_occurred: bool = False):
        """Record service-specific metrics"""
        try:
            # Update Prometheus metrics
            self.request_count.labels(service=service_name).inc()
            self.response_time.labels(service=service_name).observe(response_time)
            
            # Calculate error rate
            if service_name not in self.service_metrics_history:
                self.service_metrics_history[service_name] = []
            
            recent_metrics = [m for m in self.service_metrics_history[service_name] 
                            if m.timestamp > datetime.now() - timedelta(minutes=5)]
            
            error_count = sum(1 for m in recent_metrics if m.error_rate > 0)
            total_count = len(recent_metrics) + 1
            current_error_rate = error_count / total_count if total_count > 0 else 0
            
            if error_occurred:
                current_error_rate = (error_count + 1) / total_count
            
            self.error_rate.labels(service=service_name).set(current_error_rate)
            
            # Store service metrics
            metrics = ServiceMetrics(
                service_name=service_name,
                request_count=1,
                response_time=response_time,
                error_rate=1.0 if error_occurred else 0.0,
                active_connections=len(recent_metrics),
                timestamp=datetime.now()
            )
            
            self.service_metrics_history[service_name].append(metrics)
            
        except BiologyError as e:
            logger.error(f"Error recording service metrics: {e}")
    
    def record_axiom_service_metric(self, service_name: str, operation: str, 
                                   response_time: float, error_occurred: bool = False):
        """Record metrics for AXIOM services"""
        try:
            # Record request
            self.axiom_requests.labels(
                service=service_name, 
                operation=operation
            ).inc()
            
            # Record response time
            self.axiom_response_time.labels(
                service=service_name, 
                operation=operation
            ).observe(response_time)
            
            # Record error if occurred
            if error_occurred:
                self.axiom_errors.labels(
                    service=service_name, 
                    operation=operation
                ).inc()
            
            logger.debug(f"Recorded metric for {service_name}.{operation}: {response_time}s")
            
        except BiologyError as e:
            logger.error(f"Error recording AXIOM service metric: {e}")

    def record_axiom_metric(self, metric_type: str, value: int = 1):
        """Record AXIOM-specific metrics"""
        try:
            if metric_type == "causal_discovery":
                self.causal_discoveries.inc(value)
            elif metric_type == "federated_round":
                self.federated_rounds.inc(value)
            elif metric_type == "synthetic_data":
                self.synthetic_data_generated.inc(value)
            elif metric_type == "multimodal_analysis":
                self.multimodal_analyses.inc(value)
            elif metric_type == "quantum_circuit":
                self.quantum_circuits.inc(value)
            else:
                logger.warning(f"Unknown AXIOM metric type: {metric_type}")
                
        except BiologyError as e:
            logger.error(f"Error recording AXIOM metric: {e}")
    
    async def _check_alerts(self):
        """Check for alert conditions"""
        if not self.config.alert_thresholds:
            return
        
        try:
            latest_metrics = self.system_metrics_history[-1] if self.system_metrics_history else None
            if not latest_metrics:
                return
            
            alerts = []
            
            # CPU alert
            if latest_metrics.cpu_percent > self.config.alert_thresholds.get('cpu', 80):
                alerts.append(f"High CPU usage: {latest_metrics.cpu_percent:.1f}%")
            
            # Memory alert
            if latest_metrics.memory_percent > self.config.alert_thresholds.get('memory', 85):
                alerts.append(f"High memory usage: {latest_metrics.memory_percent:.1f}%")
            
            # Disk alert
            if latest_metrics.disk_usage > self.config.alert_thresholds.get('disk', 90):
                alerts.append(f"High disk usage: {latest_metrics.disk_usage:.1f}%")
            
            if alerts:
                logger.warning(f"System alerts: {', '.join(alerts)}")
                
        except BiologyError as e:
            logger.error(f"Error checking alerts: {e}")
    
    def _cleanup_old_metrics(self):
        """Clean up old metrics based on retention policy"""
        cutoff_time = datetime.now() - timedelta(days=self.config.retention_days)
        
        # Clean system metrics
        self.system_metrics_history = [
            m for m in self.system_metrics_history 
            if m.timestamp > cutoff_time
        ]
        
        # Clean service metrics
        for service_name in self.service_metrics_history:
            self.service_metrics_history[service_name] = [
                m for m in self.service_metrics_history[service_name]
                if m.timestamp > cutoff_time
            ]
    
    def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics in text format"""
        return generate_latest(self.registry).decode('utf-8')
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        if not self.system_metrics_history:
            return {"status": "no_data"}
        
        latest = self.system_metrics_history[-1]
        
        return {
            "status": "healthy",
            "timestamp": latest.timestamp.isoformat(),
            "cpu_percent": latest.cpu_percent,
            "memory_percent": latest.memory_percent,
            "disk_usage": latest.disk_usage,
            "network_io": latest.network_io,
            "monitoring_active": self.is_monitoring
        }
    
    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get service-specific status"""
        if service_name not in self.service_metrics_history:
            return {"status": "no_data", "service": service_name}
        
        metrics = self.service_metrics_history[service_name]
        if not metrics:
            return {"status": "no_data", "service": service_name}
        
        recent_metrics = [m for m in metrics 
                         if m.timestamp > datetime.now() - timedelta(minutes=5)]
        
        if not recent_metrics:
            return {"status": "inactive", "service": service_name}
        
        avg_response_time = sum(m.response_time for m in recent_metrics) / len(recent_metrics)
        error_count = sum(1 for m in recent_metrics if m.error_rate > 0)
        error_rate = error_count / len(recent_metrics)
        
        return {
            "status": "active",
            "service": service_name,
            "request_count": len(recent_metrics),
            "avg_response_time": avg_response_time,
            "error_rate": error_rate,
            "last_activity": recent_metrics[-1].timestamp.isoformat()
        }
    
    async def create_grafana_dashboard(self, dashboard_name: str) -> bool:
        """Create Grafana dashboard for AXIOM monitoring"""
        if not self.grafana_client:
            logger.error("Grafana client not configured")
            return False
        
        try:
            dashboard_config = {
                "dashboard": {
                    "title": dashboard_name,
                    "tags": ["axiom", "monitoring"],
                    "timezone": "browser",
                    "panels": [
                        {
                            "title": "System CPU Usage",
                            "type": "graph",
                            "targets": [{"expr": "system_cpu_usage_percent"}]
                        },
                        {
                            "title": "Memory Usage",
                            "type": "graph", 
                            "targets": [{"expr": "system_memory_usage_percent"}]
                        },
                        {
                            "title": "Service Response Times",
                            "type": "graph",
                            "targets": [{"expr": "service_response_time_seconds"}]
                        },
                        {
                            "title": "AXIOM Metrics",
                            "type": "graph",
                            "targets": [
                                {"expr": "axiom_causal_discoveries_total"},
                                {"expr": "axiom_federated_rounds_total"},
                                {"expr": "axiom_synthetic_data_generated_total"}
                            ]
                        }
                    ]
                }
            }
            
            result = self.grafana_client.dashboard.update_dashboard(dashboard_config)
            logger.info(f"Grafana dashboard created: {result}")
            return True
            
        except BiologyError as e:
            logger.error(f"Error creating Grafana dashboard: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        try:
            health_status = {
                "service": "monitoring",
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "monitoring_active": self.is_monitoring,
                "metrics_collected": len(self.system_metrics_history),
                "services_monitored": len(self.service_metrics_history),
                "grafana_connected": self.grafana_client is not None
            }
            
            # Check system health
            if self.system_metrics_history:
                latest = self.system_metrics_history[-1]
                if (latest.cpu_percent > 90 or 
                    latest.memory_percent > 95 or 
                    latest.disk_usage > 95):
                    health_status["status"] = "warning"
                    health_status["warnings"] = ["High resource usage detected"]
            
            return health_status
            
        except BiologyError as e:
            logger.error(f"Health check failed: {e}")
            return {
                "service": "monitoring",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Global monitoring service instance
monitoring_service = MonitoringService()

async def start_monitoring():
    """Start global monitoring service"""
    await monitoring_service.start_monitoring()

async def stop_monitoring():
    """Stop global monitoring service"""
    await monitoring_service.stop_monitoring()

def get_monitoring_service() -> MonitoringService:
    """Get global monitoring service instance"""
    return monitoring_service