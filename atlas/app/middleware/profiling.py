"""
Async Profiling Middleware for AXIOM ATLAS.

This module provides middleware to monitor and profile async operations,
detect event loop blocking, and track performance metrics.
"""

import asyncio
import time
import logging
import threading
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
from pathlib import Path
import psutil
import os
import aiofiles
import httpx

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class AsyncProfilingMiddleware(BaseHTTPMiddleware):
    """Middleware for profiling async operations and detecting event loop blocking."""
    
    def __init__(self, app, slow_request_threshold: float = 0.5, max_events: int = 1000):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold
        self.max_events = max_events
        
        # Performance tracking
        self.request_times = deque(maxlen=max_events)
        self.slow_requests = deque(maxlen=100)
        self.event_loop_lag = deque(maxlen=100)
        self.blocking_operations = deque(maxlen=100)
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "slow_requests": 0,
            "blocking_operations": 0,
            "avg_response_time": 0.0,
            "max_response_time": 0.0,
            "min_response_time": float('inf'),
        }
        
        # Thread-safe lock
        self._lock = threading.Lock()
        
        # Start background monitoring
        self._monitoring_task = None
        self._start_monitoring()
    
    def _start_monitoring(self):
        """Start background monitoring of event loop health."""
        async def monitor_event_loop():
            """Background task to monitor event loop health."""
            while True:
                try:
                    # Measure event loop lag
                    start_time = time.perf_counter()
                    await asyncio.sleep(0.1)  # Small delay
                    actual_delay = time.perf_counter() - start_time
                    lag = actual_delay - 0.1
                    
                    with self._lock:
                        self.event_loop_lag.append({
                            "timestamp": datetime.now(),
                            "lag_ms": lag * 1000,
                        })
                    
                    # Check for excessive lag
                    if lag > 0.05:  # 50ms lag threshold
                        logger.warning(f"Event loop lag detected: {lag*1000:.1f}ms")
                        
                        with self._lock:
                            self.blocking_operations.append({
                                "timestamp": datetime.now(),
                                "type": "event_loop_lag",
                                "lag_ms": lag * 1000,
                                "details": "Event loop blocked for extended period"
                            })
                    
                    # Monitor system resources
                    process = psutil.Process(os.getpid())
                    cpu_percent = process.cpu_percent()
                    memory_mb = process.memory_info().rss / 1024 / 1024
                    
                    if cpu_percent > 80:  # High CPU usage
                        logger.warning(f"High CPU usage: {cpu_percent:.1f}%")
                    
                    if memory_mb > 1000:  # High memory usage
                        logger.warning(f"High memory usage: {memory_mb:.1f}MB")
                    
                except Exception as e:
                    logger.error(f"Error in event loop monitoring: {e}")
                
                await asyncio.sleep(1)  # Check every second
        
        # Start monitoring task
        try:
            loop = asyncio.get_event_loop()
            self._monitoring_task = loop.create_task(monitor_event_loop())
        except Exception as e:
            logger.error(f"Failed to start event loop monitoring: {e}")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect profiling data."""
        start_time = time.perf_counter()
        
        # Get request info
        method = request.method
        url = str(request.url)
        path = request.url.path
        
        # Track if event loop is blocked
        loop = asyncio.get_event_loop()
        loop.set_debug(True)  # Enable slow callback warnings
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            duration = time.perf_counter() - start_time
            
            # Update statistics
            with self._lock:
                self.request_times.append(duration)
                self.stats["total_requests"] += 1
                self.stats["max_response_time"] = max(self.stats["max_response_time"], duration)
                self.stats["min_response_time"] = min(self.stats["min_response_time"], duration)
                
                # Calculate average
                if self.request_times:
                    self.stats["avg_response_time"] = sum(self.request_times) / len(self.request_times)
                
                # Check for slow requests
                if duration > self.slow_request_threshold:
                    self.stats["slow_requests"] += 1
                    self.slow_requests.append({
                        "timestamp": datetime.now(),
                        "method": method,
                        "path": path,
                        "duration": duration,
                        "status_code": response.status_code,
                    })
                    
                    logger.warning(
                        f"Slow request: {method} {path} took {duration:.3f}s "
                        f"(threshold: {self.slow_request_threshold}s)"
                    )
            
            # Add profiling headers
            response.headers["X-Process-Time"] = str(duration)
            response.headers["X-Event-Loop-Healthy"] = "true" if duration < 0.1 else "false"
            
            return response
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            
            # Log error with profiling info
            logger.error(
                f"Request error: {method} {path} failed after {duration:.3f}s: {e}"
            )
            
            # Track as blocking operation
            with self._lock:
                self.blocking_operations.append({
                    "timestamp": datetime.now(),
                    "type": "request_error",
                    "duration": duration,
                    "error": str(e),
                    "path": path,
                })
            
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current profiling statistics."""
        with self._lock:
            # Calculate recent event loop lag
            recent_lag = []
            if self.event_loop_lag:
                recent_events = list(self.event_loop_lag)[-10:]  # Last 10 events
                recent_lag = [event["lag_ms"] for event in recent_events]
            
            # Calculate recent blocking operations
            recent_blocking = []
            if self.blocking_operations:
                recent_blocking = list(self.blocking_operations)[-10:]  # Last 10 events
            
            return {
                "timestamp": datetime.now().isoformat(),
                "stats": self.stats.copy(),
                "recent_event_loop_lag_ms": recent_lag,
                "recent_blocking_operations": recent_blocking,
                "slow_requests_count": len(self.slow_requests),
                "event_loop_lag_count": len(self.event_loop_lag),
                "blocking_operations_count": len(self.blocking_operations),
            }
    
    def get_slow_requests(self, limit: int = 10) -> list:
        """Get recent slow requests."""
        with self._lock:
            return list(self.slow_requests)[-limit:]
    
    def get_blocking_operations(self, limit: int = 10) -> list:
        """Get recent blocking operations."""
        with self._lock:
            return list(self.blocking_operations)[-limit:]
    
    def export_metrics(self, output_file: Optional[str] = None) -> str:
        """Export profiling metrics to JSON file."""
        if output_file is None:
            output_file = f"profiling_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        metrics = {
            "export_timestamp": datetime.now().isoformat(),
            "stats": self.get_stats(),
            "slow_requests": self.get_slow_requests(50),
            "blocking_operations": self.get_blocking_operations(50),
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "memory_gb": psutil.virtual_memory().total / (1024**3),
                "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
            }
        }
        
        with aiofiles.open(output_path, 'w') as f:
            json.dump(metrics, f, indent=2, default=str)
        
        logger.info(f"Profiling metrics exported to: {output_path}")
        return str(output_path)
    
    def reset_stats(self):
        """Reset profiling statistics."""
        with self._lock:
            self.request_times.clear()
            self.slow_requests.clear()
            self.event_loop_lag.clear()
            self.blocking_operations.clear()
            
            self.stats = {
                "total_requests": 0,
                "slow_requests": 0,
                "blocking_operations": 0,
                "avg_response_time": 0.0,
                "max_response_time": 0.0,
                "min_response_time": float('inf'),
            }
        
        logger.info("Profiling statistics reset")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass


