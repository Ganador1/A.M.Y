"""
ROADMAP 5 - Phase 3.3: Simple Performance Benchmarking
Quick benchmarks for key async migration optimizations.

Usage:
    python benchmarks/simple_benchmark.py
"""

import asyncio
import time
import statistics
from typing import Dict, Any
import json
from datetime import datetime
from pathlib import Path

# Import only services that work well standalone
from app.services.structural_database_service import StructuralDatabaseService
from app.autonomous.interfaces.external_apis import (
    fetch_literature_snippets,
    fetch_material_candidates,
)


async def measure_latency(func, *args, iterations: int = 5, **kwargs) -> Dict[str, float]:
    """Measure latency statistics for a function."""
    latencies = []
    
    for _ in range(iterations):
        start = time.perf_counter()
        try:
            await func(*args, **kwargs)
        except Exception as e:
            print(f"  Warning: {func.__name__} failed: {str(e)[:50]}")
        end = time.perf_counter()
        latencies.append((end - start) * 1000)  # Convert to ms
    
    if not latencies:
        return {"error": "All iterations failed"}
    
    latencies.sort()
    return {
        "min_ms": min(latencies),
        "max_ms": max(latencies),
        "mean_ms": statistics.mean(latencies),
        "median_ms": statistics.median(latencies),
        "p95_ms": latencies[int(len(latencies) * 0.95)] if len(latencies) > 1 else latencies[0],
        "p99_ms": latencies[int(len(latencies) * 0.99)] if len(latencies) > 1 else latencies[0],
        "stdev_ms": statistics.stdev(latencies) if len(latencies) > 1 else 0.0,
        "iterations": len(latencies)
    }


async def measure_concurrent(func, *args, concurrency: int = 10, **kwargs) -> Dict[str, Any]:
    """Measure performance under concurrent load."""
    tasks = [func(*args, **kwargs) for _ in range(concurrency)]
    
    start = time.perf_counter()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    elapsed = (time.perf_counter() - start) * 1000
    
    successes = sum(1 for r in results if not isinstance(r, Exception))
    failures = concurrency - successes
    
    return {
        "concurrency": concurrency,
        "total_time_ms": elapsed,
        "successes": successes,
        "failures": failures,
        "throughput_per_second": (concurrency / (elapsed / 1000)),
        "success_rate": successes / concurrency
    }


async def benchmark_structural_database():
    """Benchmark structural database service."""
    print("\n🔬 Benchmarking Structural Database Service...")
    
    service = StructuralDatabaseService()
    results = {}
    
    # 1. PDB fetch latency
    print("  - PDB fetch latency...")
    results["pdb_fetch_latency"] = await measure_latency(
        service.fetch_pdb, "1CRN", iterations=5
    )
    
    # 2. UniProt fetch latency  
    print("  - UniProt fetch latency...")
    results["uniprot_fetch_latency"] = await measure_latency(
        service.fetch_uniprot, "P69905", iterations=5
    )
    
    # 3. Batch operations
    print("  - PDB batch operations...")
    pdb_ids = ["1CRN", "2HHB", "3NIR"]
    results["pdb_batch_latency"] = await measure_latency(
        service.fetch_pdb_batch, pdb_ids, iterations=3
    )
    
    # 4. Concurrent requests
    print("  - Concurrent PDB fetches (10)...")
    results["pdb_concurrent_10"] = await measure_concurrent(
        service.fetch_pdb, "1CRN", concurrency=10
    )
    
    print("  ✅ Structural Database benchmarks complete")
    return results


async def benchmark_external_apis():
    """Benchmark external APIs."""
    print("\n🌐 Benchmarking External APIs...")
    
    results = {}
    
    # 1. Literature fetch
    print("  - Literature fetch latency...")
    results["literature_fetch_latency"] = await measure_latency(
        fetch_literature_snippets, "quantum computing", iterations=3
    )
    
    # 2. Materials fetch
    print("  - Materials fetch latency...")
    results["materials_fetch_latency"] = await measure_latency(
        fetch_material_candidates, "LiFePO4", iterations=3
    )
    
    # 3. Concurrent literature fetches
    print("  - Concurrent literature fetches (5)...")
    results["literature_concurrent_5"] = await measure_concurrent(
        fetch_literature_snippets, "AI", concurrency=5
    )
    
    print("  ✅ External APIs benchmarks complete")
    return results


