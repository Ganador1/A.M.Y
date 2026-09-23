#!/usr/bin/env python3
"""
Event Loop Health Check Script for AXIOM ATLAS.

This script checks the health of the event loop by measuring
lag, responsiveness, and detecting blocking operations.
"""

import asyncio
import time
import statistics
from typing import List, Dict, Any
import json
from pathlib import Path
from datetime import datetime


class EventLoopHealthChecker:
    """Check event loop health and responsiveness."""
    
    def __init__(self):
        self.lag_measurements = []
        self.responsiveness_measurements = []
        self.blocking_detected = False
        
    async def measure_event_loop_lag(self, iterations: int = 100) -> List[float]:
        """Measure event loop lag over multiple iterations."""
        print(f"🔄 Measuring event loop lag ({iterations} iterations)...")
        
        lag_measurements = []
        
        for i in range(iterations):
            # Measure lag by timing a small sleep
            start_time = time.perf_counter()
            await asyncio.sleep(0.01)  # 10ms delay
            actual_delay = time.perf_counter() - start_time
            
            # Calculate lag (difference from expected delay)
            lag_ms = (actual_delay - 0.01) * 1000
            lag_measurements.append(max(0, lag_ms))
        
        self.lag_measurements = lag_measurements
        return lag_measurements
    
    async def measure_responsiveness(self, iterations: int = 50) -> List[float]:
        """Measure event loop responsiveness."""
        print(f"⚡ Measuring event loop responsiveness ({iterations} iterations)...")
        
        responsiveness_measurements = []
        
        for i in range(iterations):
            # Measure time to schedule and execute a task
            start_time = time.perf_counter()
            
            # Create and await a simple task
            async def simple_task():
                return "completed"
            
            await asyncio.create_task(simple_task())
            
            responsiveness_time = time.perf_counter() - start_time
            responsiveness_measurements.append(responsiveness_time * 1000)  # Convert to ms
        
        self.responsiveness_measurements = responsiveness_measurements
        return responsiveness_measurements
    
    async def test_concurrent_operations(self, concurrent_tasks: int = 20) -> Dict[str, Any]:
        """Test concurrent operations to check for blocking."""
        print(f"🔄 Testing concurrent operations ({concurrent_tasks} tasks)...")
        
        async def test_task(task_id: int) -> str:
            """Simple test task."""
            await asyncio.sleep(0.001)  # 1ms
            return f"Task {task_id} completed"
        
        # Measure time for concurrent execution
        start_time = time.perf_counter()
        
        # Create and execute tasks concurrently
        tasks = [test_task(i) for i in range(concurrent_tasks)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.perf_counter() - start_time
        
        # Check for exceptions
        successful_results = [r for r in results if not isinstance(r, Exception)]
        failed_results = [r for r in results if isinstance(r, Exception)]
        
        return {
            "total_time": total_time,
            "successful_tasks": len(successful_results),
            "failed_tasks": len(failed_results),
            "throughput": len(successful_results) / total_time,
            "avg_time_per_task": total_time / concurrent_tasks,
        }
    
    async def test_blocking_detection(self) -> Dict[str, Any]:
        """Test for blocking operations."""
        print("🚫 Testing for blocking operations...")
        
        # Test 1: Measure time for a small async operation
        start_time = time.perf_counter()
        await asyncio.sleep(0.001)  # 1ms
        async_time = time.perf_counter() - start_time
        
        # Test 2: Simulate a blocking operation (should be avoided)
        start_time = time.perf_counter()
        time.sleep(0.001)  # 1ms blocking sleep
        blocking_time = time.perf_counter() - start_time
        
        # Calculate blocking overhead
        blocking_overhead = blocking_time - async_time
        
        return {
            "async_time_ms": async_time * 1000,
            "blocking_time_ms": blocking_time * 1000,
            "blocking_overhead_ms": blocking_overhead * 1000,
            "blocking_detected": blocking_overhead > 0.001,  # 1ms threshold
        }
    
    def calculate_health_metrics(self) -> Dict[str, Any]:
        """Calculate overall health metrics."""
        if not self.lag_measurements:
            return {"error": "No lag measurements available"}
        
        lag_stats = {
            "min_ms": min(self.lag_measurements),
            "max_ms": max(self.lag_measurements),
            "mean_ms": statistics.mean(self.lag_measurements),
            "median_ms": statistics.median(self.lag_measurements),
            "p95_ms": sorted(self.lag_measurements)[int(len(self.lag_measurements) * 0.95)],
            "p99_ms": sorted(self.lag_measurements)[int(len(self.lag_measurements) * 0.99)],
        }
        
        responsiveness_stats = {}
        if self.responsiveness_measurements:
            responsiveness_stats = {
                "min_ms": min(self.responsiveness_measurements),
                "max_ms": max(self.responsiveness_measurements),
                "mean_ms": statistics.mean(self.responsiveness_measurements),
                "median_ms": statistics.median(self.responsiveness_measurements),
            }
        
        # Health assessment
        health_status = "healthy"
        issues = []
        
        if lag_stats["max_ms"] > 50:  # 50ms threshold
            health_status = "warning"
            issues.append(f"High max lag: {lag_stats['max_ms']:.1f}ms")
        
        if lag_stats["p95_ms"] > 20:  # 20ms threshold
            health_status = "warning"
            issues.append(f"High P95 lag: {lag_stats['p95_ms']:.1f}ms")
        
        if lag_stats["mean_ms"] > 10:  # 10ms threshold
            health_status = "critical"
            issues.append(f"High mean lag: {lag_stats['mean_ms']:.1f}ms")
        
        return {
            "health_status": health_status,
            "issues": issues,
            "lag_stats": lag_stats,
            "responsiveness_stats": responsiveness_stats,
            "measurements_count": len(self.lag_measurements),
        }
    
    async def run_comprehensive_check(self) -> Dict[str, Any]:
        """Run comprehensive event loop health check."""
        print("🚀 Starting Event Loop Health Check...")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all checks
        lag_measurements = await self.measure_event_loop_lag(100)
        responsiveness_measurements = await self.measure_responsiveness(50)
        concurrent_results = await self.test_concurrent_operations(20)
        blocking_results = await self.test_blocking_detection()
        
        total_time = time.time() - start_time
        
        # Calculate health metrics
        health_metrics = self.calculate_health_metrics()
        
        # Compile results
        results = {
            "check_info": {
                "timestamp": datetime.now().isoformat(),
                "total_duration": total_time,
                "iterations": {
                    "lag_measurements": len(lag_measurements),
                    "responsiveness_measurements": len(responsiveness_measurements),
                }
            },
            "health_metrics": health_metrics,
            "concurrent_test": concurrent_results,
            "blocking_test": blocking_results,
            "raw_measurements": {
                "lag_measurements": lag_measurements,
                "responsiveness_measurements": responsiveness_measurements,
            }
        }
        
        return results
    
    def print_results(self, results: Dict[str, Any]):
        """Print health check results."""
        print("\n" + "=" * 60)
        print("📊 EVENT LOOP HEALTH CHECK RESULTS")
        print("=" * 60)
        
        # Health status
        health_metrics = results["health_metrics"]
        print(f"🏥 Health Status: {health_metrics['health_status'].upper()}")
        
        if health_metrics.get("issues"):
            print(f"⚠️  Issues:")
            for issue in health_metrics["issues"]:
                print(f"  - {issue}")
        else:
            print("✅ No issues detected")
        
        # Lag statistics
        lag_stats = health_metrics["lag_stats"]
        print(f"\n🔄 Event Loop Lag Statistics:")
        print(f"  Mean: {lag_stats['mean_ms']:.2f}ms")
        print(f"  Median: {lag_stats['median_ms']:.2f}ms")
        print(f"  P95: {lag_stats['p95_ms']:.2f}ms")
        print(f"  P99: {lag_stats['p99_ms']:.2f}ms")
        print(f"  Max: {lag_stats['max_ms']:.2f}ms")
        
        # Responsiveness statistics
        if health_metrics.get("responsiveness_stats"):
            resp_stats = health_metrics["responsiveness_stats"]
            print(f"\n⚡ Responsiveness Statistics:")
            print(f"  Mean: {resp_stats['mean_ms']:.2f}ms")
            print(f"  Median: {resp_stats['median_ms']:.2f}ms")
            print(f"  Max: {resp_stats['max_ms']:.2f}ms")
        
        # Concurrent test results
        concurrent_test = results["concurrent_test"]
        print(f"\n🔄 Concurrent Operations Test:")
        print(f"  Total Time: {concurrent_test['total_time']:.3f}s")
        print(f"  Successful Tasks: {concurrent_test['successful_tasks']}")
        print(f"  Failed Tasks: {concurrent_test['failed_tasks']}")
        print(f"  Throughput: {concurrent_test['throughput']:.1f} tasks/s")
        print(f"  Avg Time per Task: {concurrent_test['avg_time_per_task']:.3f}s")
        
        # Blocking test results
        blocking_test = results["blocking_test"]
        print(f"\n🚫 Blocking Detection Test:")
        print(f"  Async Time: {blocking_test['async_time_ms']:.2f}ms")
        print(f"  Blocking Time: {blocking_test['blocking_time_ms']:.2f}ms")
        print(f"  Blocking Overhead: {blocking_test['blocking_overhead_ms']:.2f}ms")
        print(f"  Blocking Detected: {'Yes' if blocking_test['blocking_detected'] else 'No'}")
        
        # Overall assessment
        print(f"\n📈 Overall Assessment:")
        if health_metrics["health_status"] == "healthy":
            print("✅ Event loop is healthy and responsive")
        elif health_metrics["health_status"] == "warning":
            print("⚠️  Event loop shows some performance issues")
        else:
            print("❌ Event loop has significant performance issues")


async def main():
    """Main entry point for event loop health check."""
    checker = EventLoopHealthChecker()
    
    try:
        results = await checker.run_comprehensive_check()
        checker.print_results(results)
        
        # Save results
        output_file = Path("reports/event_loop_health.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Results saved to: {output_file}")
        
        # Return exit code based on health status
        health_status = results["health_metrics"]["health_status"]
        if health_status == "healthy":
            return 0
        elif health_status == "warning":
            return 1
        else:
            return 2
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        import traceback
        traceback.print_exc()
        return 3


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