class AsyncProfiler:
    """Standalone async profiler for specific operations."""
    
    def __init__(self, name: str = "operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.duration = None
        self.blocking_detected = False
    
    def __enter__(self):
        """Context manager entry."""
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.end_time = time.perf_counter()
        self.duration = self.end_time - self.start_time
        
        # Check for blocking (synchronous operations taking too long)
        if self.duration > 0.1:  # 100ms threshold
            self.blocking_detected = True
            logger.warning(
                f"Blocking operation detected: {self.name} took {self.duration:.3f}s"
            )
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.start_time = time.perf_counter()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self.end_time = time.perf_counter()
        self.duration = self.end_time - self.start_time
        
        # Check for blocking
        if self.duration > 0.1:  # 100ms threshold
            self.blocking_detected = True
            logger.warning(
                f"Blocking operation detected: {self.name} took {self.duration:.3f}s"
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get profiling metrics."""
        return {
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "blocking_detected": self.blocking_detected,
        }


# Utility functions for profiling
def profile_async_function(func_name: str = None):
    """Decorator to profile async functions."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            name = func_name or f"{func.__module__}.{func.__name__}"
            async with AsyncProfiler(name) as profiler:
                result = await func(*args, **kwargs)
                return result
        return wrapper
    return decorator


def profile_sync_function(func_name: str = None):
    """Decorator to profile sync functions."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            name = func_name or f"{func.__module__}.{func.__name__}"
            with AsyncProfiler(name) as profiler:
                result = func(*args, **kwargs)
                return result
        return wrapper
    return decorator


# Example usage
if __name__ == "__main__":
    # Test the profiler
    async def test_async_operation():
        """Test async operation."""
        async with AsyncProfiler("test_operation") as profiler:
            await asyncio.sleep(0.05)  # 50ms operation
            return "completed"
    
    async def main():
        """Test main function."""
        result = await test_async_operation()
        print(f"Result: {result}")
    
    # Run test
    asyncio.run(main())