async def benchmark_batch_vs_sequential():
    """Compare batch vs sequential operations."""
    print("\n⚡ Comparing Batch vs Sequential...")
    
    service = StructuralDatabaseService()
    results = {}
    
    pdb_ids = ["1CRN", "2HHB", "3NIR"]
    
    # Sequential
    print("  - Sequential PDB fetches...")
    async def sequential_pdb():
        for pdb_id in pdb_ids:
            await service.fetch_pdb(pdb_id)
    
    seq_latency = await measure_latency(sequential_pdb, iterations=3)
    
    # Batch
    print("  - Batch PDB fetches...")
    batch_latency = await measure_latency(
        service.fetch_pdb_batch, pdb_ids, iterations=3
    )
    
    speedup = seq_latency.get("mean_ms", 0) / batch_latency.get("mean_ms", 1)
    
    results["comparison"] = {
        "sequential_mean_ms": seq_latency.get("mean_ms"),
        "batch_mean_ms": batch_latency.get("mean_ms"),
        "speedup": round(speedup, 2)
    }
    
    print(f"  📊 Speedup: {speedup:.2f}x faster with batch operations")
    print("  ✅ Batch comparison complete")
    
    return results


async def run_all_benchmarks():
    """Run all benchmarks."""
    print("=" * 80)
    print("🚀 ROADMAP 5 - PHASE 3.3: PERFORMANCE BENCHMARKING")
    print("=" * 80)
    
    start_time = time.perf_counter()
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "benchmarks": {}
    }
    
    # Run benchmarks
    results["benchmarks"]["structural_database"] = await benchmark_structural_database()
    results["benchmarks"]["external_apis"] = await benchmark_external_apis()
    results["benchmarks"]["batch_vs_sequential"] = await benchmark_batch_vs_sequential()
    
    elapsed = time.perf_counter() - start_time
    results["total_benchmark_time_seconds"] = elapsed
    
    print("\n" + "=" * 80)
    print(f"✅ All benchmarks complete in {elapsed:.2f} seconds")
    print("=" * 80)
    
    return results


def save_results(results: Dict[str, Any], filename: str = "benchmark_results.json"):
    """Save results to file."""
    output_dir = Path("benchmarks/results")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"benchmark_{timestamp}.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 Results saved to: {output_path}")
    return output_path


def print_summary(results: Dict[str, Any]):
    """Print human-readable summary."""
    print("\n" + "=" * 80)
    print("📊 BENCHMARK SUMMARY")
    print("=" * 80)
    
    # Structural Database
    if "structural_database" in results["benchmarks"]:
        struct = results["benchmarks"]["structural_database"]
        print("\n🔬 Structural Database:")
        if "pdb_fetch_latency" in struct:
            pdb = struct["pdb_fetch_latency"]
            print(f"  PDB Fetch: {pdb.get('mean_ms', 0):.2f}ms (P95: {pdb.get('p95_ms', 0):.2f}ms)")
        if "pdb_batch_latency" in struct:
            batch = struct["pdb_batch_latency"]
            print(f"  PDB Batch (3): {batch.get('mean_ms', 0):.2f}ms")
        if "pdb_concurrent_10" in struct:
            conc = struct["pdb_concurrent_10"]
            print(f"  Concurrent (10): {conc.get('throughput_per_second', 0):.2f} req/s")
    
    # External APIs
    if "external_apis" in results["benchmarks"]:
        apis = results["benchmarks"]["external_apis"]
        print("\n🌐 External APIs:")
        if "literature_fetch_latency" in apis:
            lit = apis["literature_fetch_latency"]
            print(f"  Literature: {lit.get('mean_ms', 0):.2f}ms")
        if "materials_fetch_latency" in apis:
            mat = apis["materials_fetch_latency"]
            print(f"  Materials: {mat.get('mean_ms', 0):.2f}ms")
    
    # Batch Comparison
    if "batch_vs_sequential" in results["benchmarks"]:
        comp = results["benchmarks"]["batch_vs_sequential"]["comparison"]
        print("\n⚡ Batch vs Sequential:")
        print(f"  Sequential: {comp.get('sequential_mean_ms', 0):.2f}ms")
        print(f"  Batch:      {comp.get('batch_mean_ms', 0):.2f}ms")
        print(f"  Speedup:    {comp.get('speedup', 0):.2f}x faster")
    
    print("\n" + "=" * 80)


async def main():
    """Main entry point."""
    try:
        # Run benchmarks
        results = await run_all_benchmarks()
        
        # Save results
        save_results(results)
        
        # Print summary
        print_summary(results)
        
        print("\n✅ Benchmarking complete!")
        
    except Exception as e:
        print(f"\n❌ Benchmarking failed: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(main())
