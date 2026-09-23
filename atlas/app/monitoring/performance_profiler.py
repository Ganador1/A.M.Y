#!/usr/bin/env python3
"""
AXIOM Performance Profiler
Advanced profiling system for scientific computations
"""

import time
import psutil
import threading
from typing import Dict, Any, Optional
from functools import wraps
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class PerformanceProfiler:
    """Advanced performance profiling system"""

    def __init__(self):
        self.metrics = {}
        self.active_profilers = {}
        self.lock = threading.Lock()

    @contextmanager
    def profile_operation(self, operation_name: str, metadata: Optional[Dict[str, Any]] = None):
        """Context manager for profiling operations"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        start_cpu = psutil.cpu_percent(interval=None)

        profiler_id = f"{operation_name}_{threading.current_thread().ident}_{start_time}"

        with self.lock:
            self.active_profilers[profiler_id] = {
                "operation": operation_name,
                "start_time": start_time,
                "start_memory": start_memory,
                "start_cpu": start_cpu,
                "metadata": metadata or {}
            }

        try:
            yield profiler_id
        finally:
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            end_cpu = psutil.cpu_percent(interval=None)

            duration = end_time - start_time
            memory_delta = end_memory - start_memory
            cpu_usage = end_cpu - start_cpu

            with self.lock:
                if profiler_id in self.active_profilers:
                    profiler_data = self.active_profilers[profiler_id]
                    profiler_data.update({
                        "end_time": end_time,
                        "end_memory": end_memory,
                        "end_cpu": end_cpu,
                        "duration": duration,
                        "memory_delta": memory_delta,
                        "cpu_usage": cpu_usage,
                        "completed": True
                    })

                    # Store in metrics
                    if operation_name not in self.metrics:
                        self.metrics[operation_name] = []
                    self.metrics[operation_name].append(profiler_data)

                    del self.active_profilers[profiler_id]

    def profile_function(self, operation_name: Optional[str] = None):
        """Decorator for profiling functions"""
        def decorator(func):
            name = operation_name or f"{func.__module__}.{func.__name__}"

            @wraps(func)
            def wrapper(*args, **kwargs):
                metadata = {
                    "function": func.__name__,
                    "module": func.__module__,
                    "args_count": len(args),
                    "kwargs_count": len(kwargs)
                }

                with self.profile_operation(name, metadata):
                    return func(*args, **kwargs)

            return wrapper
        return decorator

    def get_operation_stats(self, operation_name: str) -> Dict[str, Any]:
        """Get statistics for a specific operation"""
        if operation_name not in self.metrics:
            return {"error": f"No data for operation: {operation_name}"}

        operations = self.metrics[operation_name]
        if not operations:
            return {"error": "No completed operations"}

        durations = [op["duration"] for op in operations]
        memory_deltas = [op["memory_delta"] for op in operations]
        cpu_usages = [op["cpu_usage"] for op in operations]

        return {
            "operation": operation_name,
            "total_calls": len(operations),
            "avg_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "p95_duration": sorted(durations)[int(len(durations) * 0.95)],
            "avg_memory_delta": sum(memory_deltas) / len(memory_deltas),
            "max_memory_delta": max(memory_deltas),
            "avg_cpu_usage": sum(cpu_usages) / len(cpu_usages),
            "recent_calls": operations[-5:]  # Last 5 calls
        }

    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all operations"""
        stats = {}
        for operation in self.metrics:
            stats[operation] = self.get_operation_stats(operation)
        return stats

    def get_performance_report(self) -> str:
        """Generate a comprehensive performance report"""
        report = []
        report.append("🚀 AXIOM Performance Report")
        report.append("=" * 50)
        report.append("")

        total_operations = sum(len(ops) for ops in self.metrics.values())
        report.append(f"📊 Total Operations Profiled: {total_operations}")
        report.append("")

        for operation, stats in self.get_all_stats().items():
            if "error" in stats:
                continue

            report.append(f"🔬 {operation}")
            report.append("-" * 40)
            report.append(f"  Calls: {stats['total_calls']}")
            report.append(".2f")
            report.append(".2f")
            report.append(".2f")
            report.append(".2f")
            report.append(".2f")
            report.append("")

        # Performance recommendations
        report.append("💡 Performance Recommendations")
        report.append("-" * 30)

        for operation, stats in self.get_all_stats().items():
            if "error" in stats:
                continue

            if stats['avg_duration'] > 1.0:  # More than 1 second
                report.append(f"⚠️  {operation}: Consider optimization (avg: {stats['avg_duration']:.2f}s)")

            if stats['max_memory_delta'] > 100:  # More than 100MB
                report.append(f"🧠 {operation}: High memory usage (max: {stats['max_memory_delta']:.1f}MB)")

        return "\n".join(report)

    def clear_metrics(self):
        """Clear all profiling metrics"""
        with self.lock:
            self.metrics.clear()
            self.active_profilers.clear()

# Global profiler instance
profiler = PerformanceProfiler()
performance_profiler = profiler  # Alias for compatibility

# Convenience functions
def profile_function(name: Optional[str] = None):
    """Convenience function for profiling functions"""
    return profiler.profile_function(name)

def get_performance_report():
    """Get performance report"""
    return profiler.get_performance_report()
