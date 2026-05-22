"""
AXIOM Metrics System
Basic metrics collection for monitoring
"""

import time
from typing import Dict, Any, List
from collections import defaultdict
from app.core.bootstrap_logging import logger


class MetricsCollector:
    """Simple metrics collector"""

    def __init__(self):
        self.metrics: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = defaultdict(list)

    def increment_counter(self, name: str, value: int = 1, tags: Dict[str, str] | None = None):
        """Increment a counter metric"""
        self.counters[name] += value
        logger.debug(f"Counter {name} incremented by {value}")

    def set_gauge(self, name: str, value: float):
        """Set a gauge metric"""
        self.gauges[name] = value
        logger.debug(f"Gauge {name} set to {value}")

    def record_histogram(self, name: str, value: float):
        """Record a value in a histogram"""
        self.histograms[name].append(value)
        # Keep only last 1000 values to prevent memory issues
        if len(self.histograms[name]) > 1000:
            self.histograms[name] = self.histograms[name][-1000:]

    def record_tool_adapter_execution(self, adapter_name: str, success: bool, duration_ms: float):
        """Record tool adapter execution metrics"""
        self.increment_counter("tool_adapter_executions_total", tags={"adapter": adapter_name})
        self.increment_counter(f"tool_adapter_{'success' if success else 'failure'}_total", tags={"adapter": adapter_name})
        self.record_histogram("tool_adapter_duration_ms", duration_ms)

    def record_validation_matrix_check(self, score: int, flags: List[str]):
        """Record validation matrix metrics"""
        self.set_gauge("validation_matrix_score", float(score))
        self.increment_counter("validation_matrix_checks_total")
        for flag in flags:
            self.increment_counter(f"validation_matrix_flag_{flag}_total")

    def record_request(self, endpoint: str, method: str, status_code: int, duration: float):
        """Record API request metrics"""
        self.increment_counter("api_requests_total", tags={"endpoint": endpoint, "method": method})
        self.increment_counter(f"api_requests_status_{status_code}")
        self.record_histogram("api_request_duration", duration)

        if status_code >= 400:
            self.increment_counter("api_errors_total", tags={"endpoint": endpoint, "status": str(status_code)})

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        summary = {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histograms": {}
        }

        # Calculate histogram statistics
        for name, values in self.histograms.items():
            if values:
                summary["histograms"][name] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "p95": sorted(values)[int(len(values) * 0.95)] if len(values) > 1 else max(values)
                }

        return summary

    def reset(self):
        """Reset all metrics"""
        self.metrics.clear()
        self.counters.clear()
        self.gauges.clear()
        self.histograms.clear()
        logger.info("Metrics reset")


# Global metrics collector
metrics = MetricsCollector()


# Compatibility function for modules that need 'inc'
def inc(metric_name: str, value: int = 1, tags: Dict[str, str] | None = None):
    """Increment a metric counter - compatibility function"""
    metrics.increment_counter(metric_name, value, tags)


# Compatibility function for modules that need 'observe'
def observe(metric_name: str, value: float, tags: Dict[str, str] | None = None):
    """Observe a metric value - compatibility function"""
    metrics.record_histogram(metric_name, value)
    logger.debug("Observed %s with value %s", metric_name, value)


# Phase timer for research cycle compatibility
class PhaseTimer:
    """Timer for research phases"""
    
    def __init__(self):
        self.start_times = {}
        self.durations = {}
    
    def start_phase(self, phase_name: str):
        """Start timing a phase"""
        self.start_times[phase_name] = time.time()
    
    def end_phase(self, phase_name: str):
        """End timing a phase and record duration"""
        if phase_name in self.start_times:
            duration = time.time() - self.start_times[phase_name]
            self.durations[phase_name] = duration
            metrics.record_histogram(f"research_phase_{phase_name}_duration", duration)
            return duration
        return 0.0
    
    def get_duration(self, phase_name: str) -> float:
        """Get duration of a completed phase"""
        return self.durations.get(phase_name, 0.0)


# Global phase timer
phase_timer = PhaseTimer()


# Phase activity function for research cycle compatibility
def phase_activity(phase_name: str, activity: str = "active") -> Dict[str, Any]:
    """Record phase activity for research cycle monitoring"""
    timestamp = time.time()
    metrics.increment_counter(f"phase_{phase_name}_activity", tags={"activity": activity})
    
    return {
        "phase": phase_name,
        "activity": activity,
        "timestamp": timestamp,
        "duration": phase_timer.get_duration(phase_name)
    }


# Global counters access for compatibility
_COUNTERS = metrics.counters


# Global gauges access for compatibility
_GAUGES = metrics.gauges


# Additional compatibility functions
def gauge_inc(metric_name: str, value: float = 1.0, tags: Dict[str, str] | None = None):
    """Increment a gauge metric - compatibility function"""
    current_value = metrics.gauges.get(metric_name, 0.0)
    metrics.set_gauge(metric_name, current_value + value)
    # Note: tags parameter kept for compatibility but not currently used


def scrape() -> Dict[str, Any]:
    """Scrape metrics for monitoring - compatibility function"""
    return metrics.get_metrics_summary()


class MonitoringSystem:
    """Monitoring system for compatibility"""
    
    def __init__(self):
        self.metrics_collector = metrics
        self.alerts = []
    
    def collect_metrics(self) -> Dict[str, Any]:
        """Collect current metrics"""
        return self.metrics_collector.get_metrics_summary()
    
    def add_alert(self, alert: Dict[str, Any]):
        """Add monitoring alert"""
        self.alerts.append(alert)
    
    def get_health_status(self) -> Dict[str, str]:
        """Get system health status"""
        return {"status": "healthy", "timestamp": str(metrics.gauges.get("last_check", 0))}


# Global monitoring system
monitoring_system = MonitoringSystem()


def timing_decorator(func):
    """Decorator to time function execution and record metrics"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            metrics.record_histogram(f"{func.__name__}_duration", duration)
            return result
        except Exception:
            duration = time.time() - start_time
            metrics.record_histogram(f"{func.__name__}_duration", duration)
            metrics.increment_counter(f"{func.__name__}_errors")
            raise

    return wrapper
